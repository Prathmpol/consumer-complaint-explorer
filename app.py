"""Flask backend: serves the dashboard and JSON aggregates computed from the notebook's cleaned data.
Run:  COMPLAINTS_CSV=path/to/complaints.csv python app.py   (defaults to data/complaints.csv)"""
import os
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from pipeline import load_clean

CSV = os.environ.get("COMPLAINTS_CSV", os.path.join(os.path.dirname(__file__), "data", "complaints.csv"))
app = Flask(__name__, static_folder="static", static_url_path="")
import numpy as np
app.json.default = lambda o: (o.item() if isinstance(o, np.generic) else str(o))
DF = load_clean(CSV)
print(f"Loaded {len(DF):,} cleaned rows from {CSV}")


def filtered():
    d, a = DF, request.args
    for key, col in (("product", "Product"), ("state", "State"), ("channel", "Submitted via")):
        vals = [v for v in a.getlist(key) if v]
        if vals:
            d = d[d[col].isin(vals)]
    if a.get("start"):
        d = d[d["Date received"] >= a["start"]]
    if a.get("end"):
        d = d[d["Date received"] <= a["end"]]
    return d


def grid(t):
    """DataFrame -> nested list with NaN as None (NaN is not valid JSON)."""
    return t.astype(object).where(t.notna(), None).values.tolist()


def counts(s, n=10):
    vc = s.value_counts().head(n)
    return {"labels": vc.index.tolist(), "values": vc.values.tolist()}


def monthly(d, col="Date received"):
    m = d.set_index(col).resample("ME").size()
    return {"labels": m.index.strftime("%Y-%m").tolist(), "values": m.values.tolist()}


def stacked_pct(d, row, col, top=None):
    if top:
        d = d[d[row].isin(d[row].value_counts().head(top).index)]
    ct = pd.crosstab(d[row], d[col], normalize="index") * 100
    return {"rows": ct.index.tolist(), "cols": ct.columns.tolist(), "data": ct.round(2).values.tolist()}


def box(d, cat, top=5):
    d = d[d[cat].isin(d[cat].value_counts().head(top).index)]
    out = []
    for k, g in d.groupby(cat)["days_to_send"]:
        q = g.quantile([.25, .5, .75])
        out.append({"label": k, "q1": q[.25], "median": q[.5], "q3": q[.75],
                    "mean": round(g.mean(), 3), "max": g.max(), "n": len(g)})
    return out


def matrix(d, row, col, top_r=5, top_c=5, value=None):
    d = d[d[row].isin(d[row].value_counts().head(top_r).index)]
    if top_c:
        d = d[d[col].isin(d[col].value_counts().head(top_c).index)]
    t = (pd.crosstab(d[row], d[col]) if value is None else
         pd.pivot_table(d, index=row, columns=col, values=value, aggfunc="mean") * 100)
    t = t.round(1)
    return {"rows": t.index.tolist(), "cols": t.columns.tolist(), "data": grid(t)}


def pivot_table(d, idx, col, n=10):
    t = pd.pivot_table(d, index=idx, columns=col, values="Complaint ID", aggfunc="count", fill_value=0)
    t["Total"] = t.sum(axis=1)
    t = t.sort_values("Total", ascending=False).head(n)
    return {"cols": [idx] + t.columns.tolist(), "rows": [[i] + r for i, r in zip(t.index, t.values.tolist())]}


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/meta")
def meta():
    return jsonify({
        "products": DF["Product"].value_counts().index.tolist(),
        "states": sorted(DF["State"].unique().tolist()),
        "channels": DF["Submitted via"].value_counts().index.tolist(),
        "min_date": DF["Date received"].min().strftime("%Y-%m-%d"),
        "max_date": DF["Date received"].max().strftime("%Y-%m-%d"),
        "total_rows": len(DF)})


@app.get("/api/dashboard")
def dashboard():
    d = filtered()
    if d.empty:
        return jsonify({"empty": True})
    chan = d["Submitted via"].value_counts()
    small = chan[chan / chan.sum() * 100 < 2]
    chan = chan[chan / chan.sum() * 100 >= 2]
    if small.sum() > 0:
        chan["Other"] = small.sum()
    wc = d["word_count"].dropna()
    top3 = d["Product"].value_counts().head(3).index
    mp = (d[d["Product"].isin(top3)].groupby("Product").resample("ME", on="Date received").size().unstack(0).fillna(0))
    p3 = d[d["Product"].isin(d["Product"].value_counts().head(5).index)]
    p3 = p3.groupby(["Product", "Timely response?"])["days_to_send"].mean().unstack().round(3)
    pv3 = d.groupby("Product")["days_to_send"].agg(["mean", "median", "count"]).sort_values("mean", ascending=False)
    hist = pd.cut(wc, bins=40).value_counts(sort=False) if len(wc) else pd.Series(dtype=int)
    return jsonify({
        "kpis": {"total": len(d), "timely_pct": round(d["timely_flag"].mean() * 100, 2),
                 "avg_days": round(d["days_to_send"].mean(), 2),
                 "narrative_pct": round(len(wc) / len(d) * 100, 1),
                 "companies": int(d["Company"].nunique()),
                 "monetary_pct": round((d["Company response to consumer"] == "Closed with monetary relief").mean() * 100, 2)},
        "univariate": {
            "monthly_received": monthly(d), "monthly_sent": monthly(d, "Date sent to company"),
            "product": counts(d["Product"]), "sub_product": counts(d["Sub-product"]),
            "issue": counts(d["Issue"]), "sub_issue": counts(d["Sub-issue"]),
            "company": counts(d["Company"]), "state": counts(d["State"]),
            "channel": {"labels": chan.index.tolist(), "values": chan.values.tolist()},
            "response": counts(d["Company response to consumer"], 20),
            "timely": counts(d["Timely response?"]),
            "words": {"labels": [f"{int(i.left)}-{int(i.right)}" for i in hist.index], "values": hist.values.tolist()}},
        "bivariate": {
            "product_timely": stacked_pct(d, "Product", "Timely response?", 5),
            "state_timely": stacked_pct(d, "State", "Timely response?", 5),
            "channel_timely": stacked_pct(d, "Submitted via", "Timely response?"),
            "product_response": stacked_pct(d, "Product", "Company response to consumer", 5),
            "issue_timely": stacked_pct(d, "Issue", "Timely response?", 10),
            "box_product": box(d, "Product"), "box_state": box(d, "State"),
            "box_channel": box(d, "Submitted via", 6), "box_response": box(d, "Company response to consumer", 8)},
        "multivariate": {
            "product_state": matrix(d, "Product", "State"),
            "state_response": matrix(d, "State", "Company response to consumer", 5, None),
            "product_channel_rate": matrix(d, "Product", "Submitted via", 5, None, value="timely_flag"),
            "avg_days": {"rows": p3.index.tolist(), "cols": p3.columns.tolist(), "data": grid(p3)},
            "monthly_top3": {"labels": mp.index.strftime("%Y-%m").tolist(),
                             "series": {k: mp[k].astype(int).tolist() for k in mp.columns}}},
        "pivots": {"product_timely": pivot_table(d, "Product", "Timely response?"),
                   "state_response": pivot_table(d, "State", "Company response to consumer"),
                   "days_by_product": {"cols": ["Product", "avg_days_to_send", "median_days_to_send", "complaint_count"],
                                       "rows": [[i, round(r["mean"], 3), r["median"], int(r["count"])] for i, r in pv3.iterrows()]}}})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
