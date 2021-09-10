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
    :param insert_tuple: Values to insert.
    """
    # build up something like this: '(%s, %s, %s)'
    insert_tuple_format = '(' + ('%s, ' * len(insert_tuple))[:-2] + ')'

    with con.cursor() as cur:
        insert_cmd = 'INSERT INTO {} VALUES {};'.format(
            table, insert_tuple_format)

        try:
            cur.execute(insert_cmd, insert_tuple)
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
    # generate battleId:
    # sha256 of battleTime and player tags of every participant in alphabetical order
    battleTime = data.get('battleTime')

    team = data.get('team')
    opponent = data.get('opponent')

    team_tags = [player.get('tag') for player in team]  # len = 1 or 2
    opponent_tags = [player.get('tag') for player in opponent]

    tags = team_tags + opponent_tags
    tags.sort()

    s = ''.join([str(battleTime)] + tags)
    m = hashlib.sha256()
    m.update(s.encode('utf8'))
    battleId = m.hexdigest()

    # insert into table BattleInfo
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

    # insert into table BattleMatch
    # for each battle, insert a row for each player
    # since primary key = battleId + selfTag, need to rotate player tags to make each a selfTag once
    selfTag = team_tags[0]
    rival1Tag = opponent_tags[0]

    if len(tags) == 2:
        psql_insert(con, 'BattleMatch', (battleId,
                    selfTag, None, rival1Tag, None))
        psql_insert(con, 'BattleMatch', (battleId,
                    rival1Tag, None, selfTag, None))

    elif len(tags) == 4:
        allyTag = team_tags[1]
        rival2Tag = opponent_tags[1]
        psql_insert(con, 'BattleMatch', (battleId, selfTag,
                    allyTag, rival1Tag, rival2Tag))
        psql_insert(con, 'BattleMatch', (battleId, allyTag,
                    selfTag, rival1Tag, rival2Tag))
        psql_insert(con, 'BattleMatch', (battleId,
                    rival1Tag, rival2Tag, selfTag, allyTag))
        psql_insert(con, 'BattleMatch', (battleId,
                    rival2Tag, rival1Tag, selfTag, allyTag))

    # TODO insert into BattleDeck and BattleData

    # insert into BattleDeck
    participants = team + opponent


# FIXME for testing only (delete afterwards)
if __name__ == '__main__':
    battle_log_res = cr_api_request('#9YJUPU9LY', 'battle_log')
    battle1 = battle_log_res.get('body')[0]
    insert_battle(CON, battle1)
