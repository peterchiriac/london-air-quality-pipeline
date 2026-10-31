import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the Gold layer
con = duckdb.connect("air_quality.duckdb", read_only=True)

df = con.execute("""
    SELECT
        date,
        site_code,
        species_code,
        CASE
            WHEN reliability_status = 'reliable'
            THEN avg_concentration
            ELSE NULL
        END AS avg_concentration
    FROM daily_pollutant_averages
    WHERE site_code IN ('TH4', 'TH6')
      AND species_code IN ('NO2', 'O3')
    ORDER BY date
""").df()

con.close()

# Convert dates to Pandas datetime format
df["date"] = pd.to_datetime(df["date"])

# Separate the four station-pollutant combinations
th4_no2 = df[(df["site_code"] == "TH4") & (df["species_code"] == "NO2")]
th6_no2 = df[(df["site_code"] == "TH6") & (df["species_code"] == "NO2")]

th4_o3 = df[(df["site_code"] == "TH4") & (df["species_code"] == "O3")]
th6_o3 = df[(df["site_code"] == "TH6") & (df["species_code"] == "O3")]

# Create a complete calendar so missing days appear as gaps
full_dates = pd.date_range(
    start=df["date"].min(),
    end=df["date"].max(),
    freq="D"
)

th4_no2 = th4_no2.set_index("date").reindex(full_dates)
th6_no2 = th6_no2.set_index("date").reindex(full_dates)

th4_o3 = th4_o3.set_index("date").reindex(full_dates)
th6_o3 = th6_o3.set_index("date").reindex(full_dates)

# Create two vertically stacked charts
fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(12, 9),
    sharex=True
)

# Chart 1: Nitrogen dioxide
ax1.plot(
    th4_no2.index,
    th4_no2["avg_concentration"],
    label="Blackwall (Roadside)"
)

ax1.plot(
    th6_no2.index,
    th6_no2["avg_concentration"],
    label="Millwall Park (Urban Background)"
)

ax1.set_title("Daily NO₂ Concentrations")
ax1.set_ylabel("Concentration (µg/m³)")
ax1.legend()
ax1.grid(True, alpha=0.3)

# Chart 2: Ozone
ax2.plot(
    th4_o3.index,
    th4_o3["avg_concentration"],
    label="Blackwall (Roadside)"
)

ax2.plot(
    th6_o3.index,
    th6_o3["avg_concentration"],
    label="Millwall Park (Urban Background)"
)

ax2.set_title("Daily O₃ Concentrations")
ax2.set_ylabel("Concentration (µg/m³)")
ax2.set_xlabel("Date")
ax2.legend()
ax2.grid(True, alpha=0.3)

# Overall title
fig.suptitle(
    "Tower Hamlets Air Quality: Roadside vs Urban Background",
    fontsize=15
)

fig.tight_layout()

# Save the visualisation
plt.savefig(
    "air_quality_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()