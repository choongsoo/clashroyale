DROP TABLE IF EXISTS BattleInfo CASCADE;
CREATE TABLE BattleInfo (
  battleId           char(64) NOT NULL,  -- made via sha256()
  battleTime         timestamp, 
  type               varchar(30), 
  isLadderTournament boolean, 
  arenaId            int4, 
  arena              varchar(30), 
  gameModeId         int4, 
  gameMode           varchar(50), 
  deckSelection      varchar(30), 
  PRIMARY KEY (battleId));


DROP TABLE IF EXISTS BattleParticipant CASCADE;
CREATE TABLE BattleParticipant (
  battleId    char(64) NOT NULL, 
  playerTag   varchar(20) NOT NULL, 
  team        boolean, 
  PRIMARY KEY (battleId, playerTag),
  FOREIGN KEY (battleId) REFERENCES BattleInfo (battleId));


DROP TABLE IF EXISTS BattleDeck;
CREATE TABLE BattleDeck (
  battleId    char(64) NOT NULL, 
  playerTag   varchar(20) NOT NULL, 
  card        varchar(30) NOT NULL, 
  cardLevel   int4, 
  PRIMARY KEY (battleId, playerTag, card),
  FOREIGN KEY (battleId, playerTag) REFERENCES BattleParticipant (battleId, playerTag));


DROP TABLE IF EXISTS BattleData;
CREATE TABLE BattleData (
  battleId                char(64) NOT NULL, 
  playerTag               varchar(20) NOT NULL, 
  clanTag                 varchar(20), 
  startingTrophies        int4, 
  trophyChange            int4, 
  crowns                  int4, 
  princessTower1HitPoints int4, 
  princessTower2HitPoints int4, 
  kingTowerHitPoints      int4, 
  boatBattleSide          char(8), 
  boatBattleWon           boolean, 
  newBoatTowersDestroyed  int4, 
  prevBoatTowersDestroyed int4, 
  remainingBoatTowers     int4, 
  PRIMARY KEY (battleId, playerTag), 
  FOREIGN KEY (battleId, playerTag) REFERENCES BattleParticipant (battleId, playerTag));


DROP TABLE IF EXISTS PlayerInfo;
CREATE TABLE PlayerInfo (
  playerTag                  varchar(20) NOT NULL, 
  name                       varchar(30), 
  clanTag                    varchar(20),
  role                       varchar(30),
  arenaId                    int4,
  arena                      varchar(30),
  trophies                   int4,
  bestTrophies               int4,
  donations                  int4,
  donationsReceived          int4,
  totalDonations             int4,
  previousSeasonTrophies     int4,
  previousSeasonRank         int4,
  previousSeasonBestTrophies int4,
  previousSeasonId           varchar(30),
  currentSeasonTrophies      int4,
  currentSeasonRank          int4,
  currentSeasonBestTrophies  int4,
  currentSeasonId            varchar(30),
  bestSeasonTrophies         int4,
  bestSeasonRank             int4,
  bestSeasonBestTrophies     int4,
  bestSeasonId               varchar(30),
  currentFavouriteCard       varchar(30),
  expLevel                   int4,
  expPoints                  int4,
  wins                       int4,
  losses                     int4,
  battleCount                int4,
  threeCrownWins             int4,
  challengeCardsWon          int4,
  challengeMaxWins           int4,
  tournamentCardsWon         int4,
  tournamentBattleCount      int4,
  warDayWins                 int4,
  clanCardsCollected         int4,
  starPoints                 int4,
  PRIMARY KEY (playerTag));
