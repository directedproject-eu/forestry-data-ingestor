import requests
import pandas as pd
import io
import transformer

def get_data(url):

    response = requests.get(url)

    if response.status_code == 200:
        virtual_file = io.BytesIO(response.content)
        return pd.read_excel(virtual_file, engine='openpyxl', sheet_name=None)
    else:
        print(f"Failed to download. Status code: {response.status_code}")


if __name__ == "__main__":
    df = get_data(url="https://met.boreas.hu/bakonyerdo/xls_tables/Bakonyerd%c5%91-2026-01.xlsx")
    stations = list(df.keys())

    for station in stations:
        clean_df = transformer.clean_and_simplify_forestry_data(
            df=df[station],
            old_cols=["Mérés ideje", "T2m in °C", "Szél in m/s"],
            new_cols=["time", "temperature", "wind_speed"]
        )

        json_data = transformer.to_json_structure(clean_df)

        # USE THE NEW FUNCTION HERE
        transformer.append_and_save_json(json_data, file_name=station + ".json")




