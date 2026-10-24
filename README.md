# CodeAlpha_DataVisualization

**CodeAlpha Data Analytics Internship, Task 3: Data Visualization**

**Topic: Global CO₂ emissions: who emits, how much, and from what? (1950-2024)**

Turning real, up-to-date climate data into charts and a one-page dashboard that support decision-making.

## Dataset
[Our World in Data: CO₂ and Greenhouse Gas Emissions](https://github.com/owid/co2-data) (`owid/co2-data` on GitHub, licensed CC BY). It has 50,411 rows and 79 columns covering 1750-2024, with 215 countries reporting CO₂ in 2024. The script downloads it automatically on first run and caches it in `data/`.

Real countries are separated from aggregates ("World", "Asia", etc.) using the ISO code column, so totals are never double counted.

## Questions I set out to answer
1. How have global emissions changed over time, and where are they now?
2. Which countries emit the most?
3. Is the picture different per person than in total?
4. Which fuels cause the emissions?
5. How have the biggest emitters changed since 1990?
6. How are income and emissions related?

## Tools
Python, pandas, numpy, matplotlib, seaborn

## Project structure
```
CodeAlpha_DataVisualization/
├── README.md
├── visualize.py              # data loading, cleaning, all chart code
├── CO2_dashboard_v2.html     # interactive dashboard (open in a browser)
├── charts/                   # 8 static PNG charts incl. 00_dashboard.png
├── powerbi_csv/              # clean CSV files ready for Power BI
│   ├── country_year.csv
│   ├── world_by_year.csv
│   └── country_latest_2024.csv
└── LinkedIn_video_script.md
```
(`data/` is created automatically on the first run of `visualize.py`.)

## Interactive dashboard
`CO2_dashboard_v2.html` is a Power BI-style dashboard. Download it and double-click to open it in Chrome (internet needed for the chart library).
- Sidebar pages: **Overview**, **Countries** (searchable, sortable table), **Fuels & Income**
- Filters: year (1990-2024) and country
- KPI cards, emissions trend, top 10 emitters, world fuel-mix donut, region and top-5 tables, per-person segmentation and a key-insights strip
- Cross-filtering: click a bar or a table row to switch the whole dashboard to that country
- Light and dark mode

## Power BI data
The `powerbi_csv/` folder holds cleaned tables that can be loaded in Power BI Desktop with Get data > Text/CSV:
- `country_year.csv`: one row per country per year since 1950 (CO₂, per person, population, GDP, fuel breakdown)
- `world_by_year.csv`: world totals per year
- `country_latest_2024.csv`: one row per country for 2024 with share of world total

## How to run
```bash
pip install pandas numpy matplotlib seaborn
python visualize.py
```
Charts are saved to the `charts/` folder.

## Visualizations
| File | Chart | What it shows |
|---|---|---|
| `00_dashboard.png` | Dashboard | KPIs + four key charts on one page |
| `01_world_emissions_trend.png` | Area/line | Record 38.6 Gt in 2024, COVID dip in 2020 |
| `02_top10_emitters.png` | Horizontal bar | China and the US dominate |
| `03_total_vs_per_capita.png` | Bubble chart | Total vs per-person emissions, sized by population |
| `04_emissions_by_source.png` | Stacked area | Coal, oil, gas, cement, flaring |
| `05_big_emitters_trend.png` | Line chart | China, US, India, EU-27 since 1990 |
| `06_income_vs_emissions.png` | Log-log scatter | GDP per person vs CO₂ per person |
| `07_per_capita_distribution.png` | Histogram | How per-person emissions are spread across countries |

## Key insights
- **Global emissions hit a record 38.6 billion tonnes in 2024**, up 1.3% on 2023 and about 70% above 1990 (22.7 Gt). The only recent fall was 2020 (37.1 to 35.2 Gt), which was quickly reversed.
- **China emits 32% of the world's CO₂, the US 13% and India 8%.** China and the US together account for about 44%.
- **Per person, the ranking flips.** The US emits 14.2 t per person, China 8.7 t and India 2.2 t, against a world average of 4.7 t. Saudi Arabia reaches 20.4 t.
- **Since 1990 China's emissions grew 4.9x (2.5 to 12.3 Gt) and India's 5.5x, while the US fell slightly (5.1 to 4.9 Gt) and the EU-27 fell 37% (3.9 to 2.4 Gt).**
- **Coal, oil and gas still cause about 95% of fossil CO₂** (coal 41%, oil 33%, gas 21%, cement 4%, flaring 1%).
- **Income and emissions are tightly linked:** across 164 countries in 2022, GDP per person and CO₂ per person have a correlation of 0.91 on log scales.
- **Three quarters of countries emit under 6 tonnes per person**; the median country emits 3.2 t.

## Recommendations
- Policy focused only on total emissions would miss per-person and historical responsibility; reports should show both views.
- Coal is the single largest source, so coal phase-down offers the biggest reduction per unit of effort.
- The EU's 37% fall since 1990 shows that economies can decouple emissions from growth, which is a useful model for fast-growing emitters.

## Limitations
- These are territorial emissions (produced within a country's borders). Emissions embedded in imported goods are not counted here, which flatters importers and penalises exporters such as China.
- CO₂ only; methane and other greenhouse gases are not included in these charts.
- GDP data is not yet available for 2024, so chart 06 uses 2022.
- Correlation does not prove causation (chart 06).

## Author
Santhosh | CodeAlpha Data Analytics Intern
