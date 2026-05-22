import streamlit as st
import pandas as pd


def display_ancestry_tables(selected_lib, selected_class, classes_in_lib, node_to_parent_id, node_id_to_display,
                            node_id_to_lib):
    nodes_to_draw = set()

    if selected_class == "All Classes":
        target_classes = classes_in_lib
    else:
        target_classes = [selected_class]

    chains_raw = {}
    for cls in target_classes:
        node_id = f"{selected_lib}::{cls}"
        chain_ids = []
        current_node = node_id

        nodes_to_draw.add(current_node)

        # trace upwards until we reacg the root parent
        while current_node in node_to_parent_id and node_to_parent_id[current_node] is not None:
            parent_id = node_to_parent_id[current_node]

            if parent_id in chain_ids:
                break  # Prevent infinite loops

            chain_ids.append(parent_id)
            nodes_to_draw.add(parent_id)
            current_node = parent_id

        chains_raw[node_id] = chain_ids # list of parents in the dictionary

    # format the chains for the UI Tables
    formatted_table_data = []
    first_parents = []
    last_parents = []

    for node_id, chain_ids in chains_raw.items():
        class_display_name = node_id_to_display.get(node_id, node_id.split("::")[-1])
        formatted_chain = []

        for p_id in chain_ids:
            p_lib = node_id_to_lib.get(p_id, "Unknown Library")
            p_disp = node_id_to_display.get(p_id, "Unknown Class")

            if p_lib != selected_lib:
                formatted_parent = f"{p_disp} ({p_lib})"
            else:
                formatted_parent = p_disp

            formatted_chain.append(formatted_parent)

        if len(formatted_chain) > 0:
            chain_string = " -> ".join(formatted_chain)
            first_parents.append(formatted_chain[0])
            last_parents.append(formatted_chain[-1])
        else:
            chain_string = "None"

        formatted_table_data.append({
            "Class": class_display_name,
            "Ancestral Chain": chain_string
        })

    # display UI tables
    if selected_class == "All Classes":
        st.subheader(f"Library Analysis: {selected_lib}")

        if len(first_parents) > 0:
            most_freq_first = pd.Series(first_parents).mode()[0]
        else:
            most_freq_first = "N/A"

        if len(last_parents) > 0:
            most_freq_last = pd.Series(last_parents).mode()[0]
        else:
            most_freq_last = "N/A"

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Classes in Library", len(classes_in_lib))
        col2.metric("Most Frequent Direct Parent", most_freq_first)
        col3.metric("Most Frequent Root Ancestor", most_freq_last)

        st.dataframe(pd.DataFrame(formatted_table_data), use_container_width=True, hide_index=True)

    else:
        st.subheader(f"Class Ancestry: {selected_class} (from {selected_lib})")
        single_row_data = {
            "Library": selected_lib,
            "Class": selected_class,
            "Ancestral Chain": formatted_table_data[0]["Ancestral Chain"]
        }
        st.table(pd.DataFrame([single_row_data]))
    st.markdown("---")
    return nodes_to_draw