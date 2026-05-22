import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from utils_data import clean_dataframe, build_lookup_dictionaries
from utils_analysis import display_ancestry_tables
from utils_graph import generate_pyvis_graph

st.set_page_config(layout="wide", page_title="AML Library Viewer")
st.title("AutomationML Role Class Library Manager")

# data upload
st.sidebar.header("1. Data Source")
uploaded_file = st.sidebar.file_uploader("Upload AML CSV File", type=['csv'])

if uploaded_file is None:
    st.info(
        "👋 Welcome! Please upload your AutomationML CSV file in the sidebar to begin visualizing and editing your libraries.")
    st.stop()

is_new_file = 'df' not in st.session_state or (
            'last_file' in st.session_state and st.session_state.last_file != uploaded_file.name)
if is_new_file:
    st.session_state.df = clean_dataframe(pd.read_csv(uploaded_file))
    st.session_state.last_file = uploaded_file.name

current_df = st.session_state.df
attr_col = "Attributes?" if "Attributes?" in current_df.columns else "Attributes"

# sidebar
st.sidebar.markdown("---")
st.sidebar.header("2. Data Management")
operation = st.sidebar.radio("Action:",
                             ["View Graph", "Add Node (Class)", "Edit Node / Edges", "Delete Node", "Export Data"])

selected_lib, selected_class, layout_style = "All Libraries", "All Classes", "Physics Clusters (Best for Large Data)"

if operation == "View Graph":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Graph Appearance")
    layout_style = st.sidebar.selectbox("Select Layout Style",
                                        ["Physics Clusters (Best for Large Data)", "Top-Down Tree", "Left-Right Tree"])

    st.sidebar.markdown("---")
    st.sidebar.subheader("Deep Dive Filter")
    unique_libs_list = sorted(
        [str(lib).strip() for lib in current_df["RoleClassLibName"].dropna().unique() if str(lib).strip() != ""])
    selected_lib = st.sidebar.selectbox("1. Select a Library:", ["All Libraries"] + unique_libs_list)

    if selected_lib != "All Libraries":
        classes_in_lib_df = current_df[current_df["RoleClassLibName"] == selected_lib]
        classes_in_lib = sorted(classes_in_lib_df["Name"].dropna().unique().tolist())
        selected_class = st.sidebar.selectbox("2. Select a Class (Optional):", ["All Classes"] + classes_in_lib)


if operation == "Add Node (Class)":
    st.header("Create New Role Class")
    st.markdown("Fill out the details below to add a new class to your AutomationML libraries.")

    col1, col2 = st.columns(2)
    with col1:
        new_lib = st.text_input("Library (Containment Edge Target)")
        new_name = st.text_input("Class Name (New Node)")
        new_parent = st.text_input("Parent Class (Inheritance Edge Target)")
    with col2:
        new_id = st.selectbox("ID Present?", ["Yes", "No"])
        new_desc = st.selectbox("Description Present?", ["Yes", "No"])
        new_attr = st.selectbox("Attributes Present?", ["Yes", "No"])

    if st.button("Submit Creation", type="primary") and new_name != "":
        new_row = {"RoleClassLibName": new_lib, "Name": new_name, "Parent": new_parent, "ID": new_id,
                   "Description": new_desc, attr_col: new_attr}
        st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Node added successfully! Switch to 'View Graph' in the sidebar to see it.")

elif operation == "Edit Node / Edges":
    st.header("Edit Node & Edge Relationships")
    st.markdown("Select an existing class to modify its library assignment or inheritance structure.")
    target_name = st.selectbox("Select Class to Edit", current_df["Name"].dropna().unique())

    if target_name:
        curr_data = current_df[current_df["Name"] == target_name].iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            updated_lib = st.text_input("Library (Containment)", value=curr_data.get("RoleClassLibName", ""))
        with col2:
            updated_parent = st.text_input("Parent Class (Inheritance)", value=curr_data.get("Parent", ""))

        if st.button("Submit Updates", type="primary"):
            row_index = current_df[current_df["Name"] == target_name].index
            st.session_state.df.loc[row_index, "RoleClassLibName"] = updated_lib if updated_lib != "" else None
            st.session_state.df.loc[row_index, "Parent"] = updated_parent if updated_parent != "" else None
            st.success("Node updated successfully! Switch to 'View Graph' in the sidebar to see changes.")

elif operation == "Delete Node":
    st.header("Remove Role Class")
    st.markdown("Warning: Deleting a node will remove it from the visual graph entirely.")
    target_delete = st.selectbox("Select Class to Delete", current_df["Name"].dropna().unique())
    if st.button("Delete Node", type="primary"):
        st.session_state.df = current_df[current_df["Name"] != target_delete]
        st.success(f"Node '{target_delete}' has been deleted.")

elif operation == "Export Data":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Export")
    st.sidebar.download_button("Download New CSV File", data=current_df.to_csv(index=False).encode('utf-8'),
                               file_name="Modified_AML_Libraries.csv", mime="text/csv", type="primary")
    st.header("Data Preview")
    st.markdown("Review your modified library data below. Use the button in the sidebar to download the CSV.")
    st.dataframe(current_df, use_container_width=True, height=600)

elif operation == "View Graph":
    node_to_parent_id, node_id_to_display, node_id_to_lib = build_lookup_dictionaries(current_df)

    nodes_to_draw = set()
    if selected_lib != "All Libraries":
        nodes_to_draw = display_ancestry_tables(selected_lib, selected_class, classes_in_lib, node_to_parent_id,
                                                node_id_to_display, node_id_to_lib)

    net = generate_pyvis_graph(current_df, layout_style, selected_lib, unique_libs_list, nodes_to_draw,
                               node_to_parent_id, node_id_to_display, node_id_to_lib)
    net.save_graph("graph.html")
    with open("graph.html", 'r', encoding='utf-8') as html_file:
        components.html(html_file.read(), height=720)