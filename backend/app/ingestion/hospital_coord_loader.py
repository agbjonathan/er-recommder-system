from sqlalchemy.orm import Session
import pandas as pd

from app.db.session import SessionLocal
from app.db.models import Hospital
from app.core.logging import logger

DATASET_URL = "https://www.donneesquebec.ca/recherche/dataset/51998b55-7d4c-4381-8c20-0ac1cd9c1b87/resource/2aa06e66-c1d0-4e2f-bf3c-c2e413c3f84d/download/installationscsv.csv"




def populate_hospital_coords():
    db: Session = SessionLocal()

    df = pd.read_csv(DATASET_URL)

    updated = 0
    skipped = 0

    for _, row in df.iterrows():
        permit_id = str(row.get("INSTAL_COD")).strip()

        if not permit_id:
            continue

        hospital = (
            db.query(Hospital)
            .filter(Hospital.permit_id == permit_id)
            .first()
        )

        if not hospital:
            skipped += 1
            continue

        try:
            hospital.latitude = float(row["LATITUDE"])
            hospital.longitude = float(row["LONGITUDE"])
            db.add(hospital)
            updated += 1
        except (TypeError, ValueError):
            logger.warning(
                f"Invalid coordinates for permit_id={permit_id}"
            )

    db.commit()
    db.close()

    logger.info(
        f"Hospital coordinates updated={updated}, skipped={skipped}"
    )

if __name__ == "__main__":
    populate_hospital_coords()
