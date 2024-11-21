import argparse
from src.extract_archived_data import extract_tar
from src.data_processor import process_and_insert_reports
from src.data_transformer import process_and_insert_transformed_reports
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
        wild_query('DROP TABLE ufo_reports_transform')
        execute_sql_script('db/schema.sql')
        process_and_insert_transformed_reports()
        print('Transforming and formatting raw data...')
    if args.embed:
        print('Creating vectorized embeddings with report descriptions...')
        ## drop embeddings tables
        ## run schema
    if args.reference:
        print('Creating reference tables...')
        ## drop embeddings tables
        ## run schema
    if args.setup_summary:
        print('Seeding the database with archive data...')
        ## print summary
    else:
        print('Run with --help to see instructions.')

if __name__ == "__main__":
    main()