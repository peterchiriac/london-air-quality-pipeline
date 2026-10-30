# London Pollution Fingerprints

## Project Overview

London Pollution Fingerprints is a reproducible data pipeline that collects, validates, stores and transforms historical air quality measurements from the London Air Quality Network (LAQN).

The project aims to enable environmental researchers to explore how two pollutants, nitrogen dioxide (NO₂) and ozone (O₃), behave over time across roadside and urban-background monitoring stations.

## Data Source

Data is retrieved from the London Air Quality Network (LAQN) API, maintained by the Environmental Research Group at Imperial College London.

The pipeline currently collects hourly measurements of two pollutants:

- **Nitrogen dioxide (NO₂):** Commonly associated with combustion processes, particularly road traffic.
- **Ozone (O₃):** A secondary pollutant formed through atmospheric chemical reactions.

The initial implementation uses monitoring station BQ7. Support for additional roadside and urban-background stations is in development.

## Pipeline Architecture

The project follows a three-layer Medallion architecture to separate data ingestion, transformation and analysis.

### Bronze — Raw Data Ingestion

- Retrieves historical observations from the LAQN API.
- Preserves the original API responses as JSON files.
- Determines the starting point for incremental ingestion independently for each station and pollutant, using the latest stored measurement timestamp.
- Includes a three-day overlap to capture late-arriving observations and corrections.
- Performs timestamp coverage checks to identify potentially incomplete responses.

### Silver — Structured Data

- Transforms raw JSON observations into structured records stored in DuckDB.
- Uses a composite primary key consisting of station, pollutant and measurement timestamp.
- Prevents duplicate observations during repeated ingestion.
- Updates existing observations when valid measurements are received.
- Preserves missing and negative measurements with explicit quality flags.
- Processes Bronze files chronologically by file modification time.
- Station metadata ingestion has been implemented and is undergoing testing. The pollutant metadata table remains in development.


### Gold — Analysis-Ready Data

The current Gold layer produces daily average pollutant concentrations for each station and pollutant, using only measurements classified as valid.

Further analysis will explore differences in pollutant concentrations over time and across monitoring station types.

## Data Quality

The pipeline includes several mechanisms to improve data reliability:

- **HTTP validation:** Checks for unsuccessful API requests.
- **Timestamp coverage:** Compares returned observations against expected hourly timestamps.
- **Missing values:** Retained and classified as `missing`.
- **Negative values:** Retained and classified as `negative`.
- **Duplicate prevention:** Enforced through a composite primary key.
- **Correction handling:** Valid incoming measurements can update existing records, while missing or negative incoming measurements cannot overwrite existing records.

The three-day overlap is a design choice rather than a guarantee that all late-arriving corrections will be captured.

## How to Run

The pipeline consists of four Python scripts.

1. `init_db.py` - Initializes the DuckDB database and creates the required tables if they do not already exist.
2. `fetch_air_quality.py` — Retrieves and saves API observations to Bronze.
3. `silver.py` — Transforms saved observations and loads them into DuckDB.
4. `gold.py` — Generates daily pollutant averages.

### Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Initialize the database

```bash
python init_db.py
```

Run this once before executing the pipeline for the first time. It is safe to rerun because existing tables and data are preserved.

### Running the Pipeline

Run the scripts in the following order:

```bash
python fetch_air_quality.py
python silver.py
python gold.py
```

## Development Status

The historical and incremental ingestion pipeline is operational for NO₂ and O₃ at station BQ7.

The remaining development work includes:

- Testing station metadata ingestion and adding pollutant metadata.
- Expanding ingestion to multiple monitoring stations.
- Developing comparative analysis and visualisations.
- Finalising end-to-end testing and documentation.