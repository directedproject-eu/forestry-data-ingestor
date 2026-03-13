import io
import logging
import os
import sys
from datetime import datetime

import pandas as pd
import requests
import transformer
from s3fs import S3FileSystem

# Necessary to avoid writing checksums into the COGs when uploading them to the bucket (cf. https://github.com/boto/boto3/issues/4435)
os.environ["AWS_REQUEST_CHECKSUM_CALCULATION"] = "when_required"
os.environ["AWS_RESPONSE_CHECKSUM_VALIDATION"] = "when_required"

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="[%(asctime)s | %(name)s::%(module)s.py:%(lineno)d | %(process)d] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_data(url: str):
    logger.info(f"Download data from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        virtual_file = io.BytesIO(response.content)
        return pd.read_excel(virtual_file, engine="openpyxl", sheet_name=None)
    else:
        logger.error(f"Failed to download. Status code: {response.status_code}")


def is_valid_format(date_str: str):
    try:
        datetime.strptime(date_str, "%Y-%m")
        return True
    except ValueError as err:
        logger.error(err)
        return False


def download_from_bucket(
    local_file: str, bucket_file: str, endpoint_url: str, key: str, secret: str
):
    logger.info(f"Try to download {bucket_file} to {local_file}.")
    try:
        s3 = S3FileSystem(endpoint_url=endpoint_url, key=key, secret=secret)
        s3.get(bucket_file, local_file)
        logger.info("Download succeeded.")
    except FileNotFoundError:
        logger.info("Download failed.")
    except Exception:
        logger.info("Download failed.")


def upload_to_bucket(
    local_file: str, bucket_file: str, endpoint_url: str, key: str, secret: str
):
    logger.info(f"Try to upload {local_file} to {bucket_file}.")
    s3 = S3FileSystem(endpoint_url=endpoint_url, key=key, secret=secret)
    with open(local_file, "rb") as f:
        with s3.open(bucket_file, "wb") as s3_file:
            s3_file.write(f.read())
            logger.info("Upload succeeded.")


if __name__ == "__main__":
    # Configurable parameters
    bucket_endpoint = os.getenv(
        "BUCKET_ENDPOINT", "https://obs.eu-de.otc.t-systems.com"
    )
    bucket_name = os.getenv("BUCKET_NAME")
    bucket_base_path = os.getenv("BUCKET_BASE_PATH", "data/forestry")
    bucket_key = os.getenv("BUCKET_KEY")
    bucket_secret = os.getenv("BUCKET_SECRET")
    upload = os.getenv("UPLOAD_TO_BUCKET", "true").lower() == "true"
    source_file_base = os.getenv("SOURCE_FILE_BASE", "Bakonyerd%c5%91")
    year = os.getenv("YEAR", datetime.now().strftime("%Y"))
    month = os.getenv("MONTH", datetime.now().strftime("%m"))
    # Fixed parameters
    local_base_folder = "data"
    date = f"{year}-{month}"
    if not is_valid_format(date):
        msg = f"Invalid date format: '{date}'. The expected format is 'YYYY-MM' (e.g., '2026-02')."
        logger.error(msg)
        raise ValueError(msg)
    url = f"https://met.boreas.hu/bakonyerdo/xls_tables/{source_file_base}-{date}.xlsx"
    old_col_names = [
        "Mérés ideje",
        "T2m in °C",
        "Szél in m/s",
        "VWC1 in %",
        "VWC2 in %",
        "VWC3 in %",
        "VWC4 in %",
    ]
    new_col_names = [
        "time",
        "temperature",
        "wind_speed",
        "soil_moisture_10cm",
        "soil_moisture_25cm",
        "soil_moisture_50cm",
        "soil_moisture_70cm",
    ]

    df = get_data(url=url)
    stations = list(df.keys())
    for station in stations:
        clean_df = transformer.clean_and_simplify_forestry_data(
            df=df[station],
            old_cols=old_col_names,
            new_cols=new_col_names,
        )
        station_normalized = transformer.normalize_string(station)
        local_folder_name = os.path.join(local_base_folder, station_normalized)
        os.makedirs(local_folder_name, exist_ok=True)
        bucket_path = f"{bucket_name}/{bucket_base_path}/{station_normalized}"
        for param in new_col_names[1:]:
            local_file_name = os.path.join(local_folder_name, f"{param}.json")
            bucket_file_name = f"{bucket_path}/{param}.json"
            download_from_bucket(
                local_file_name,
                bucket_file_name,
                bucket_endpoint,
                bucket_key,
                bucket_secret,
            )
            json_data = transformer.to_json_structure(clean_df[["time", param]])
            transformer.append_and_save_json(json_data, local_file_name)
            if upload:
                upload_to_bucket(
                    local_file_name,
                    bucket_file_name,
                    bucket_endpoint,
                    bucket_key,
                    bucket_secret,
                )
