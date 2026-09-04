"""Application configuration and constants."""

DATA_SOURCES = [
    {
        "name": "NIST Chemistry WebBook",
        "url": "https://webbook.nist.gov/chemistry/",
        "description": "Shomate equation coefficients for elements, gases, and inorganic compounds.",
    },
    {
        "name": "NIST JANAF Thermochemical Tables",
        "url": "https://www.nist.gov/srd/janaf",
        "description": "Thermochemical data for pure substances and reactions.",
    },
    {
        "name": "MatWeb Material Property Data",
        "url": "https://www.matweb.com/",
        "description": "Engineering properties for metals, alloys, ceramics, and polymers.",
    },
    {
        "name": "ASM Handbook",
        "url": "https://www.asminternational.org/",
        "description": "Authoritative data for metals, alloys, and heat-treatment properties.",
    },
    {
        "name": "PoLyInfo (NIMS Polymer Database)",
        "url": "https://polymer.nims.go.jp/",
        "description": "Thermophysical properties of commercial polymer materials.",
    },
    {
        "name": "AZoM Materials Database",
        "url": "https://www.azom.com/",
        "description": "Specific heat and thermal data for engineering materials.",
    },
]

SOURCE_URLS = {
    "NIST Chemistry WebBook (webbook.nist.gov)": "https://webbook.nist.gov/chemistry/",
    "MatWeb / ASM Handbook": "https://www.matweb.com/",
    "MatWeb": "https://www.matweb.com/",
    "ASM Handbook": "https://www.asminternational.org/",
    "PoLyInfo / MatWeb": "https://polymer.nims.go.jp/",
    "PoLyInfo": "https://polymer.nims.go.jp/",
    "MatWeb / AZoM": "https://www.azom.com/",
    "MatWeb / ASM": "https://www.matweb.com/",
    "Engineering handbook": "https://webbook.nist.gov/chemistry/",
}

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

:root {
    --bg: #0a0d13;
    --panel: #12151c;
    --panel2: #171c26;
    --panel3: #1c2230;
    --border: #262e3d;
    --border2: #323c50;
    --accent: #2e86ab;
    --accent2: #4ecdc4;
    --accent3: #7c5cff;
    --text: #e8edf5;
    --muted: #93a1b5;
    --muted2: #6b7688;
    --radius: 14px;
    --shadow: 0 8px 30px rgba(0,0,0,.45);
}

.stApp {
    background: 
        radial-gradient(1200px 600px at 12% -10%, rgba(46,134,171,.18), transparent 60%),
        radial-gradient(1000px 500px at 100% 0%, rgba(124,92,255,.14), transparent 55%),
        var(--bg) !important;
    font-family: "Inter", system-ui, -apple-system, sans-serif !important;
    color: var(--text) !important;
}

[data-testid="stSidebar"] {
    background: rgba(15,18,25,.75) !important;
    border-right: 1px solid var(--border) !important;
    backdrop-filter: blur(10px);
}

.brand-wrapper {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 20px;
}

.logo-box {
    width: 46px;
    height: 46px;
    border-radius: 13px;
    display: grid;
    place-items: center;
    font-size: 24px;
    background: linear-gradient(135deg, #2e86ab, #7c5cff);
    box-shadow: 0 6px 20px rgba(124,92,255,.4);
}

.main-header {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
    margin: 0 !important;
    background: linear-gradient(90deg, #6cc5ec, #4ecdc4, #a99bff);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
}

.sub-header {
    color: var(--muted) !important;
    font-size: 0.82rem !important;
    margin: 3px 0 0 !important;
}

.stat-card-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}

.stat-card {
    flex: 1;
    min-width: 96px;
    padding: 10px 16px;
    border-radius: 12px;
    text-align: center;
    background: linear-gradient(180deg, rgba(28,34,48,.8), rgba(18,21,28,.8));
    border: 1px solid var(--border);
}

.stat-num {
    font-size: 1.5rem;
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(90deg, #4ecdc4, #6cc5ec);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-lbl {
    font-size: 0.66rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: var(--muted2);
    margin-top: 4px;
}

.plot-hero {
    background: linear-gradient(180deg, rgba(23,28,38,.7), rgba(15,18,25,.7));
    border: 1px solid var(--border2);
    border-radius: var(--radius);
    padding: 10px 14px;
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 12px;
}

.source-card {
    background: rgba(18,21,28,.6);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 13px 16px;
    margin-bottom: 10px;
    transition: 0.15s;
}

.source-card:hover {
    border-color: var(--accent2);
    transform: translateX(3px);
}
</style>
"""
