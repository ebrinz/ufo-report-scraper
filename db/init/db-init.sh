#!/bin/bash

set -e

psql -U local -d postgres -c "CREATE EXTENSION IF NOT EXISTS postgis;"

echo "Attempting table creation now....."

psql -U "local" -d "postgres" -e --set=VERBOSITY=verbose <<-EOSQL
    CREATE TABLE IF NOT EXISTS ufo_reports_raw (
        report_id VARCHAR(255),
        entered TEXT,
        occurred TEXT,
        reported TEXT,
        posted TEXT,
        location TEXT,
        shape TEXT,
        duration TEXT,
        description TEXT,
        status_code INT,
        characteristics TEXT
    );
EOSQL

