from time import time

import pandas as pd
from app.core.logging import logger

DATA_URL = "https://www.msss.gouv.qc.ca/professionnels/statistiques/documents/urgences/Releve_horaire_urgences_7jours_nbpers.csv"

def fetch_dataset(retries: int = 3, delay: int = 10) -> pd.DataFrame:
    for attempt in range(retries):
        try:
            df = pd.read_csv(DATA_URL, encoding="latin1")
            logger.info("Dataset fetched successfully.")
            return df
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)

    raise RuntimeError(f"Failed to fetch dataset after {retries} attempts.")
