import psycopg2
import hashlib
import pandas as pd

import extensions.load_api_key
from extensions.connect_db import DBConnection
from request_funcs import cr_api_request
from helpers import email_admin


DB = DBConnection()
CON = DB.get_con()


def psql_insert(con, table: str, insert_tuple: tuple) -> None:
    """
    A helper function that does exactly what INSERT INTO does
    (when inserting into all columns).
    :param table: Name of the table;
    :param insert_tuple: Values to insert - usually a single tuple,
    but if bulk=True, a tuple of tuples.
    """
    # detect if this is a bulk insertion
    bulk = type(insert_tuple[0]) is tuple
    num_attr = len(insert_tuple) if not bulk else len(insert_tuple[0])

    # build up something like this: '(%s, %s, %s)'
    insert_tuple_format = '(' + ('%s, ' * num_attr)[:-2] + ')'

    with con.cursor() as cur:
        insert_cmd = 'INSERT INTO {} VALUES {};'.format(
            table, insert_tuple_format)

        try:
            if not bulk:
                cur.execute(insert_cmd, insert_tuple)
            else:
                cur.executemany(insert_cmd, insert_tuple)
        # FIXME iff violates primary key constraint, do not email
        except psycopg2.Error as e:
            email_admin(
                400, 'ERROR: Insertion: {}.'.format(str(e).strip()))
            return


def insert_battle(con, data: dict) -> None:
    """
    Inserts a single battle into the DB.
    :param data: A dictionary (subset) taken directly from a battle_log request.
    The data contains information for exactly one battle.
    """
    # ------------------------------------------
    # generate battleId
    # ------------------------------------------

    # sha256 of battleTime and player tags of every participant in alphabetical order
    battleTime = data.get('battleTime')

    team = data.get('team')
    opponent = data.get('opponent')

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
        arena = data.get('arena').get('name')
    except AttributeError:
        arena = None
    try:
        gameMode = data.get('gameMode').get('name')
    except AttributeError:
        gameMode = None
    deckSelection = data.get('deckSelection')

    psql_insert(con, 'BattleInfo', (battleId, battleTime, type,
                isLadderTournament, arena, gameMode, deckSelection))

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
    psql_insert(CON, 'BattleParticipant', insertion_tuple)

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
    psql_insert(CON, 'BattleDeck', insertion_tuple)

    # ------------------------------------------
    # insert into table BattleData
    # ------------------------------------------

    # TODO


# FIXME for testing only (delete afterwards)
if __name__ == '__main__':
    battle_log_res = cr_api_request('#9YJUPU9LY', 'battle_log')
    battle1 = battle_log_res.get('body')[0]
    insert_battle(CON, battle1)
