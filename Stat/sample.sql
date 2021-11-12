-- Take a random sample from DB with all relavant tables joined

CREATE TEMP VIEW Sample AS (
    WITH SampleInfo AS (
        SELECT *
        FROM BattleInfo
        WHERE RANDOM() < 0.01
        LIMIT 500000
    ),
    SampleParticipant AS (
        SELECT *
        FROM SampleInfo
        LEFT JOIN BattleParticipant USING (battleId)
    ),
    SampleDeck AS (
        SELECT *
        FROM SampleParticipant
        LEFT JOIN BattleDeck USING (battleId, playerTag)
    ),
    SampleData AS (
        SELECT *
        FROM SampleDeck
        LEFT JOIN BattleData USING (battleId, playerTag)
    )
    SELECT * FROM SampleData
);

\COPY (SELECT * FROM Sample) TO 'clash_sample.csv' CSV HEADER
