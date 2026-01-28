from app.db.models import Hospital

def get_or_create_hospital(db, row):
    permit_id = row["No_permis_installation"]

    hospital = db.query(Hospital).filter_by(permit_id=permit_id).first()
    if hospital:
        return hospital

    hospital = Hospital(
        establishment=row["Nom_etablissement"],
        name=row["Nom_installation"],
        region=row["Region"],
        permit_id=permit_id,
        latitude=0.0,   # temporary
        longitude=0.0,  # temporary
        phone=None,
        is_active=True,
    )

    db.add(hospital)
    db.commit()
    db.refresh(hospital)

    return hospital
