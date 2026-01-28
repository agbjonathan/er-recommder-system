from app.db.session import SessionLocal
from app.ingestion.fetcher import fetch_dataset
from app.ingestion.parser import clean_dataframe
from app.ingestion.hospital_loader import get_or_create_hospital
from app.ingestion.snapshot_loader import insert_snapshot
from app.core.logging import logger
from app.db.models import Hospital


def load_hospital_map(db):
    hospitals = db.query(Hospital).all()
    return {h.permit_id: h for h in hospitals}

def run_ingestion():
    logger.info("INGESTION STARTED")
    db = SessionLocal()
    try:
        df = fetch_dataset()
        df = clean_dataframe(df)

        hospital_map = load_hospital_map(db)
        count = 0

        for _, row in df.iterrows():
            permit_id = row["No_permis_installation"]

            hospital = hospital_map.get(permit_id)

            if not hospital:
                hospital = get_or_create_hospital(db, row)
                hospital_map[permit_id] = hospital

            insert_snapshot(db, hospital.id, row)
            count += 1

        db.commit()
        logger.info(f"INGESTION COMPLETED: {count} snapshots inserted")
    except Exception:
        db.rollback()
        logger.exception("INGESTION FAILED, transaction rolled back")
        raise
    finally:
        db.close()
if __name__ == "__main__":
    run_ingestion()
