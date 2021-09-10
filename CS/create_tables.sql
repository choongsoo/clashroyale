DROP TABLE IF EXISTS BattleInfo CASCADE;
CREATE TABLE BattleInfo (
  battleId           char(64) NOT NULL,  -- made via sha256()
  battleTime         timestamp NOT NULL, 
  type               varchar(30) NOT NULL, 
  isLadderTournament boolean NOT NULL, 
  arena              varchar(30),  -- arena can sometimes be null
  gameMode           varchar(50) NOT NULL, 
  deckSelection      varchar(30) NOT NULL, 
  PRIMARY KEY (battleId));


DROP TABLE IF EXISTS BattleParticipant CASCADE;
CREATE TABLE BattleParticipant (
  battleId    char(64) NOT NULL, 
  playerTag   varchar(20) NOT NULL, 
  team        boolean NOT NULL, 
  PRIMARY KEY (battleId, playerTag),
  FOREIGN KEY (battleId) REFERENCES BattleInfo (battleId));


DROP TABLE IF EXISTS BattleDeck;
CREATE TABLE BattleDeck (
  battleId    char(64) NOT NULL, 
  playerTag   varchar(20) NOT NULL, 
  card        varchar(30) NOT NULL, 
  cardLevel   int4 NOT NULL, 
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
  playerTag             varchar(20) NOT NULL, 
  name                  varchar(30) NOT NULL, 
  expLevel              int4 NOT NULL, 
  trophies              int4 NOT NULL, 
  bestTrophies          int4 NOT NULL, 
  wins                  int4 NOT NULL, 
  losses                int4 NOT NULL, 
  battleCount           int4 NOT NULL, 
  threeCrownWins        int4 NOT NULL, 
  challengeCardsWon     int4 NOT NULL, 
  challengeMaxWins      int4 NOT NULL, 
  tournamentCardsWon    int4 NOT NULL, 
  tournamentBattleCount int4 NOT NULL, 
  role                  varchar(30) NOT NULL, 
  donations             int4 NOT NULL, 
  donationsReceived     int4 NOT NULL, 
  totalDonations        int4 NOT NULL, 
  warDayWins            int4 NOT NULL, 
  clanCardsCollected    int4 NOT NULL, 
  clanTag               varchar(20), 
  arena                 varchar(30) NOT NULL, 
  PRIMARY KEY (playerTag));
