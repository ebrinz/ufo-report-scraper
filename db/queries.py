from db.connection import get_connection

import psycopg2
from psycopg2.extras import DictCursor

from logger_config import get_logger



logger = get_logger(__name__)

def execute_sql_script(script_path: str):
    conn = None
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        logger.info(f"Executing schema SQL script from {script_path}")
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
        conn.commit()
        logger.info("Schema setup completed successfully.")
    except FileNotFoundError:
        logger.error(f"Schema script file not found: {script_path}")
        raise
    except Exception as e:
        logger.error(f"Error executing schema script: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed after executing schema script.")

def wild_query(query, fetch_results=False):
    conn = None
    results = None
    try:
        logger.info(f"Attempting to wild query: {query}")
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            if fetch_results:
                results = cursor.fetchall()
        conn.commit()
        logger.info(f"Successfully ran: {query}")
    except Exception as e:
        logger.error(f"Error in query execution: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed.")
    return results

def insert_report_raw(report):
    insert_query = """
        INSERT INTO ufo_reports_raw (
            report_id, entered, occurred, reported, posted,
            location, shape, duration, description, status_code, characteristics
        )
        VALUES (
            %(report_id)s, %(entered)s, %(occurred)s, %(reported)s, %(posted)s,
            %(location)s, %(shape)s, %(duration)s, %(description)s, %(status_code)s, %(characteristics)s
        )
    """
    conn = None
    try:
        logger.info(f"Attempting to insert report: {report['report_id']}")
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(insert_query, report)
        conn.commit()
        logger.info(f"Successfully inserted report: {report['report_id']}")
    except Exception as e:
        logger.error(f"Error inserting report: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed after insert.")

def insert_reports_raw_bulk(reports):
    if not reports:
        logger.info("No reports to insert.")
        return

    insert_query = """
        INSERT INTO ufo_reports_raw (
            report_id, entered, occurred, reported, posted,
            location, shape, duration, description, status_code, characteristics
        )
        VALUES %s
    """
    conn = None
    try:
        logger.info(f"Attempting to bulk insert {len(reports)} reports.")
        conn = get_connection()
        with conn.cursor() as cursor:
            psycopg2.extras.execute_values(
                cursor, insert_query,
                [(r['report_id'], r['entered'], r['occurred'], r['reported'], r['posted'],
                  r['location'], r['shape'], r['duration'], r['description'], r['status_code'], r['characteristics'])
                 for r in reports]
            )
        conn.commit()
        logger.info(f"Successfully inserted {len(reports)} reports.")
    except Exception as e:
        logger.error(f"Error in bulk insert: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed after bulk insert.")


def fetch_raw_reports():
    query = "SELECT * FROM ufo_reports_raw where status_code = 200;"
    conn = None
    try:
        logger.info("Fetching all reports from the database.")
        conn = get_connection()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
        logger.info(f"Fetched {len(results)} reports from the database.")
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        return []
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed after fetch.")

def insert_report_transform(report):
    insert_query = """
        INSERT INTO ufo_reports_transform (
            report_id, entered, occurred, reported, posted,
            location, shape, duration, description
        )
        VALUES (
            %(report_id)s, %(entered)s, %(occurred)s, %(reported)s, %(posted)s,
            %(location)s, %(shape)s, %(duration)s, %(description)s
        )
    """
    conn = None
    try:
        logger.info(f"Attempting to insert report: {report['report_id']}")
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(insert_query, report)
        conn.commit()
        logger.info(f"Successfully inserted report: {report['report_id']}")
    except Exception as e:
        logger.error(f"Error inserting report: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed after insert.")


def insert_reports_transform_bulk(reports):
    if not reports:
        logger.info("No reports to insert.")
        return

    insert_query = """
        INSERT INTO ufo_reports_transform (
            report_id, entered, occurred, reported, posted,
            location, shape, duration, description
        )
        VALUES %s
    """
    conn = None
    try:
        logger.info(f"Attempting to bulk insert {len(reports)} transformed reports.")
        conn = get_connection()
        with conn.cursor() as cursor:
            psycopg2.extras.execute_values(
                cursor, insert_query,
                [(r['report_id'], r['entered'], r['occurred'], r['reported'], r['posted'],
                r['location'], r['shape'], r['duration'], r['description'])
                for r in reports]
            )
        conn.commit()
        logger.info(f"Successfully inserted {len(reports)} transformed reports.")
    except Exception as e:
        logger.error(f"Error in bulk insert: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed after bulk insert.")
