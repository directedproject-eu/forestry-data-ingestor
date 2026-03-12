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
