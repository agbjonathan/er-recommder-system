import pandas as pd

DATA_URL = "https://www.msss.gouv.qc.ca/professionnels/statistiques/documents/urgences/Releve_horaire_urgences_7jours_nbpers.csv"

def fetch_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL, encoding="latin-1",sep=",")
    return df
