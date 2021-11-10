import psycopg2
import hashlib
import pandas as pd
from numpy import nan
from time import sleep
from random import randrange
from collections import deque

import extensions.load_api_key
from extensions.connect_db import DBConnection
from helpers import log, email_admin, cr_api_request


SLEEP_TIME = 0.05


def psql_insert(con, table: str, insert_tuple: tuple, integrity_error_action: str = 'rollback',
                primary_key: str = None, primary_key_value: str = None) -> None:
    """
    A helper function that does exactly what INSERT INTO does
    (when inserting into all columns).
    :param con: A psycopg2 connection object;
    :param table: Name of the table;
    :param insert_tuple: Values to insert - usually a single tuple,
    but if bulk=True, a tuple of tuples;
    :param integrity_error_action: 'rollback' (default) or 'update' (given a primary key);
    this is useful for PlayerInfo insertions;
    :param primary_key: Required only if integrity_error_action = 'update';
    :param primary_key_value: The actual value of primary key (assumes it's a string)
    """
    log('Entered psql_insert()')

    # detect if this is a bulk insertion
    bulk = type(insert_tuple[0]) is tuple
    num_attr = len(insert_tuple) if not bulk else len(insert_tuple[0])

    # build up something like this: '(%s, %s, %s)'
    insert_tuple_format = '(' + ('%s, ' * num_attr)[:-2] + ')'

    with con.cursor() as cur:
        insert_cmd = 'INSERT INTO {} VALUES {};'.format(
            table, insert_tuple_format)

        try:
            # execute insertion
            if not bulk:
                cur.execute(insert_cmd, insert_tuple)
            else:
                cur.executemany(insert_cmd, insert_tuple)
        except psycopg2.IntegrityError:
            if integrity_error_action == 'rollback':
                # by default, if primary/foreign key constraint violation, roll back, do not email
                con.rollback()
            elif integrity_error_action == 'update':
                # perform an update instead - use primary key specified
                # shortcut: delete row with primary key, then re-insert
                delete_cmd = "DELETE FROM {} WHERE {} = '{}'".format(
                    table, primary_key, primary_key_value)
                cur.execute(delete_cmd)
                psql_insert(con, table, insert_tuple,
                            integrity_error_action, primary_key, primary_key_value)
        except psycopg2.Error as e:
            # email admin on all other errors
            email_admin(400, 'ERROR: Insertion: {}.'.format(str(e).strip()))
        else:
            # commit if successful
            con.commit()


def insert_player_info(con, player_tag: str) -> None:
    """
    Inserts into table PlayerInfo given a player_tag. Requires API call.
    :param con: A psycopg2 connection object;
    :param player_tag: A string.
    """
    log('Entered insert_player_info(), player_tag = {}'.format(player_tag))

    player_info_res = cr_api_request(player_tag, 'player_info')
    # sleep(SLEEP_TIME)

    if player_info_res.get('statusCode') == 200 and len(player_info_res.get('body')) > 0:
        player_info = player_info_res.get('body')  # a dictionary

        # build insertion tuple by extracting every attribute for table PlayerInfo
        playerTag = player_info.get('tag')
        name = player_info.get('name')

        clan = player_info.get('clan')
        try:
            clanTag = clan.get('tag')
        except AttributeError:
            clanTag = None

        role = player_info.get('role')

        arena = player_info.get('arena')
        try:
            arenaId = arena.get('id')
            arenaName = arena.get('name')
        except AttributeError:
            arenaId = None
            arenaName = None

        trophies = player_info.get('trophies')
        bestTrophies = player_info.get('bestTrophies')
        donations = player_info.get('donations')
        donationsReceived = player_info.get('donationsReceived')
        totalDonations = player_info.get('totalDonations')

        leagueStatistics = player_info.get('leagueStatistics')
        if leagueStatistics is not None:
            previousSeason = leagueStatistics.get('previousSeason')
            try:
                previousSeasonTrophies = previousSeason.get('trophies')
                previousSeasonRank = previousSeason.get('rank')
                previousSeasonBestTrophies = previousSeason.get('bestTrophies')
                previousSeasonId = previousSeason.get('id')
            except AttributeError:
                previousSeasonTrophies = None
                previousSeasonRank = None
                previousSeasonBestTrophies = None
                previousSeasonId = None

            currentSeason = leagueStatistics.get('currentSeason')
            try:
                currentSeasonTrophies = currentSeason.get('trophies')
                currentSeasonRank = currentSeason.get('rank')
                currentSeasonBestTrophies = currentSeason.get('bestTrophies')
                currentSeasonId = currentSeason.get('id')
            except AttributeError:
                currentSeasonTrophies = None
                currentSeasonRank = None
                currentSeasonBestTrophies = None
                currentSeasonId = None

            bestSeason = leagueStatistics.get('bestSeason')
            try:
                bestSeasonTrophies = bestSeason.get('trophies')
                bestSeasonRank = bestSeason.get('rank')
                bestSeasonBestTrophies = bestSeason.get('bestTrophies')
                bestSeasonId = bestSeason.get('id')
            except AttributeError:
                bestSeasonTrophies = None
                bestSeasonRank = None
                bestSeasonBestTrophies = None
                bestSeasonId = None
        else:
            previousSeasonTrophies = None
            previousSeasonRank = None
            previousSeasonBestTrophies = None
            previousSeasonId = None
            currentSeasonTrophies = None
            currentSeasonRank = None
            currentSeasonBestTrophies = None
            currentSeasonId = None
            bestSeasonTrophies = None
            bestSeasonRank = None
            bestSeasonBestTrophies = None
            bestSeasonId = None

        currentFavouriteCard = player_info.get('currentFavouriteCard')
        try:
            currentFavouriteCardName = currentFavouriteCard.get('name')
        except AttributeError:
            currentFavouriteCardName = None

        expLevel = player_info.get('expLevel')
        expPoints = player_info.get('expPoints')
        wins = player_info.get('wins')
        losses = player_info.get('losses')
        battleCount = player_info.get('battleCount')
        threeCrownWins = player_info.get('threeCrownWins')
        challengeCardsWon = player_info.get('challengeCardsWon')
        challengeMaxWins = player_info.get('challengeMaxWins')
        tournamentCardsWon = player_info.get('tournamentCardsWon')
        tournamentBattleCount = player_info.get('tournamentBattleCount')
        warDayWins = player_info.get('warDayWins')
        clanCardsCollected = player_info.get('clanCardsCollected')
        starPoints = player_info.get('starPoints')

        # the insertion tuple
        insertion_tuple = (playerTag, name, clanTag, role, arenaId, arenaName, trophies, bestTrophies,
                           donations, donationsReceived, totalDonations,
                           previousSeasonTrophies, previousSeasonRank, previousSeasonBestTrophies, previousSeasonId,
                           currentSeasonTrophies, currentSeasonRank, currentSeasonBestTrophies, currentSeasonId,
                           bestSeasonTrophies, bestSeasonRank, bestSeasonBestTrophies, bestSeasonId,
                           currentFavouriteCardName, expLevel, expPoints, wins, losses, battleCount,
                           threeCrownWins, challengeCardsWon, challengeMaxWins, tournamentCardsWon,
                           tournamentBattleCount, warDayWins, clanCardsCollected, starPoints)

        psql_insert(con, 'PlayerInfo', insertion_tuple, integrity_error_action='update',
                    primary_key='playerTag', primary_key_value=playerTag)

        log('insert_player_info() success, player_tag = {}'.format(player_tag))

    else:
        # if fails, ignore - this is not a critical part of data collection
        log('Did not insert player info')
        pass


def insert_battle(con, data: dict) -> None:
    """
    Inserts a single battle into the DB.
    :param con: A psycopg2 connection object;
    :param data: A dictionary (subset) taken directly from a battle_log request.
    The data contains information for exactly one battle.
    """
    log('Entered insert_battle()')

    # ------------------------------------------
    # generate battleId
    # ------------------------------------------

    # sha256 of battleTime and player tags of every participant in alphabetical order
    battleTime = data.get('battleTime')

    team = data.get('team') or []
    opponent = data.get('opponent') or []

    participants = team + opponent
    tags = [player.get('tag') for player in participants]
    tags.sort()

    s = ''.join([str(battleTime)] + tags)
    m = hashlib.sha256()
    m.update(s.encode('utf8'))
    battleId = m.hexdigest()

    # ------------------------------------------
    # insert into table BattleInfo
    # ------------------------------------------

    type = data.get('type')
    isLadderTournament = data.get('isLadderTournament')
    try:
        arena = data.get('arena')
        arena_id = arena.get('id')
        arena_name = arena.get('name')
    except AttributeError:
        arena_id = None
        arena_name = None
    try:
        gameMode = data.get('gameMode')
        game_mode_id = gameMode.get('id')
        game_mode_name = gameMode.get('name')
    except AttributeError:
        game_mode_id = None
        game_mode_name = None
    deckSelection = data.get('deckSelection')

    psql_insert(con, 'BattleInfo', (battleId, battleTime, type, isLadderTournament,
                                    arena_id, arena_name, game_mode_id, game_mode_name, deckSelection))

    # ------------------------------------------
    # insert into table BattleParticipant
    # ------------------------------------------

    # for each battle, insert a row for each player
    df = pd.DataFrame(participants)
    df = df.drop('name', axis=1)  # TODO further subsetting

    # add extra columns for BattleParticipant insertion
    team_tags = [player.get('tag') for player in team]
    df['team'] = df['tag'].apply(
        lambda tag: True if tag in team_tags else False)
    df['battleId'] = battleId
    df_sub = df[['battleId', 'tag', 'team']]

    # bulk insertion
    insertion_tuple = df_sub.to_records(index=False).tolist()
    psql_insert(con, 'BattleParticipant', insertion_tuple)

    # ------------------------------------------
    # insert into table BattleData
    # ------------------------------------------

    # make sure all db columns exist in current data (if not set null)
    curr_cols = df.columns
    all_cols = pd.Series(['clan', 'startingTrophies', 'trophyChange', 'crowns',
                          'princessTowersHitPoints', 'kingTowerHitPoints',
                          'boatBattleSide', 'boatBattleWon',
                          'newTowersDestroyed', 'prevTowersDestroyed', 'remainingTowers'])

    def f(col):
        if col not in curr_cols:
            df[col] = None
    all_cols.apply(f)

    df = df.replace({nan: None})  # change NaN to None

    # process clan column
    df['clan'] = df['clan'].apply(lambda entry: entry.get(
        'tag') if entry is not None else None)

    # split princess tower hitpoints into separate columns
    df_princess = []

    def f(col):
        values = [None, None]
        if col is not None:
            if len(col) == 2:
                values = col
            elif len(col) == 1:
                values = col + [None]
        df_princess.append(values)

    df['princessTowersHitPoints'].apply(f)

    df_princess = pd.DataFrame(df_princess, columns=[
                               'princessTower1HitPoints', 'princessTower2HitPoints'])
    df_princess = df_princess.replace({nan: None})

    df = pd.concat([df, df_princess], axis=1)

    # process boatBattle (1v1 always) columns
    if data.get('type') == 'boatBattle':
        # match attacker/defender status with team sides
        df.loc[df['team'], 'boatBattleSide'] = data.get('boatBattleSide')
        df.loc[~(df['team']), 'boatBattleSide'] = 'attacker' if data.get(
            'boatBattleSide') != 'attacker' else 'defender'

        # match win status with team sides
        df.loc[df['team'], 'boatBattleWon'] = data.get('boatBattleWon')
        df.loc[~(df['team']), 'boatBattleWon'] = not data.get('boatBattleWon')

        # these are shared values
        df['newTowersDestroyed'] = data.get('newTowersDestroyed')
        df['prevTowersDestroyed'] = data.get('prevTowersDestroyed')
        df['remainingTowers'] = data.get('remainingTowers')

    # make subset for insertion
    df_sub = df[['battleId', 'tag', 'clan',
                 'startingTrophies', 'trophyChange', 'crowns',
                 'princessTower1HitPoints', 'princessTower2HitPoints', 'kingTowerHitPoints',
                 'boatBattleSide', 'boatBattleWon',
                 'newTowersDestroyed', 'prevTowersDestroyed', 'remainingTowers']]

    # bulk insertion
    insertion_tuple = df_sub.to_records(index=False).tolist()
    psql_insert(con, 'BattleData', insertion_tuple)

    # ------------------------------------------
    # insert into table BattleDeck
    # ------------------------------------------

    # for each battle, insert a row for each player
    # also explode cards column
    df = df.explode('cards')
    df = pd.concat([df.drop(['cards'], axis=1),
                   df['cards'].apply(pd.Series)], axis=1)
    df_sub = df[['battleId', 'tag', 'name', 'level']]

    # bulk insertion
    insertion_tuple = df_sub.to_records(index=False).tolist()
    psql_insert(con, 'BattleDeck', insertion_tuple)

    # ------------------------------------------
    # insert/update table PlayerInfo for all player tags involved
    # ------------------------------------------
    for tag in tags:
        insert_player_info(con, tag)

    log('insert_battle() success')


def get_last_playertag(con) -> str:
    """
    A function that selects the last player tag within table BattleParticipant.
    :return: Either a string or None.
    """
    log('Entered get_last_playertag()')

    with con.cursor() as cur:
        try:
            cur.execute("""
                SELECT playerTag
                FROM BattleParticipant
                WHERE battleId = (
                    SELECT battleId
                    FROM BattleInfo
                    ORDER BY battleTime DESC
                    LIMIT 1
                )
                LIMIT 1;
            """)
            res = cur.fetchone()  # a tuple
            if res is not None:
                return res[0]
            else:
                return None
        except psycopg2.Error as e:
            email_admin(
                400, 'ERROR: Get last playerTag: {}.'.format(str(e).strip()))


def get_random_playertags(con, n=1000) -> str:
    """
    A function that selects random player tags within table BattleParticipant.
    :return: Either a string or None.
    """
    log('Entered get_random_playertags()')

    with con.cursor() as cur:
        try:
            cur.execute("""
                SELECT playerTag FROM BattleParticipant WHERE RANDOM() < 0.01 LIMIT %s;
            """, (n,))
            res = cur.fetchall()  # a list of tuples
            return res  # if no result, []
        except psycopg2.Error as e:
            email_admin(
                400, 'ERROR: Get random playerTags: {}.'.format(str(e).strip()))


def collect_data(init_player_tag_manual=None) -> None:
    """
    Collect data recursively using the technique called crawling.
    Each node is a battle; and from this battle, a list of players can be produced:
    All battle participants + their clanmates.
    Then each player from this list yields a battle log (more battles).
    Now recurse with a level-order traversal to enhance diversity.
    :param con: A psycopg2 connection object;
    :param init_player_tag_manual: A player tag to initialize data collection manually.
    """
    db = DBConnection()
    con = db.get_con()

    # need an initial battle

    if init_player_tag_manual is None:
        init_player_tag = '#9YJUPU9LY'  # default to myself

        # use last player tag from existing player pool if any
        last_tag = get_last_playertag(con)
        if last_tag is not None:
            init_player_tag = last_tag
    else:
        init_player_tag = init_player_tag_manual

    log('collect_data() started with player tag: {}'.format(init_player_tag))

    # retrive a battle from this player tag
    battle_log_res = cr_api_request(init_player_tag, 'battle_log')
    sleep(SLEEP_TIME)

    if battle_log_res.get('statusCode') == 200 and len(battle_log_res.get('body')) > 0:
        # a list of dict, where each dict is a battle
        battle_log = battle_log_res.get('body')
        # randomly pick a battle
        init_battle = battle_log[randrange(len(battle_log))]
    else:
        email_admin(
            400, 'Cannot get battle log from initial player; need to manually specify one; data collection terminated.')
        exit(1)

    # data collection process starts

    # initialize queue for level-order traversal
    queue = deque()
    queue.append(init_battle)

    i = 0  # counts number of inserts

    while len(queue) > 0:
        # stop level order traversal after DB has been populated enough
        if i >= 5:
            break

        # remove front of queue and insert into DB
        curr_battle = queue.popleft()
        insert_battle(con, curr_battle)
        i += 1

        log('Inserted queue front to DB')

        # produce a list of players

        # player tags of battle participants
        team = curr_battle.get('team') or []
        opponent = curr_battle.get('opponent') or []
        participants = team + opponent

        # # clan tags of battle participants if any
        # player_clan_map = {}
        # for player in participants:
        #     clan = player.get('clan')
        #     try:
        #         clan_tag = clan.get('tag')
        #     except AttributeError:
        #         clan_tag = None
        #     player_clan_map[player.get('tag')] = clan_tag

        # # get tags of all members of each clan
        # all_player_tags = []
        # for player_tag in player_clan_map:
        #     clan_tag = player_clan_map.get(player_tag)
        #     if clan_tag is None:
        #         # not part of a clan, append itself
        #         all_player_tags.append(player_tag)
        #     else:
        #         clan_members_res = cr_api_request(clan_tag, 'clan_members')
        #         sleep(SLEEP_TIME)

        #         if clan_members_res.get('statusCode') != 200:  # request failed
        #             # failed to get clan members, append itself
        #             all_player_tags.append(player_tag)
        #         else:
        #             clan = clan_members_res.get('body')
        #             members = clan.get('items')
        #             for member in members:
        #                 all_player_tags.append(member.get('tag'))

        # do not process clans for now to speed up
        all_player_tags = [player.get('tag') for player in participants]

        log('All player tags: {}'.format(len(all_player_tags)))

        # get battle logs of all players, then enqueue
        for player_tag in all_player_tags:
            # get battle log of current player
            battle_log_res = cr_api_request(player_tag, 'battle_log')
            sleep(SLEEP_TIME)

            if battle_log_res.get('statusCode') == 200 and len(battle_log_res.get('body')) > 0:
                # a list of dict, where each dict is a battle
                battle_log = battle_log_res.get('body')

                # enqueue all battles for current player
                for battle in battle_log:
                    queue.append(battle)
            else:
                continue

        log('while() curr iter done')

    # after DB has been populated enough
    # first finish inserting all battles currently in queue
    log('Exited while() - BFS')

    while len(queue) > 0:
        insert_battle(con, queue.popleft())
        sleep(SLEEP_TIME)

    log('Queue emptied')

    # repeat random sampling from existing player pool
    while True:
        log('Entered while-true')

        # a list of 1000 length-1 tuples
        random_playertags = get_random_playertags(con)

        log('Got random player tags')

        # for each player tag, insert all its battles
        for tp in random_playertags:
            log('Entered for-each-random-player-tag')

            tag = tp[0]

            log('Curr random player tag = {}'.format(tag))

            battle_log_res = cr_api_request(tag, 'battle_log')
            sleep(SLEEP_TIME)

            log('Got battle log response for tag: {}'.format(tag))

            if battle_log_res.get('statusCode') == 200 and len(battle_log_res.get('body')) > 0:
                log('Valid battle_log_res')

                # a list of dict, where each dict is a battle
                battle_log = battle_log_res.get('body')

                log('Battle log for player tag {}:\n{}'.format(tag, str(battle_log)))

                log('Start insertion for-loop')

                for battle in battle_log:
                    insert_battle(con, battle)
                    log('Inserted battle:\n{}'.format(str(battle)))
