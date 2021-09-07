import psycopg2
import hashlib
import extensions.load_api_key
from extensions.connect_db import DBConnection
from request_funcs import cr_api_request
from helpers import email_admin


db = DBConnection()
con = db.get_con()


def insert_battle(data: dict) -> None:
    """
    Inserts a single battle into the DB.
    :param data: A dictionary (subset) taken directly from a battle_log request.
    The data contains information for exactly one battle.
    """
    # generate battleId:
    # sha256 of battleTime and player tags of every participant in alphabetical order
    battleTime = data.get('battleTime')
    tags = []

    team = data.get('team')
    opponent = data.get('opponent')
    participants = team + opponent

    for player in participants:
        tags.append(player.get('tag'))

    tags.sort()

    s = ''.join([str(battleTime)] + tags)
    m = hashlib.sha256()
    m.update(s.encode('utf8'))
    battleId = m.hexdigest()

    # table BattleInfo
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

    with con.cursor() as cur:
        insert_cmd = 'INSERT INTO BattleInfo VALUES (%s, %s, %s, %s, %s, %s, %s);'
        insert_tuple = (battleId, battleTime, type,
                        isLadderTournament, arena, gameMode, deckSelection)

        try:
            cur.execute(insert_cmd, insert_tuple)
        except psycopg2.Error as e:
            email_admin(
                400, 'ERROR: Battle insertion: {}.'.format(str(e).strip()))
            return

    # table BattleMatch
    # TODO 3 more tables
    # TODO TODO TODO


# FIXME for testing only (delete afterwards)
if __name__ == '__main__':
    battle_log_res = cr_api_request('#9YJUPU9LY', 'battle_log')
    battle1 = battle_log_res.get('body')[0]
    insert_battle(battle1)
