

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

CREATE TABLE IF NOT EXISTS ufo_reports_transform (
    report_id VARCHAR(255) PRIMARY KEY,
    entered BIGINT,
    occurred BIGINT,
    reported BIGINT,
    posted BIGINT,
    location TEXT,
    shape TEXT,
    duration INT,
    description TEXT[]
);

CREATE TABLE IF NOT EXISTS description_sentence_embeddings (
    report_id VARCHAR(255) NOT NULL,
    sentence_id VARCHAR(255) NOT NULL,
    embedding VECTOR(384),
    PRIMARY KEY (report_id, sentence_id)
);

CREATE TABLE IF NOT EXISTS description_averaged_embeddings (
    report_id VARCHAR(255) PRIMARY KEY,
    embedding VECTOR(384)
);

CREATE TABLE IF NOT EXISTS city_county_lat_lon (
    city_state VARCHAR(255),
    state VARCHAR(2),
    city VARCHAR(255),
    county VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE IF NOT EXISTS geography_lookup (
    report_id VARCHAR(255) PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL,
    county VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT
);