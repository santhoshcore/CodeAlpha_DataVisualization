"""
CodeAlpha Data Analytics Internship - Task 3: Data Visualization
Topic   : Global CO2 emissions - who emits, how much, and from what? (1950-2024)
Dataset : Our World in Data "CO2 and Greenhouse Gas Emissions" (owid/co2-data on GitHub)
Tools   : pandas, matplotlib, seaborn
Goal    : Turn raw data into clear visuals and a data story that supports
          climate-policy decisions.

Run:  python visualize.py
Output: PNG charts in ./charts/ (including a summary dashboard)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns

# ----------------------------------------------------------------------
# 1. Setup
# ----------------------------------------------------------------------
DATA_URL = ("https://raw.githubusercontent.com/owid/co2-data/"
            "master/owid-co2-data.csv")
DATA_FILE = os.path.join("data", "owid-co2-data.csv")
OUT_DIR = "charts"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook", font_scale=1.05)
C = {"dark": "#264653", "teal": "#2A9D8F", "sand": "#E9C46A",
     "orange": "#F4A261", "red": "#E76F51", "grey": "#8D99AE"}
COUNTRY_COLORS = {"China": C["red"], "United States": C["dark"],
                  "India": C["orange"], "EU-27": C["teal"]}


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", path)


def clean_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)


# ----------------------------------------------------------------------
# 2. Load and prepare data
# ----------------------------------------------------------------------
if os.path.exists(DATA_FILE):
    raw = pd.read_csv(DATA_FILE)
else:
    raw = pd.read_csv(DATA_URL)
    raw.to_csv(DATA_FILE, index=False)

LAST = int(raw["year"].max())          # latest year in the data (2024)
PREV = LAST - 1

# Real countries have an ISO code (aggregates like 'World', 'Asia' do not;
# OWID uses 'OWID_...' codes for a few special regions, so drop those too)
countries = raw[raw["iso_code"].notna()
                & ~raw["iso_code"].astype(str).str.startswith("OWID")].copy()
world = raw[raw["country"] == "World"].set_index("year")
eu = raw[raw["country"] == "European Union (27)"].set_index("year")

print(f"Rows: {raw.shape[0]:,}  Columns: {raw.shape[1]}  Years: {raw.year.min()}-{LAST}")
print("Countries with CO2 data in", LAST, ":",
      countries[countries.year == LAST]["co2"].notna().sum())

latest = countries[countries["year"] == LAST].dropna(subset=["co2"])

# ----------------------------------------------------------------------
# 3. Individual charts
# ----------------------------------------------------------------------

# 3.1 World emissions over time
w = world.loc[1950:LAST, "co2"] / 1000  # Gt
fig, ax = plt.subplots(figsize=(9, 5))
ax.fill_between(w.index, w.values, color=C["teal"], alpha=0.25)
ax.plot(w.index, w.values, color=C["teal"], lw=2.5)
ax.annotate("2020: COVID-19 dip", xy=(2020, w.loc[2020]),
            xytext=(1999, w.loc[2020] - 9),
            arrowprops=dict(arrowstyle="->", color=C["dark"]), color=C["dark"])
ax.annotate(f"{LAST}: {w.loc[LAST]:.1f} Gt", xy=(LAST, w.loc[LAST]),
            xytext=(LAST - 12, w.loc[LAST] + 3), color=C["dark"],
            fontweight="bold")
ax.set(title=f"Global CO₂ emissions are at a record high: "
             f"{w.loc[LAST]:.1f} billion tonnes in {LAST}",
       xlabel="", ylabel="Billion tonnes of CO₂ per year")
ax.set_ylim(0, w.max() + 6)
clean_axes(ax)
save(fig, "01_world_emissions_trend.png")

# 3.2 Top 10 emitters
top10 = latest.nlargest(10, "co2").sort_values("co2")
fig, ax = plt.subplots(figsize=(9, 5.5))
colors = [C["red"] if c == "China" else C["dark"] for c in top10["country"]]
ax.barh(top10["country"], top10["co2"] / 1000, color=colors)
for y, v in enumerate(top10["co2"] / 1000):
    ax.text(v + 0.1, y, f"{v:.2f} Gt", va="center", fontsize=10)
top2_share = latest.nlargest(2, "co2")["co2"].sum() / world.loc[LAST, "co2"] * 100
ax.set(title=f"China and the US emit about {top2_share:.0f}% of the world's CO₂",
       xlabel="Billion tonnes of CO₂", ylabel="")
ax.grid(axis="y", visible=False)
ax.set_xlim(0, top10["co2"].max() / 1000 * 1.15)
clean_axes(ax)
save(fig, "02_top10_emitters.png")

# 3.3 Per capita vs total (bubble) - same total, very different per person
top20 = latest.nlargest(20, "co2")
fig, ax = plt.subplots(figsize=(9.5, 6))
ax.scatter(top20["co2_per_capita"], top20["co2"] / 1000,
           s=top20["population"] / 1e6 * 2.2, color=C["teal"], alpha=0.6,
           edgecolor="white")
for _, r in top20.iterrows():
    off = (5, -13) if r["country"] == "Italy" else (5, 5)
    ax.annotate(r["country"], (r["co2_per_capita"], r["co2"] / 1000),
                xytext=off, textcoords="offset points", fontsize=8.5)
ax.set_yscale("log")
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
ax.set(title="Top 20 emitters: total vs per person (bubble size = population)",
       xlabel="CO₂ per person (tonnes per year)",
       ylabel="Total CO₂ (billion tonnes, log scale)")
clean_axes(ax)
save(fig, "03_total_vs_per_capita.png")

# 3.4 Emissions by source (stacked area)
src_cols = {"coal_co2": "Coal", "oil_co2": "Oil", "gas_co2": "Gas",
            "cement_co2": "Cement", "flaring_co2": "Flaring"}
src = world.loc[1950:LAST, list(src_cols)].rename(columns=src_cols) / 1000
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.stackplot(src.index, src.T.values, labels=src.columns,
             colors=[C["dark"], C["red"], C["sand"], C["grey"], C["orange"]],
             alpha=0.9)
ax.legend(loc="upper left", frameon=False)
share = src.loc[LAST] / src.loc[LAST].sum() * 100
ax.set(title=f"Coal, oil and gas still produce about "
             f"{share[['Coal','Oil','Gas']].sum():.0f}% of fossil CO₂",
       xlabel="", ylabel="Billion tonnes of CO₂")
clean_axes(ax)
save(fig, "04_emissions_by_source.png")

# 3.5 Trends for the big emitters since 1990
tr = pd.DataFrame({
    "China": countries[countries.country == "China"].set_index("year")["co2"],
    "United States": countries[countries.country == "United States"].set_index("year")["co2"],
    "India": countries[countries.country == "India"].set_index("year")["co2"],
    "EU-27": eu["co2"],
}).loc[1990:LAST] / 1000
fig, ax = plt.subplots(figsize=(9, 5.5))
for col in tr.columns:
    ax.plot(tr.index, tr[col], lw=2.8, color=COUNTRY_COLORS[col])
    ax.text(LAST + 0.4, tr[col].iloc[-1], col, color=COUNTRY_COLORS[col],
            va="center", fontweight="bold")
ax.set_xlim(1990, LAST + 6)
ax.set_xticks(range(1990, LAST + 1, 5))
ch = tr["China"]
ax.set(title=f"China's emissions grew {ch.loc[LAST] / ch.loc[1990]:.1f}x since 1990 "
             f"while the EU's fell",
       xlabel="", ylabel="Billion tonnes of CO₂")
clean_axes(ax)
save(fig, "05_big_emitters_trend.png")

# 3.6 Income vs per-capita emissions (latest year with GDP data)
gdp_year = int(countries.dropna(subset=["gdp", "co2_per_capita"])["year"].max())
g = countries[(countries.year == gdp_year)].dropna(
    subset=["gdp", "co2_per_capita", "population"]).copy()
g["gdp_per_capita"] = g["gdp"] / g["population"]
corr = np.corrcoef(np.log10(g["gdp_per_capita"]), np.log10(g["co2_per_capita"]))[0, 1]
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.scatter(g["gdp_per_capita"], g["co2_per_capita"], s=45,
           color=C["teal"], alpha=0.6, edgecolor="white")
slope, intercept = np.polyfit(np.log10(g["gdp_per_capita"]),
                              np.log10(g["co2_per_capita"]), 1)
xs = np.logspace(np.log10(g["gdp_per_capita"].min()),
                 np.log10(g["gdp_per_capita"].max()), 100)
ax.plot(xs, 10 ** (intercept + slope * np.log10(xs)),
        color=C["dark"], lw=2, ls="--")
ax.set_xscale("log")
ax.set_yscale("log")
for name in ["United States", "China", "India", "Qatar", "Germany", "Nigeria"]:
    r = g[g.country == name]
    if len(r):
        ax.annotate(name, (r["gdp_per_capita"].iloc[0], r["co2_per_capita"].iloc[0]),
                    xytext=(5, 5), textcoords="offset points", fontsize=9)
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
ax.set(title=f"Richer countries emit more per person (r = {corr:.2f} on log scales, {gdp_year})",
       xlabel="GDP per person (log scale)",
       ylabel="CO₂ per person, tonnes (log scale)")
clean_axes(ax)
save(fig, "06_income_vs_emissions.png")

# 3.7 Distribution of per-capita emissions
fig, ax = plt.subplots(figsize=(9, 5))
pc = latest["co2_per_capita"].dropna()
sns.histplot(pc, bins=30, color=C["dark"], ax=ax)
ax.axvline(pc.median(), color=C["red"], ls="--",
           label=f"Median country = {pc.median():.1f} t")
ax.axvline(world.loc[LAST, "co2_per_capita"], color=C["teal"], ls="--",
           label=f"World average = {world.loc[LAST, 'co2_per_capita']:.1f} t")
ax.legend(frameon=False)
ax.set(title="Most countries emit under 6 tonnes per person; a few emit far more",
       xlabel=f"CO₂ per person in {LAST} (tonnes)", ylabel="Number of countries")
clean_axes(ax)
save(fig, "07_per_capita_distribution.png")

# ----------------------------------------------------------------------
# 4. Dashboard (one-page summary)
# ----------------------------------------------------------------------
growth = (world.loc[LAST, "co2"] / world.loc[PREV, "co2"] - 1) * 100
top1 = latest.nlargest(1, "co2").iloc[0]
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 4, height_ratios=[0.5, 1.6, 1.6], hspace=0.55,
                      wspace=0.4)
fig.suptitle(f"Global CO₂ Emissions Dashboard ({LAST})", fontsize=22,
             fontweight="bold", y=0.98)

kpis = [("World CO₂ emissions", f"{world.loc[LAST, 'co2'] / 1000:.1f} Gt"),
        (f"Change vs {PREV}", f"{growth:+.1f}%"),
        (f"Largest emitter: {top1['country']}",
         f"{top1['co2'] / world.loc[LAST, 'co2'] * 100:.0f}% of world"),
        ("World per person", f"{world.loc[LAST, 'co2_per_capita']:.1f} t")]
for i, (label, value) in enumerate(kpis):
    ax = fig.add_subplot(gs[0, i])
    ax.axis("off")
    ax.text(0.5, 0.62, value, ha="center", fontsize=26,
            fontweight="bold", color=C["dark"])
    ax.text(0.5, 0.15, label, ha="center", fontsize=12, color="grey")

ax = fig.add_subplot(gs[1, 0:2])
ax.fill_between(w.index, w.values, color=C["teal"], alpha=0.25)
ax.plot(w.index, w.values, color=C["teal"], lw=2.5)
ax.set(title="World emissions, 1950 to now", ylabel="Gt CO₂")
clean_axes(ax)

ax = fig.add_subplot(gs[1, 2:4])
ax.barh(top10["country"], top10["co2"] / 1000, color=colors)
ax.set(title=f"Top 10 emitters, {LAST}", xlabel="Gt CO₂")
ax.grid(axis="y", visible=False)
clean_axes(ax)

ax = fig.add_subplot(gs[2, 0:2])
for col in tr.columns:
    ax.plot(tr.index, tr[col], lw=2.5, color=COUNTRY_COLORS[col], label=col)
ax.legend(frameon=False, loc="upper left", ncol=2)
ax.set(title="Big emitters since 1990", ylabel="Gt CO₂")
clean_axes(ax)

ax = fig.add_subplot(gs[2, 2:4])
ax.stackplot(src.index, src.T.values, labels=src.columns,
             colors=[C["dark"], C["red"], C["sand"], C["grey"], C["orange"]])
ax.legend(frameon=False, loc="upper left", fontsize=9)
ax.set(title="Emissions by source", ylabel="Gt CO₂")
clean_axes(ax)

save(fig, "00_dashboard.png")

# ----------------------------------------------------------------------
# 5. Key numbers for the written insights
# ----------------------------------------------------------------------
print("\n=== KEY INSIGHTS ===")
print(f"World CO2 {LAST}: {world.loc[LAST,'co2']/1000:.2f} Gt ({growth:+.2f}% vs {PREV})")
print(f"World CO2 2019/2020/2021: {world.loc[2019,'co2']/1000:.2f} / "
      f"{world.loc[2020,'co2']/1000:.2f} / {world.loc[2021,'co2']/1000:.2f} Gt")
print(f"World CO2 1990 -> {LAST}: {world.loc[1990,'co2']/1000:.1f} -> "
      f"{world.loc[LAST,'co2']/1000:.1f} Gt")
print("Top 5 share of world %:\n",
      (latest.nlargest(5, 'co2').set_index('country')['co2']
       / world.loc[LAST, 'co2'] * 100).round(1).to_string())
print("Per capita 2024:\n", latest.set_index("country").loc[
    ["United States", "China", "India", "Saudi Arabia"], "co2_per_capita"].to_string())
print("1990 -> latest (Gt):\n", tr.loc[[1990, LAST]].round(2).to_string())
print("EU change %:", round((tr['EU-27'].loc[LAST] / tr['EU-27'].loc[1990] - 1) * 100, 1))
print("Source shares %:\n", share.round(1).to_string())
print(f"GDP/emissions log correlation ({gdp_year}): {corr:.2f}, n={len(g)}")
print(f"Median country per capita: {pc.median():.2f} t, share under 6t: "
      f"{(pc < 6).mean() * 100:.0f}%")
