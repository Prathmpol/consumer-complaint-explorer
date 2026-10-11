"""Generate a small synthetic complaints.csv (same schema) so the app runs without the 17M-row file."""
import numpy as np, pandas as pd, sys
rng = np.random.default_rng(1); n = 20000
P = {"Credit reporting or other personal consumer reports": .55, "Debt collection": .12, "Credit card": .08,
     "Checking or savings account": .08, "Mortgage": .05, "Vehicle loan or lease": .03,
     "Student loan": .03, "Money transfer or virtual currency": .03, "Payday loan": .02, "Prepaid card": .01}
ISS = ["Incorrect information on your report", "Problem with a credit reporting investigation",
       "Attempts to collect debt not owed", "Managing an account", "Struggling to pay mortgage", "Fraud or scam"]
CO = ["EQUIFAX, INC.", "Experian Information Solutions Inc.", "TRANSUNION INTERMEDIATE HOLDINGS, INC.",
      "BANK OF AMERICA, NATIONAL ASSOCIATION", "WELLS FARGO & COMPANY", "CITIBANK, N.A.", "CAPITAL ONE FINANCIAL CORPORATION", "JPMORGAN CHASE & CO."]
ST = ["CA","TX","FL","NY","GA","PA","IL","NJ","OH","NC","VA","MI"]
RESP = {"Closed with explanation": .61, "Closed with non-monetary relief": .34, "In progress": .035,
        "Closed with monetary relief": .012, "Untimely response": .002, "Closed": .001}
CH = {"Web": .78, "Referral": .1, "Phone": .05, "Postal mail": .03, "Fax": .02, "Email": .02}
pick = lambda d: rng.choice(list(d), n, p=np.array(list(d.values()))/sum(d.values()))
rec = pd.Timestamp("2013-01-01") + pd.to_timedelta(rng.integers(0, 365*13, n), "D")
gap = np.where(rng.random(n) < .85, 0, rng.integers(0, 12, n))
late = rng.random(n) < .007
df = pd.DataFrame({"Date received": rec.strftime("%Y-%m-%d"), "Product": pick(P),
    "Sub-product": rng.choice(["Credit reporting", "Other debt", "General-purpose card", np.nan], n),
    "Issue": rng.choice(ISS, n), "Sub-issue": rng.choice(["Account status incorrect", np.nan, "Not given enough info"], n),
    "Company": rng.choice(CO, n, p=[.2,.2,.2,.1,.1,.08,.07,.05]), "State": rng.choice(ST + [np.nan], n),
    "Submitted via": pick(CH), "Date sent to company": (rec + pd.to_timedelta(gap + late*rng.integers(5,40,n), "D")).strftime("%Y-%m-%d"),
    "Company response to consumer": pick(RESP), "Timely response?": np.where(late, "No", "Yes"),
    "Complaint ID": np.arange(1000, 1000+n),
    "Consumer complaint narrative": pd.Series([("I disputed this account many times and nobody fixed it " * int(k)).strip() if r < .22 else None for r, k in zip(rng.random(n), rng.integers(1, 8, n))])})
df.to_csv(sys.argv[1] if len(sys.argv) > 1 else "data/complaints.csv", index=False)
print("wrote", len(df), "rows")
