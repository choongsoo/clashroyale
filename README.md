# SYE
* My Stat/CS SYE involving Clash Royale...
    - The CS part is all about data collection and warehousing.
    - The Stat component concerns data analysis.

## CS
* The CS portion of the SYE deals with data collection/warehousing/migration.
* Make sure you're in directory CS/ (run `cd CS`)

### DB Creation
* Refer to er_diagram.pdf for ER diagram of the PostgreSQL database.
* create_tables.sql creates all tables involved (should be already created on host 10.32.95.90).
    - If not yet created, run `psql -U clashuser -h 10.32.95.90 -d clash -f create_tables.sql`
* Inspect the database with `psql -U clashuser -h 10.32.95.90 -d clash`

### Data Migration
* The goal is to migrate our original table (with less columns) to this new database.
* The original table Clash resides in database Hotlogs (on host 10.32.95.90). I made a copy of it to database Clash.
* `cd data_migration`
    - data_migration_batch.sql is the migration script.
    - It commits by batches of size 1 million rows.
    - Run it with `psql -U clashuser -h 10.32.95.90 -d clash -f data_migration_batch.sql`

### Data Collection (Crawling)
* Open `helpers.py`
    - In function `email_admin`, set variables `sender_email` and `receiver_email` to the email you want to use to be notified of any bugs.
    - Preferably Gmail, created specifically for development.
    - Turn on "allow less secure apps" in account settings.
* `cd credentials`
    - Create file `psql-pass.txt`
        - Contains the password for clashuser.
        - Just the password, no empty line.
    - Create file `dev-gmail-pass.txt`
        - Contains the password for the email used to notify admin of any bugs.
        - Just the password, no empty line.
* `cd ..` (back to directory CS/)
    - Install dependencies: `pip install -r requirements.txt`
    - Run collection script with `python main.py`
    - If it is the first time you run this, it is expected to fail - in which case:
        - You will receive an email in your dev gmail you provided in a previou step.
        - It should include the following message: API key does not allow access from IP x.x.x.x
        - Log into Clash Royale API (https://developer.clashroyale.com/).
        - Create a new API key using the appropriate IP address x.x.x.x; copy the token.
        - Go to directory credentials `cd credentials`
        - Open api_keys.json
        - Add in the new token you just created; make sure it is the first one in the JSON file.
        - `cd ..` and `python main.py` again. It should work now.
