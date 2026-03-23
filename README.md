# Forestry data ingestion for DIRECTED project

## Data

The original data is available at https://met.boreas.hu/bakonyerdo/index.php.

Measurements are provided for about 30 different parameters at 11 stations with 10 minute intervals.

We currently ingest the following parameters:
 - Temperature at 2 m height in °C
 - Wind speed in m/s
 - Soil moisture at 10, 25, 50 and 70 cm depth in %

## Steps

Build the Docker image:

```shell
docker build . -t directed/forestry-data-ingestor:latest
```

Run the Docker image:

```shell
 docker run -e BUCKET_NAME="" -e BUCKET_KEY="" -e BUCKET_SECRET="" directed/forestry-data-ingestor:latest
```

Be default, the script ingests data for the current month. Different months can be configured with the "DATES" 
environment parameter. Dates have to be provided in the format "YYYY-MM".
Multiple dates have to be separated with a comma, e.g. "2025-12,2026-01,2026-02".