import argparse
from src.data_processor import process_and_insert_reports

def main():
    parser = argparse.ArgumentParser(description="Seed the database with archive data.")
    parser.add_argument('--ingest', action='store_true', help='Seed the ufo_reports_raw table in the database with archive data')
    parser.add_argument('--transform', action='store_true', help='Format and transform raw data into cleaner state')
    parser.add_argument('--embed', action='store_true', help='Create vectorized embeddings')
    parser.add_argument('--reference', action='store_true', help='Create reference tables ie: geographical lookups')
    args = parser.parse_args()

    if args.ingest:
        print('Seeding the database with archive data...')
        process_and_insert_reports()
    else:
        print('Run with --seed to seed the database.')

if __name__ == "__main__":
    main()