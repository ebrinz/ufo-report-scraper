from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
from db.connection import get_connection

from logger_config import get_logger
logger = get_logger(__name__)


def generate_and_insert_embeddings():

    model = SentenceTransformer('all-MiniLM-L6-v2')

    sentence_embeddings_data = []
    average_embeddings_data = []

    dbconn = get_connection()
    cursor = dbconn.cursor()

    cursor.execute("SELECT report_id, description FROM ufo_reports_transform;")
    rows = cursor.fetchall()

    for row in rows:
        report_id, sentences = row
        if not sentences:
            continue  # Skip empty descriptions

        embeddings = model.encode(sentences)
        average_embedding = np.mean(embeddings, axis=0)

        for idx, embedding in enumerate(embeddings):
            sentence_embeddings_data.append({
                "report_id": report_id,
                "sentence_id": f"{report_id}_{idx}",
                "embedding": embedding.tolist()
            })

        average_embeddings_data.append({
            "report_id": report_id,
            "embedding": average_embedding.tolist()
        })
        logger.info(f"Processed {report_id} as group of embeddings and averaged embedding!")

    sentence_embeddings_df = pd.DataFrame(sentence_embeddings_data)
    average_embeddings_df = pd.DataFrame(average_embeddings_data)

    sentence_tuples = [
    (row['report_id'], row['sentence_id'], row['embedding'])
    for _, row in sentence_embeddings_df.iterrows()
]
    average_tuples = [
        (row['report_id'], row['embedding'])
        for _, row in average_embeddings_df.iterrows()
    ]

    sentence_insert_query = """
    INSERT INTO description_sentence_embeddings (report_id, sentence_id, embedding)
    VALUES (%s, %s, %s)
    """
    average_insert_query = """
    INSERT INTO description_averaged_embeddings (report_id, embedding)
    VALUES (%s, %s)
    """

    cursor.executemany(sentence_insert_query, sentence_tuples)
    cursor.executemany(average_insert_query, average_tuples)
    dbconn.commit()
