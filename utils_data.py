import pandas as pd
import numpy as np


def clean_dataframe(df):
    # Replace hyphens with actual NaN values (true empty cells)
    df.replace(to_replace=r'^\s*-\s*$', value=np.nan, regex=True, inplace=True)
    # Aggressive whitespace scrubbing for critical columns
    for col in ["RoleClassLibName", "Name", "Parent"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', '', 'None'], np.nan)
    return df


def resolve_parent_id(df, child_lib, parent_name):
    if pd.isna(parent_name) or str(parent_name).strip() == 'nan' or not str(parent_name).strip():
        return None

    p_name = str(parent_name).strip()
    # Check if parent exists in the same library
    same_lib_match = df[(df["RoleClassLibName"] == child_lib) & (df["Name"] == p_name)]
    if not same_lib_match.empty:
        return f"{child_lib}::{p_name}"

    # Check if parent exists in a different library
    other_match = df[df["Name"] == p_name]
    if not other_match.empty:
        return f"{other_match.iloc[0]['RoleClassLibName']}::{p_name}"

    # Parent is undefined
    return f"undefined::{p_name}"

def build_lookup_dictionaries(df):
    node_to_parent_id = {}
    node_id_to_display = {}
    node_id_to_lib = {}

    for index, row in df.iterrows():
        lib_name = str(row.get("RoleClassLibName")).strip()
        class_name = str(row.get("Name")).strip()
        parent_name = row.get("Parent")

        if class_name != 'nan' and class_name != "":
            node_id = f"{lib_name}::{class_name}"
            node_id_to_display[node_id] = class_name
            node_id_to_lib[node_id] = lib_name

            parent_id = resolve_parent_id(df, lib_name, parent_name)
            node_to_parent_id[node_id] = parent_id

            # Register implied parents into the lookup dictionaries
            if parent_id is not None and parent_id.startswith("Implied::"):
                node_id_to_display[parent_id] = str(parent_name).strip()
                node_id_to_lib[parent_id] = "Implied/Unknown"
    return node_to_parent_id, node_id_to_display, node_id_to_lib