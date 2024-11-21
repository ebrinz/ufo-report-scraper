

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
)

CREATE TABLE IF NOT EXISTS ufo_reports_transform (
    report_id VARCHAR(255) PRIMARY KEY,
    entered TIMESTAMP,
    occurred TIMESTAMP,
    reported TIMESTAMP,
    posted TIMESTAMP,
    location TEXT,
    shape TEXT,
    duration INT,
    description TEXT[],
)

CREATE TABLE IF NOT EXISTS description_sentence_embeddings (
    report_id VARCHAR(255) PRIMARY KEY,
    sentence_id VARCHAR(255),
    embedding VECTOR(128),
)

CREATE TABLE IF NOT EXISTS description_averaged_embeddings (
    report_id VARCHAR(255) PRIMARY KEY,
    embedding VECTOR(128),
)
;