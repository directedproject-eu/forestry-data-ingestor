# Forestry data ingestion for DIRECTED project

## Data

The original data is available at https://met.boreas.hu/bakonyerdo/index.php.

Measurements are provided for about 30 different parameters at 11 stations with 10 minute intervals.

## Steps

Build the Docker image:

```shell
docker build . -t directed/forestry-data-ingestor:latest
```

Run the Docker image:

```shell
 docker run -e BUCKET_NAME="" -e BUCKET_KEY="" -e BUCKET_SECRET="" directed/forestry-data-ingestor:latest
```
