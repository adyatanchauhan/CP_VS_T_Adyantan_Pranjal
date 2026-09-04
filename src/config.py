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
    "MatWeb / ASM Handbook": "https://www.matweb.com/",
    "Engineering handbook": "https://webbook.nist.gov/chemistry/",
}

CUSTOM_CSS = """
<style>
.main-header {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #1e3a5f, #2e86ab);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.sub-header { color: #555; font-size: 0.85rem; margin-bottom: 0.5rem; }
.source-card {
    background: #f8fafc;
    border: 1px solid #dde4ec;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.warning-box {
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 8px 0;
}
.plot-hero {
    background: linear-gradient(180deg, #12151c 0%, #0d1117 100%);
    border: 2px solid #2e86ab;
    border-radius: 12px;
    padding: 8px 12px 4px 12px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.45);
    margin-bottom: 12px;
}
.plot-hero-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e8edf5;
    margin: 4px 0 8px 4px;
}
</style>
"""
