from db.connection import get_connection
from psycopg2.extras import DictCursor

from logger_config import get_logger

logger = get_logger(__name__)

def insert_report(report):
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

def fetch_reports():
    query = "SELECT * FROM ufo_reports_raw;"
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
