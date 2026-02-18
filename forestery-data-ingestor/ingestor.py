import requests
import pandas as pd
import io
import transformer
import os
from dotenv import load_dotenv
from datetime import datetime

def get_data(url):

    response = requests.get(url)

    if response.status_code == 200:
        virtual_file = io.BytesIO(response.content)
        return pd.read_excel(virtual_file, engine='openpyxl', sheet_name=None)
    else:
        print(f"Failed to download. Status code: {response.status_code}")


def is_valid_format(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m")
        return True
    except ValueError:
        return False


if __name__ == "__main__":

    load_dotenv()
    #bucket_endpoint = os.getenv("BUCKET_ENDPOINT", "https://obs.eu-de.otc.t-systems.com")
    #bucket_name = os.getenv("BUCKET_NAME")
    #bucket_base_path = os.getenv("BUCKET_BASE_PATH", "data/dmi/forecasts")
    #bucket_key = os.getenv("BUCKET_KEY")
    #bucket_secret = os.getenv("BUCKET_SECRET")
    #upload = os.getenv("UPLOAD_TO_BUCKET", "true").lower() == "true"

    month = os.getenv("month", datetime.now().strftime("%Y-%m"))
    file_name = os.getenv("file_name", "Bakonyerd%c5%91")

    if not is_valid_format(month):
        raise ValueError(f"Invalid date format: '{month}'. The expected format is 'YYYY-MM' (e.g., '2026-02').")
    url = f"https://met.boreas.hu/bakonyerdo/xls_tables/{file_name}-{month}.xlsx"
    print(url)
    df = get_data(url=url)
    stations = list(df.keys())

    for station in stations:
        clean_df = transformer.clean_and_simplify_forestry_data(
            df=df[station],
            old_cols=["Mérés ideje", "T2m in °C", "Szél in m/s", "VWC1 in %", "VWC2 in %", "VWC3 in %",  "VWC4 in %"],
            new_cols=["time", "temperature", "wind_speed", "soil_moisture_10cm", "soil_moisture_25cm", "soil_moisture_50cm", "soil_moisture_70cm"],
        )

        json_data = transformer.to_json_structure(clean_df)

        transformer.append_and_save_json(json_data, file_name=station + ".json")




