-- ==========================================
-- Notes on Command Execution
-- ==========================================
-- Instead of running shell commands locally, use an HPCC
-- ssh zhang@ada.hpc.stlawu.edu
-- Create scripts: slurm*.run
-- Modify "email" and "PGPASSWORD" to the real values
-- sbatch slurm*.run


-- ==========================================
-- Copy table 'clash' from DB 'hotslogs' into new DB 'clash'
-- ==========================================
-- 1. Export table (takes ~17 hours; output file size ~255 GB, ~636,000,000 rows)
-- pg_dump -U clashuser -h 10.32.95.90 -t clash hotslogs > copy_clash.sql

-- 2. Import table into new DB
-- psql -U clashuser -h 10.32.95.90 -d clash -f copy_clash.sql


-- ==========================================
-- Distribute original table into new tables within new DB 'clash'
-- ==========================================
-- First, sha256(id)
-- Note: clash(id) conveniently happens to be battleTime + (player tags in alphabetical order)
-- To create BattleInfo(battleId), simply perform sha256(clash(id)), then remove '\x'
ALTER TABLE Clash
ADD COLUMN idHash CHAR(64);

UPDATE Clash
SET idHash = ENCODE(SHA256(id::BYTEA), 'hex');


-- ==========================================
-- Insert into BattleInfo
-- ==========================================
INSERT INTO BattleInfo (battleId, battleTime, arenaId, gameModeId)
SELECT idHash, battleTime, arenaId, gameModeId
FROM Clash;


-- ==========================================
-- Insert into BattleParticipant
-- ==========================================
INSERT INTO BattleParticipant (battleId, playerTag)
SELECT idHash, leftTag FROM Clash
UNION ALL
SELECT idHash, rightTag FROM Clash;


-- ==========================================
-- Insert into BattleDeck
-- ==========================================
-- Remove junk characters from deck
WITH DF1 AS (
    SELECT
        idHash, leftTag, rightTag,
        REPLACE(leftDeck, '[', '') AS leftDeck,
        REPLACE(rightDeck, '[', '') AS rightDeck
    FROM Clash
),
DF2 AS (
    SELECT
        idHash, leftTag, rightTag,
        REPLACE(leftDeck, '"', '') AS leftDeck,
        REPLACE(rightDeck, '"', '') AS rightDeck
    FROM DF1
),
DF3 AS (
    SELECT
        idHash, leftTag, rightTag,
        REPLACE(leftDeck, ']', '') AS leftDeck,
        REPLACE(rightDeck, ']', '') AS rightDeck
    FROM DF2
),
-- Split deck into separate columns
DF4 AS (
    SELECT
        idHash,
        leftTag,
        rightTag,
        SPLIT_PART(leftDeck, ', ', 1) AS leftCard1,
        SPLIT_PART(leftDeck, ', ', 2) AS leftLevel1,
        SPLIT_PART(leftDeck, ', ', 3) AS leftCard2,
        SPLIT_PART(leftDeck, ', ', 4) AS leftLevel2,
        SPLIT_PART(leftDeck, ', ', 5) AS leftCard3,
        SPLIT_PART(leftDeck, ', ', 6) AS leftLevel3,
        SPLIT_PART(leftDeck, ', ', 7) AS leftCard4,
        SPLIT_PART(leftDeck, ', ', 8) AS leftLevel4,
        SPLIT_PART(leftDeck, ', ', 9) AS leftCard5,
        SPLIT_PART(leftDeck, ', ', 10) AS leftLevel5,
        SPLIT_PART(leftDeck, ', ', 11) AS leftCard6,
        SPLIT_PART(leftDeck, ', ', 12) AS leftLevel6,
        SPLIT_PART(leftDeck, ', ', 13) AS leftCard7,
        SPLIT_PART(leftDeck, ', ', 14) AS leftLevel7,
        SPLIT_PART(leftDeck, ', ', 15) AS leftCard8,
        SPLIT_PART(leftDeck, ', ', 16) AS leftLevel8,
        SPLIT_PART(rightDeck, ', ', 1) AS rightCard1,
        SPLIT_PART(rightDeck, ', ', 2) AS rightLevel1,
        SPLIT_PART(rightDeck, ', ', 3) AS rightCard2,
        SPLIT_PART(rightDeck, ', ', 4) AS rightLevel2,
        SPLIT_PART(rightDeck, ', ', 5) AS rightCard3,
        SPLIT_PART(rightDeck, ', ', 6) AS rightLevel3,
        SPLIT_PART(rightDeck, ', ', 7) AS rightCard4,
        SPLIT_PART(rightDeck, ', ', 8) AS rightLevel4,
        SPLIT_PART(rightDeck, ', ', 9) AS rightCard5,
        SPLIT_PART(rightDeck, ', ', 10) AS rightLevel5,
        SPLIT_PART(rightDeck, ', ', 11) AS rightCard6,
        SPLIT_PART(rightDeck, ', ', 12) AS rightLevel6,
        SPLIT_PART(rightDeck, ', ', 13) AS rightCard7,
        SPLIT_PART(rightDeck, ', ', 14) AS rightLevel7,
        SPLIT_PART(rightDeck, ', ', 15) AS rightCard8,
        SPLIT_PART(rightDeck, ', ', 16) AS rightLevel8
    FROM DF3
)
INSERT INTO BattleDeck
SELECT idHash, leftTag, CASE WHEN leftCard1 = '' THEN 'leftCard1' ELSE leftCard1 END, NULLIF(leftLevel1, '')::INT FROM DF4 UNION ALL
SELECT idHash, leftTag, CASE WHEN leftCard2 = '' THEN 'leftCard2' ELSE leftCard2 END, NULLIF(leftLevel2, '')::INT FROM DF4 UNION ALL
SELECT idHash, leftTag, CASE WHEN leftCard3 = '' THEN 'leftCard3' ELSE leftCard3 END, NULLIF(leftLevel3, '')::INT FROM DF4 UNION ALL
SELECT idHash, leftTag, CASE WHEN leftCard4 = '' THEN 'leftCard4' ELSE leftCard4 END, NULLIF(leftLevel4, '')::INT FROM DF4 UNION ALL
SELECT idHash, leftTag, CASE WHEN leftCard5 = '' THEN 'leftCard5' ELSE leftCard5 END, NULLIF(leftLevel5, '')::INT FROM DF4 UNION ALL
SELECT idHash, leftTag, CASE WHEN leftCard6 = '' THEN 'leftCard6' ELSE leftCard6 END, NULLIF(leftLevel6, '')::INT FROM DF4 UNION ALL
SELECT idHash, leftTag, CASE WHEN leftCard7 = '' THEN 'leftCard7' ELSE leftCard7 END, NULLIF(leftLevel7, '')::INT FROM DF4 UNION ALL
SELECT idHash, leftTag, CASE WHEN leftCard8 = '' THEN 'leftCard8' ELSE leftCard8 END, NULLIF(leftLevel8, '')::INT FROM DF4 UNION ALL
SELECT idHash, rightTag, CASE WHEN rightCard1 = '' THEN 'rightCard1' ELSE rightCard1 END, NULLIF(rightLevel1, '')::INT FROM DF4 UNION ALL
SELECT idHash, rightTag, CASE WHEN rightCard2 = '' THEN 'rightCard2' ELSE rightCard2 END, NULLIF(rightLevel2, '')::INT FROM DF4 UNION ALL
SELECT idHash, rightTag, CASE WHEN rightCard3 = '' THEN 'rightCard3' ELSE rightCard3 END, NULLIF(rightLevel3, '')::INT FROM DF4 UNION ALL
SELECT idHash, rightTag, CASE WHEN rightCard4 = '' THEN 'rightCard4' ELSE rightCard4 END, NULLIF(rightLevel4, '')::INT FROM DF4 UNION ALL
SELECT idHash, rightTag, CASE WHEN rightCard5 = '' THEN 'rightCard5' ELSE rightCard5 END, NULLIF(rightLevel5, '')::INT FROM DF4 UNION ALL
SELECT idHash, rightTag, CASE WHEN rightCard6 = '' THEN 'rightCard6' ELSE rightCard6 END, NULLIF(rightLevel6, '')::INT FROM DF4 UNION ALL
SELECT idHash, rightTag, CASE WHEN rightCard7 = '' THEN 'rightCard7' ELSE rightCard7 END, NULLIF(rightLevel7, '')::INT FROM DF4 UNION ALL
SELECT idHash, rightTag, CASE WHEN rightCard8 = '' THEN 'rightCard8' ELSE rightCard8 END, NULLIF(rightLevel8, '')::INT FROM DF4;


-- ==========================================
-- Insert into BattleData
-- ==========================================
INSERT INTO BattleData (battleId, playerTag, clanTag, startingTrophies, trophyChange, crowns)
SELECT idHash, leftTag, leftClanTag, leftStartingTrophies, leftTrophyChange, leftCrowns
FROM Clash
UNION ALL
SELECT idHash, rightTag, rightClanTag, rightStartingTrophies, rightTrophyChange, rightCrowns
FROM Clash;








-- TODO: Extensive testing on ADA!
-- \c szhan18_clash
-- drop table clash;
-- create table clash as select * from clash0 limit 3;
-- truncate table battleinfo cascade;
-- RUN THIS SCRIPT
