# Consumer Complaint Explorer — EDA Project

An exploratory data analysis project that examines consumer financial complaints and institutional response patterns using Python and interactive dashboards.

## 📌 Project Overview

The Consumer Complaint Explorer analyzes complaint-related data to explore patterns across financial products, issues, states, submission channels, and company responses. The project presents findings through interactive visualizations and filters.

## 🎯 Objectives

- Explore complaint patterns across financial products and issues.
- Analyze complaint distributions across states and submission channels.
- Examine company response types and timely response patterns.
- Use data visualization to make complaint trends easier to understand.
- Build interactive dashboards for data exploration.

## ✨ Features

- Interactive Streamlit dashboard with sidebar navigation.
- Flask-based web dashboard with an HTML frontend.
- Filters for year, product, state, channel, and response-related fields.
- Univariate, bivariate, and multivariate analysis sections.
- KPI summaries, charts, and pivot-table exploration.
- Data preprocessing and a reproducible synthetic demo dataset.

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Streamlit
- Flask
- HTML and JavaScript
- Chart.js

## 📂 Project Structure

```text
consumer-complaint-explorer/
├── .streamlit/
│   └── config.toml
├── data/
│   └── complaints.csv
├── static/
│   ├── index.html
│   └── chart.umd.js
├── app.py
├── streamlit_app.py
├── pipeline.py
├── make_demo_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Prathmpol/consumer-complaint-explorer.git
cd consumer-complaint-explorer
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Run the Streamlit dashboard

```bash
python -m streamlit run streamlit_app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

### 4. Run the Flask dashboard (alternative)

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## 📊 Dataset

The repository includes a small **synthetic demo dataset** so the dashboards can run without downloading the full CFPB dataset.

The demo data is generated using `make_demo_data.py` and is intended for testing and demonstrating dashboard functionality. It should not be interpreted as actual consumer complaint statistics.

The original Consumer Financial Protection Bureau (CFPB) complaint data is not bundled with this repository.

## 📚 Key Learning Outcomes

- Data cleaning and preprocessing
- Exploratory data analysis
- Analysis of categorical and time-based patterns
- Interactive data visualization
- Building dashboards with Python
- Presenting analytical information in an accessible format

## 👨‍💻 Author

**Prathmesh Pol**

- GitHub: [@Prathmpol](https://github.com/Prathmpol)

---

If you find this project useful, feel free to explore the repository and share feedback.