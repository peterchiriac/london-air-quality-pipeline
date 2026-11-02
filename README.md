# London Pollution Fingerprints

## What I built and who for

London Pollution Fingerprints is a data pipeline that collects, validates, stores and transforms historical air quality measurements from the London Air Quality Network (LAQN).

The project enables environmental researchers to explore how nitrogen dioxide (NO₂) and ozone (O₃) behave over time at two monitoring stations in Tower Hamlets: Blackwall, a roadside station, and Millwall Park, an urban-background station.

This first version helps researchers explore the relationship between NO₂ and O₃ across different monitoring environments, identify patterns in their concentrations over time, and generate hypotheses for further investigation.

## The data

### Data Source Acknowledgement

This information has been obtained from the Environmental Research Group of Imperial College London (https://www.imperial.ac.uk/school-public-health/environmental-research-group/), using data from the London Air Quality Network (https://www.londonair.org.uk). This information is licensed under the terms of the Open Government Licence.

Data is retrieved from the London Air Quality Network (LAQN) API, maintained by the Environmental Research Group at Imperial College London.

The pipeline collects hourly measurements of two pollutants, expressed in micrograms per cubic metre (µg/m³):

* Nitrogen dioxide (NO₂): A pollutant commonly associated with combustion processes, particularly road traffic.
* Ozone (O₃): A secondary pollutant formed through atmospheric chemical reactions involving other pollutants and sunlight.

Measurements are collected from two monitoring stations in Tower Hamlets:

* TH4 — Blackwall: Roadside monitoring station.
* TH6 — Millwall Park: Urban-background monitoring station.

I selected two stations within the same borough to make the comparison between monitoring environments more focused. Although local conditions can still differ, their geographical proximity helps reduce some variation in broader environmental conditions.

This allows the project to explore whether the relationship between NO₂ and O₃ differs between roadside and urban-background environments.

The historical dataset begins on 1 April 2026 and is extended through subsequent pipeline runs as new observations become available.

## How it works

The project follows a three-layer Medallion architecture to separate data ingestion, transformation and analysis.

### Bronze — Raw Data Ingestion

* Retrieves historical observations from the LAQN API and preserves the original responses as JSON files.
* Supports incremental ingestion by identifying the latest stored timestamp for each station and pollutant.
* Includes a three-day overlap to capture late-arriving observations and corrections.
* Performs timestamp coverage checks to identify potentially incomplete API responses.

### Silver — Structured Data

* Transforms raw JSON observations into structured records stored in DuckDB.
* Uses three related tables: sites (monitoring sites metadata), pollutants (pollutant metadata and units) and readings (hourly measurements).
* Links readings to sites and pollutants through foreign keys.
* Enforces a composite primary key (site_code, species_code, measurement_timestamp) to prevent duplicate observations.
* Supports idempotent loading: repeated runs do not create duplicates, while valid incoming observations can update existing values.
* Preserves missing and negative measurements with explicit quality flags.
* Processes Bronze files by modification time, oldest first, so newer valid observations take precedence.


### Data Quality

The pipeline includes several mechanisms to improve data reliability:

- **HTTP validation:** Checks for unsuccessful API requests.
- **Timestamp coverage:** Compares returned observations against expected hourly timestamps.
- **Missing values:** Retained and classified as `missing`.
- **Negative values:** Retained and classified as `negative`.
- **Duplicate prevention:** Enforced through a composite primary key.
- **Correction handling:** Valid incoming measurements can update existing records, while missing or negative incoming measurements cannot overwrite existing records. Consequently, a previously valid measurement that is subsequently invalidated by the source will remain unchanged in Silver.

The three-day overlap is a design choice rather than a guarantee that all late-arriving corrections will be captured.

### Gold — Analysis-Ready Data

* Calculates daily average concentrations using only valid hourly measurements.
* Measures daily completeness against 24 expected hourly observations.
* Classifies days with at least 18 valid hours (75%) as reliable; otherwise, they are incomplete.

### Visualisation

* Compares daily NO₂ and O₃ concentrations at Blackwall (TH4, roadside) and Millwall Park (TH6, urban background).
* Displays incomplete or unreliable days as gaps rather than potentially misleading averages.
* Uses a scatter plot to explore the relationship between NO₂ and O₃ within each site and compare pollutant profiles across the two monitoring environments.

### Data Model Limitations - What it makes difficult

* Station metadata: Historical changes to station locations or classifications are not preserved.
* Measurement revisions: Silver retains the latest accepted measurement rather than a history of corrections. Earlier observations may still be recoverable from Bronze.
* External factors: Weather and traffic data are not included, limiting investigations into factors associated with pollutant concentrations.



## How to run it

The pipeline consists of five Python scripts.

1. `init_db.py` - Initializes the DuckDB database and creates the required tables if they do not already exist.
2. `fetch_air_quality.py` — Retrieves and saves API observations to Bronze.
3. `silver.py` — Transforms saved observations and loads them into DuckDB.
4. `gold.py` — Generates daily pollutant averages.
5. `visualise.py` — Generates a chart comparing daily NO₂ and O₃ concentrations across the two monitoring stations, displaying incomplete days as gaps.

The repository includes the collected historical data in Bronze and a DuckDB database containing the processed measurements. Running the pipeline again retrieves recent observations and updates the existing dataset without introducing duplicates.

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

Subsequent runs retrieve recent observations using a three-day overlap, insert new measurements and update existing records where valid corrections are available, without creating duplicates.

Run the scripts in the following order:

```bash
python fetch_air_quality.py
python silver.py
python gold.py
python visualise.py
```

## What I would do next

Given more development time, I would prioritise five improvements:

* Automated recovery: Identify missing hourly observations and retry requests where appropriate, while respecting API limits.
* Historical corrections: Periodically refresh older measurements to capture revisions outside the current three-day overlap.
* Improved data validation: Investigate instrument-specific rules for negative concentrations rather than automatically excluding them.
* Historical traceability: Track changes to site metadata and preserve previous versions of corrected measurements.
* More robust ingestion: Record API retrieval timestamps instead of relying on file modification times to determine processing order.


## Where AI helped

I used AI as a learning and development assistant throughout this project, particularly when working with unfamiliar data engineering concepts and implementation patterns.

AI helped me explore approaches to incremental ingestion, database modelling, idempotency, data validation and correction handling. It also assisted with generating and reviewing code, debugging errors, and identifying potential limitations in my design.

I used these interactions to develop my understanding of the pipeline, test its behaviour and evaluate engineering decisions.

The project was an opportunity to extend my existing Python and SQL knowledge while learning how to design and maintain a reproducible data pipeline.