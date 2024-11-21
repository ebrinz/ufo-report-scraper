import argparse
from src.data_processor import process_and_insert_reports

def main():
    parser = argparse.ArgumentParser(description="Seed the database with archive data.")
    parser.add_argument('--seed', action='store_true', help='Seed the ufo_reports_raw table in the database with archive data')
    args = parser.parse_args()

    if args.seed:
        print('Seeding the database with archive data...')
        process_and_insert_reports()
    else:
        print('Run with --seed to seed the database.')

if __name__ == "__main__":
    main()