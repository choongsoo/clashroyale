DROP TABLE IF EXISTS BattleInfo CASCADE;
CREATE TABLE BattleInfo (
  battleId           char(36) NOT NULL, 
  battleTime         timestamp NOT NULL, 
  type               varchar(30) NOT NULL, 
  isLadderTournament boolean NOT NULL, 
  arena              varchar(30) NOT NULL, 
  gameMode           varchar(50) NOT NULL, 
  deckSelection      varchar(30) NOT NULL, 
  PRIMARY KEY (battleId));


DROP TABLE IF EXISTS BattleMatch CASCADE;
CREATE TABLE BattleMatch (
  battleId  char(36) NOT NULL, 
  selfTag   varchar(20) NOT NULL, 
  allyTag   varchar(20), 
  rival1Tag varchar(20) NOT NULL, 
  rival2Tag varchar(20), 
  PRIMARY KEY (battleId, selfTag),
  FOREIGN KEY (battleId) REFERENCES BattleInfo (battleId));


DROP TABLE IF EXISTS BattleDeck;
CREATE TABLE BattleDeck (
  battleId   char(36) NOT NULL, 
  playerTag  varchar(20) NOT NULL, 
  card1      varchar(30) NOT NULL, 
  card1Level int4 NOT NULL, 
  card2      varchar(30) NOT NULL, 
  card2Level int4 NOT NULL, 
  card3      varchar(30) NOT NULL, 
  card3Level int4 NOT NULL, 
  card4      varchar(30) NOT NULL, 
  card4Level int4 NOT NULL, 
  card5      varchar(30) NOT NULL, 
  card5Level int4 NOT NULL, 
  card6      varchar(30) NOT NULL, 
  card6Level int4 NOT NULL, 
  card7      varchar(30) NOT NULL, 
  card7Level int4 NOT NULL, 
  card8      varchar(30) NOT NULL, 
  card8Level int4 NOT NULL, 
  PRIMARY KEY (battleId, playerTag),
  FOREIGN KEY (battleId, playerTag) REFERENCES BattleMatch (battleId, selfTag));


DROP TABLE IF EXISTS BattleData;
CREATE TABLE BattleData (
  battleId                char(36) NOT NULL, 
  playerTag               varchar(20) NOT NULL, 
  startingTrophies        int4 NOT NULL, 
  trophyChange            int4, 
  crowns                  int4 NOT NULL, 
  princessTower1HitPoints int4, 
  princessTower2HitPoints int4, 
  kingTowerHitPoints      int4, 
  clanTag                 varchar(20), 
  PRIMARY KEY (battleId, playerTag),
  FOREIGN KEY (battleId, playerTag) REFERENCES BattleMatch (battleId, selfTag));


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
