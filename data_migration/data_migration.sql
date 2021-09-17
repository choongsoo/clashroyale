-- ==========================================
-- Copy table into new DB
-- ==========================================
-- 1. Export table (run in command line, takes 2-3 hours, 32 GB)
-- pg_dump -U clashuser -h 10.32.95.90 -t clash hotslogs > copy_clash.sql

-- 2. Import table into new DB (run in command line)
-- psql -U clashuser -h 10.32.95.90 -d clash -f copy_clash.sql

-- [Optional]: Instead of running the commands locally, use an HPCC
-- ssh zhang@ada.hpc.stlawu.edu
-- Create scripts: slurm_copy_clash.run and slurm_import_clash.run
-- Modify "email" and "PGPASSWORD" to the real values
-- sbatch slurm_copy_clash.run
-- Wait 2-3 hours, then check if copy_clash.sql has been created
-- sbatch slurm_import_clash.run


-- ==========================================
-- Distribute original table into new tables within new DB
-- ==========================================

-- Remove junk characters from deck
WITH DF1 AS (
    SELECT
        REPLACE(deck, '[', '') AS deck
    FROM
        tmp
),
DF2 AS (
    SELECT
        REPLACE(deck, '"', '') AS deck
    FROM
        DF1
),
DF3 AS (
    SELECT
        REPLACE(deck, ']', '') AS deck
    FROM
        DF2
)
-- Split deck into separate columns
SELECT
    SPLIT_PART(deck, ', ', 1) AS c1,
    SPLIT_PART(deck, ', ', 2) AS l1,
    SPLIT_PART(deck, ', ', 3) AS c2,
    SPLIT_PART(deck, ', ', 4) AS l2,
    SPLIT_PART(deck, ', ', 5) AS c3,
    SPLIT_PART(deck, ', ', 6) AS l3,
    SPLIT_PART(deck, ', ', 7) AS c4,
    SPLIT_PART(deck, ', ', 8) AS l4,
    SPLIT_PART(deck, ', ', 9) AS c5,
    SPLIT_PART(deck, ', ', 10) AS l5,
    SPLIT_PART(deck, ', ', 11) AS c6,
    SPLIT_PART(deck, ', ', 12) AS l6,
    SPLIT_PART(deck, ', ', 13) AS c7,
    SPLIT_PART(deck, ', ', 14) AS l7,
    SPLIT_PART(deck, ', ', 15) AS c8,
    SPLIT_PART(deck, ', ', 16) AS l8
FROM
    DF3;


-- Note: clash(id) conveniently happens to be battleTime + (player tags in alphabetical order)
-- To create BattleInfo(battleId), simply perform sha256(clash(id)), then remove '\x'
select encode(sha256(deck::bytea), 'hex') from tmp;
