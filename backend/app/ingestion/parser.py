import pandas as pd
import pytz

MONTREAL_TZ = pytz.timezone("America/Montreal")

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
    df.columns
    .str.strip()            # remove spaces
    .str.replace(" ", "_")  # spaces → underscores
    .str.replace("'", "")   # remove apostrophes
    .str.normalize("NFKD")  # remove accents
    .str.encode("ascii", errors="ignore")
    .str.decode("utf-8")
    )

    # remove regional totals rows
    df = df[df["Nom_installation"] != "Total régional"]
    df = df[df["Nom_installation"] != "Ensemble du Québec"]

    df["No_permis_installation"] = df["No_permis_installation"].astype(str)
    df["snapshot_time"] = (
        pd.to_datetime(df["Heure_de_lextraction_(image)"])
        .dt.tz_localize(MONTREAL_TZ, ambiguous="infer", nonexistent="shift_forward")
    )
    df["updated_at"] = (
        pd.to_datetime(df["Mise_a_jour"])
        .dt.tz_localize(MONTREAL_TZ, ambiguous="infer", nonexistent="shift_forward")
    )

    # print(df.columns.tolist())

    return df


