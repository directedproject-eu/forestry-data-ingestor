import json
import logging
import os
import unicodedata

import pandas as pd

logger = logging.getLogger()


def clean_and_simplify_forestry_data(df: pd.DataFrame, old_cols: list[str], new_cols: list[str]) -> pd.DataFrame:
    df.columns = df.columns.str.replace('\n', ' in ')
    rename_map = dict(zip(old_cols, new_cols))
    df = df.rename(columns=rename_map)
    df = df[df.columns.intersection(new_cols)].copy()
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"]).dt.strftime('%Y-%m-%dT%H:%M:%S')
    return df


def normalize_string(sequence: str) -> str:
    # Decompose characters, e.g. é (NFKD = Normalization Form Compatibility Decomposition)
    normalized = unicodedata.normalize('NFKD', sequence)
    # Filter out non-spacing mark characters
    ascii_bytes = normalized.encode('ascii', 'ignore')
    # Decode back to string
    ascii_str = ascii_bytes.decode('ascii')
    return ascii_str.strip().replace(' ', '_').lower()


def to_json_structure(df: pd.DataFrame):
    return df.rename(columns={df.columns[-1]: "val"}).to_dict(orient='records')


def append_and_save_json(new_data_list: list, file_name: str):
    # Load existing data (if the file exists)
    existing_data = []
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Warning: {file_name} was empty or corrupted. Starting fresh.")
            existing_data = []
    existing_timestamps = {entry['time'] for entry in existing_data}

    # Append ONLY new unique records
    added_count = 0
    for row in new_data_list:
        if row['time'] not in existing_timestamps:
            existing_data.append(row)
            added_count += 1

    # Order by time
    existing_data = sorted(existing_data, key=lambda d: d['time'])

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4)

    logger.info(f"Updated {file_name}: Added {added_count} new records. (Total: {len(existing_data)})")
