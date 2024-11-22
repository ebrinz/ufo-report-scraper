import argparse
from src.extract_archived_data import extract_tar
from src.data_processor import process_and_insert_reports
from src.data_transformer import process_and_insert_transformed_reports
from src.data_embeddings import generate_and_insert_embeddings
from db.queries import execute_sql_script, wild_query

def main():
    parser = argparse.ArgumentParser(description="Seed the database with archive data.")
    parser.add_argument('--extract', action='store_true', help='Extract data from tar file in archive')
    parser.add_argument('--ingest', action='store_true', help='Seed the ufo_reports_raw table in the database with archive data')
    parser.add_argument('--transform', action='store_true', help='Format and transform raw data into cleaner state')
    parser.add_argument('--embed', action='store_true', help='Create vectorized embeddings')
    parser.add_argument('--reference', action='store_true', help='Create reference tables ie: geographical lookups')
    parser.add_argument('--setup_summary', action='store_true', help='Check previous steps for incomplete or missing data')
    args = parser.parse_args()

    if args.extract:
        print('Extracting archive data...')
        extract_tar("data/archive/nuforc_dataset.tar" , "data/raw")
    if args.ingest:
        wild_query('DROP TABLE ufo_reports_raw')
        execute_sql_script('db/schema.sql')
        print('Seeding the database with archive data...')
        process_and_insert_reports()
    if args.transform:
        #### this takes way too long - need to implement bulk insert, andperhaps break this into multiple tables
        wild_query('DROP TABLE ufo_reports_transform')
        execute_sql_script('db/schema.sql')
        print('Transforming and formatting raw data...')
        process_and_insert_transformed_reports()
    if args.embed:
        wild_query('DROP TABLE IF EXISTS description_sentence_embeddings')
        wild_query('DROP TABLE IF EXISTS description_averaged_embeddings')
        execute_sql_script('db/schema.sql')
        print('Creating vectorized embeddings with report descriptions...')
        generate_and_insert_embeddings()
    if args.reference:
        print('Creating reference tables...')
        wild_query('DROP TABLE IF EXISTS reference_table')
        execute_sql_script('db/schema.sql')
        # create_reference_tables()
    if args.setup_summary:
        print('Seeding the database with archive data...')
        ## print summary
        # setup_summary()

if __name__ == "__main__":
    main()