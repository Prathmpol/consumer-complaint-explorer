# Consumer Complaint Explorer

Web frontend for `Final_Consumer_Complaints_EDA.ipynb`. `pipeline.py` repeats the notebook's sampling and cleaning,
`app.py` (Flask) serves the aggregates as JSON, and `static/index.html` is the dashboard. The dashboard has
filters (product, state, channel, dates), KPIs, and tabs for the univariate, bivariate, multivariate and pivot-table sections.

    pip install -r requirements.txt
    COMPLAINTS_CSV=/path/to/complaints.csv python app.py     # then open http://localhost:5000

With no `COMPLAINTS_CSV` it reads `data/complaints.csv`, which is a 20k-row synthetic demo file
(regenerate with `python make_demo_data.py`). The real CFPB file is not bundled. If you point at it, the app samples
120,000 rows with seed 42. Loading the 17M-row file with pandas needs several GB of RAM.

## Streamlit dashboard (sidebar navigation + filters)

    streamlit run streamlit_app.py

The sidebar has Home / Univariate / Bivariate / Multivariate navigation and Year, Product, State, Channel and Timely filters.
The earlier Flask + HTML version (`app.py`, `static/`) still works.
