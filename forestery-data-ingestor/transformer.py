import pandas as pd
import os
import json

def clean_and_simplify_forestry_data(df, old_cols, new_cols):

    df.columns = df.columns.str.replace('\n', ' in ')

    rename_map = dict(zip(old_cols, new_cols))
    df = df.rename(columns=rename_map)

    df = df[df.columns.intersection(new_cols)].copy()

    # Format time
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"]).dt.strftime('%Y-%m-%dT%H:%M:%S')

    return df


def to_json_structure(df):
    return df.to_dict(orient='records')


import json
import os


def append_and_save_json(new_data_list, folder_name="data", file_name="station_data.json"):
    # 1. Construct path
    os.makedirs(folder_name, exist_ok=True)
    file_path = os.path.join(folder_name, file_name)

    existing_data = []

    # 2. Load existing data (if the file exists)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {file_name} was empty or corrupted. Starting fresh.")
            existing_data = []

    # 3. Create a set of existing timestamps for fast lookup
    existing_timestamps = {entry['time'] for entry in existing_data}

    # 4. Append ONLY new unique records
    added_count = 0
    for row in new_data_list:
        if row['time'] not in existing_timestamps:
            existing_data.append(row)
            added_count += 1


    # 5. Save back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4)

    print(f"Updated {file_name}: Added {added_count} new records. (Total: {len(existing_data)})")