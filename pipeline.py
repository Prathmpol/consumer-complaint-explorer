"""Data pipeline mirroring Final_Consumer_Complaints_EDA.ipynb (load -> sample -> clean)."""
import os
import numpy as np
import pandas as pd

COLS = ["Date received", "Product", "Sub-product", "Issue", "Sub-issue", "Company", "State",
        "Submitted via", "Date sent to company", "Company response to consumer",
        "Timely response?", "Complaint ID", "Consumer complaint narrative"]
SAMPLE_N, SEED = 120_000, 42


def load_clean(path: str) -> pd.DataFrame:
    # usecols keeps memory low on the 17M-row raw file; pandas sample ~ notebook's polars sample
    df = pd.read_csv(path, usecols=COLS, dtype=str)
    if len(df) > SAMPLE_N:
        df = df.sample(n=SAMPLE_N, random_state=SEED)
    df["Consumer complaint narrative"] = df["Consumer complaint narrative"].fillna("Not Provided")
    df["Sub-product"] = df["Sub-product"].fillna("Not Specified")
    df["Sub-issue"] = df["Sub-issue"].fillna("Not Specified")
    core = ["Date received", "Product", "Company", "State", "Submitted via",
            "Company response to consumer", "Timely response?", "Complaint ID"]
    df = df.dropna(subset=core).drop_duplicates().drop_duplicates(subset=["Complaint ID"])
    df["Date received"] = pd.to_datetime(df["Date received"], errors="coerce")
    df["Date sent to company"] = pd.to_datetime(df["Date sent to company"], errors="coerce")
    d = (df["Date sent to company"] - df["Date received"]).dt.days
    q1, q3 = d.quantile(.25), d.quantile(.75)
    iqr = q3 - q1
    lo, hi = (d.quantile(.01), d.quantile(.99)) if iqr == 0 else (q1 - 1.5 * iqr, q3 + 1.5 * iqr)
    df["days_to_send"] = d.clip(lo, hi)  # cap outliers, as in the notebook
    df["timely_flag"] = (df["Timely response?"] == "Yes").astype(int)
    df["word_count"] = np.where(df["Consumer complaint narrative"] == "Not Provided", np.nan,
                                df["Consumer complaint narrative"].str.split().str.len())
    return df.dropna(subset=["Date received"]).reset_index(drop=True)
