from sqlalchemy.exc import IntegrityError
from app.db.models import ERSnapshot
from sqlalchemy.dialects.postgresql import insert

def insert_snapshot(db, hospital_id, row):
    
    stmt = (
        insert(ERSnapshot)
        .values(
            hospital_id=hospital_id,
            functional_stretchers=row["Nombre_de_civieres_fonctionnelles"],
            occupied_stretchers=row["Nombre_de_civieres_occupees"],
            patients_total=row["Nombre_total_de_patients_presents_a_lurgence"],
            patients_waiting_mc=row["Nombre_total_de_patients_en_attente_de_PEC"],
            patients_over_24h=row["Nombre_de_patients_sur_civiere_plus_de_24_heures"],
            patients_over_48h=row["Nombre_de_patients_sur_civiere_plus_de_48_heures"],
            avg_stay_stretcher=row["DMS_sur_civiere"],
            avg_stay_ambulatory=row["DMS_ambulatoire"],
            snapshot_time=row["snapshot_time"],
            updated_at=row["updated_at"],
        )
        .on_conflict_do_nothing()
    )

    # Let the caller manage transaction boundaries; duplicates are skipped by ON CONFLICT DO NOTHING.
    db.execute(stmt)
