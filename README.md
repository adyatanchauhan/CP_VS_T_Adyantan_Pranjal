# Interactive Cp vs T Database for Engineering Materials

A Python/Streamlit web application for exploring and comparing the specific heat capacity (Cp) of 245+ engineering materials as a function of temperature.

## Quick Start

```bash
cd cp-database
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501**

## Project Structure

```
cp-database/
├── app.py                  # Main entry point
├── requirements.txt
├── run.sh                  # Launch script
├── data/
│   └── materials.json      # 245 materials with coefficients
├── src/
│   ├── config.py           # Constants, CSS, data source links
│   ├── cp_calculator.py    # Shomate & polynomial Cp engines
│   ├── data_loader.py      # Database loading & filtering
│   ├── plotting.py         # Plotly chart builders
│   └── ui.py               # Streamlit UI components
└── scripts/
    └── build_database.py   # Regenerate materials.json
```

## Features

- **245 materials** across 9 categories on the left panel
- **Scrollable table** listing every material with name, formula, category, source, and T range
- **Multi-material Cp–T plots** with zoom, pan, and hover tooltips
- **Temperature range warnings** for out-of-range extrapolation
- **Data Sources tab** with full citations and material–source mapping
- **Ranking, browse, and export** capabilities

## Data Sources

- [NIST Chemistry WebBook](https://webbook.nist.gov/chemistry/)
- [NIST JANAF Thermochemical Tables](https://www.nist.gov/srd/janaf)
- [MatWeb](https://www.matweb.com/)
- [ASM Handbook](https://www.asminternational.org/)
- [PoLyInfo (NIMS)](https://polymer.nims.go.jp/)
- [AZoM](https://www.azom.com/)
