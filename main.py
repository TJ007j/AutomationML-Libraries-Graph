import streamlit as st
import pandas as pd
import numpy as np
from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="AML Library Viewer")
st.title("AutomationML Role Class Library Manager")

# --- 1. DATA UPLOAD & INITIALIZATION ---
st.sidebar.header("1. Data Source")
uploaded_file = st.sidebar.file_uploader("Upload AML CSV File", type=['csv'])

if uploaded_file is None:
    st.info(
        "👋 Welcome! Please upload your AutomationML CSV file in the sidebar to begin visualizing and editing your libraries.")
    st.stop()

if 'df' not in st.session_state or (
        'last_file' in st.session_state and st.session_state.last_file != uploaded_file.name):
    raw_df = pd.read_csv(uploaded_file)

    # Clean 1: Replace hyphens with actual NaN values
    raw_df.replace(to_replace=r'^\s*-\s*$', value=np.nan, regex=True, inplace=True)

    # Clean 2: Aggressive whitespace scrubbing for critical columns
    for col in ["RoleClassLibName", "Name", "Parent"]:
        if col in raw_df.columns:
            raw_df[col] = raw_df[col].astype(str).str.strip()
            raw_df[col] = raw_df[col].replace(['nan', '', 'None'], np.nan)

    st.session_state.df = raw_df
    st.session_state.last_file = uploaded_file.name

attr_col = "Attributes?" if "Attributes?" in st.session_state.df.columns else "Attributes"
current_df = st.session_state.df


# Helper function to prevent namespace collisions (Resolving Parents)
def resolve_parent_id(df, child_lib, parent_name):
    if pd.isna(parent_name) or str(parent_name).strip() == 'nan' or not str(parent_name).strip():
        return None

    p_name = str(parent_name).strip()

    # Priority 1: Parent exists in the SAME library
    same_lib_match = df[(df["RoleClassLibName"] == child_lib) & (df["Name"] == p_name)]
    if not same_lib_match.empty:
        return f"{child_lib}::{p_name}"

    # Priority 2: Parent exists in a DIFFERENT library
    other_match = df[df["Name"] == p_name]
    if not other_match.empty:
        return f"{other_match.iloc[0]['RoleClassLibName']}::{p_name}"

    # Priority 3: Parent is completely undefined (Implied)
    return f"Implied::{p_name}"


# Build strict lookup dictionaries using Unique Namespace IDs (Lib::Class)
node_to_parent_id = {}
node_id_to_display = {}
node_id_to_lib = {}

for _, row in current_df.iterrows():
    l = str(row.get("RoleClassLibName")).strip()
    c = str(row.get("Name")).strip()
    p = row.get("Parent")

    if c != 'nan' and c:
        node_id = f"{l}::{c}"
        node_id_to_display[node_id] = c
        node_id_to_lib[node_id] = l

        parent_id = resolve_parent_id(current_df, l, p)
        node_to_parent_id[node_id] = parent_id

        # Register implied parents into the lookup dictionaries
        if parent_id and parent_id.startswith("Implied::"):
            node_id_to_display[parent_id] = str(p).strip()
            node_id_to_lib[parent_id] = "Implied/Unknown"

# --- 2. SIDEBAR NAVIGATION ---
st.sidebar.markdown("---")
st.sidebar.header("2. Data Management")
operation = st.sidebar.radio(
    "Action:",
    ["View Graph", "Add Node (Class)", "Edit Node / Edges", "Delete Node", "Export Data"]
)

selected_lib = "All Libraries"
selected_class = "All Classes"

# --- SIDEBAR FILTERS (Only active when viewing graph) ---
if operation == "View Graph":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Graph Appearance")
    layout_style = st.sidebar.selectbox(
        "Select Layout Style",
        ["Physics Clusters (Best for Large Data)", "Top-Down Tree", "Left-Right Tree"]
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Deep Dive Filter")
    unique_libs_list = sorted(
        [str(lib) for lib in current_df["RoleClassLibName"].dropna().unique() if str(lib).strip()])
    selected_lib = st.sidebar.selectbox("1. Select a Library:", ["All Libraries"] + unique_libs_list)

    if selected_lib != "All Libraries":
        classes_in_lib = sorted(
            current_df[current_df["RoleClassLibName"] == selected_lib]["Name"].dropna().unique().tolist())
        selected_class = st.sidebar.selectbox("2. Select a Class (Optional):", ["All Classes"] + classes_in_lib)

# --- 3. MAIN PAGE CONTENT ---

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

    if st.button("Submit Creation", type="primary") and new_name:
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
            idx = current_df[current_df["Name"] == target_name].index
            st.session_state.df.loc[idx, "RoleClassLibName"] = updated_lib if updated_lib else None
            st.session_state.df.loc[idx, "Parent"] = updated_parent if updated_parent else None
            st.success("Node updated successfully! Switch to 'View Graph' in the sidebar to see changes.")

elif operation == "Delete Node":
    st.header("Remove Role Class")
    st.markdown("Warning: Deleting a node will remove it from the visual graph entirely.")

    target_delete = st.selectbox("Select Class to Delete", current_df["Name"].dropna().unique())
    if st.button("Delete Node", type="primary"):
        st.session_state.df = current_df[current_df["Name"] != target_delete]
        st.success(f"Node '{target_delete}' has been deleted.")

elif operation == "Export Data":
    # Sidebar Download Button
    st.sidebar.markdown("---")
    st.sidebar.subheader("Export")
    csv_data = current_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="Download New CSV File",
        data=csv_data,
        file_name="Modified_AML_Libraries.csv",
        mime="text/csv",
        type="primary"
    )

    # Main Page Dataframe Preview
    st.header("Data Preview")
    st.markdown("Review your modified library data below. Use the button in the sidebar to download the CSV.")
    st.dataframe(current_df, use_container_width=True, height=600)


elif operation == "View Graph":

    # --- Ancestry Logic & UI Tables ---
    nodes_to_draw = set()

    if selected_lib != "All Libraries":
        target_classes = classes_in_lib if selected_class == "All Classes" else [selected_class]

        chains_raw = {}
        for cls in target_classes:
            node_id = f"{selected_lib}::{cls}"
            chain_ids = []
            curr = node_id
            nodes_to_draw.add(curr)

            while curr in node_to_parent_id and node_to_parent_id[curr]:
                p_id = node_to_parent_id[curr]
                if p_id in chain_ids: break  # Prevent infinite loops
                chain_ids.append(p_id)
                nodes_to_draw.add(p_id)
                curr = p_id
            chains_raw[node_id] = chain_ids

        # Format the chains for the UI Tables
        formatted_table_data = []
        first_parents = []
        last_parents = []

        for n_id, chain_ids in chains_raw.items():
            cls_display = node_id_to_display.get(n_id, n_id.split("::")[-1])
            fmt_chain = []

            for p_id in chain_ids:
                p_lib = node_id_to_lib.get(p_id, "Unknown Library")
                p_disp = node_id_to_display.get(p_id, "Unknown Class")
                formatted_p = f"{p_disp} ({p_lib})" if p_lib != selected_lib else p_disp
                fmt_chain.append(formatted_p)

            chain_str = " -> ".join(fmt_chain) if fmt_chain else "None"
            formatted_table_data.append({"Class": cls_display, "Ancestral Chain": chain_str})

            if fmt_chain:
                first_parents.append(fmt_chain[0])
                last_parents.append(fmt_chain[-1])

        # Display UI Tables
        if selected_class == "All Classes":
            st.subheader(f"Library Analysis: {selected_lib}")
            most_freq_first = pd.Series(first_parents).mode()[0] if first_parents else "N/A"
            most_freq_last = pd.Series(last_parents).mode()[0] if last_parents else "N/A"

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Classes in Library", len(classes_in_lib))
            col2.metric("Most Frequent Direct Parent", most_freq_first)
            col3.metric("Most Frequent Root Ancestor", most_freq_last)

            st.dataframe(pd.DataFrame(formatted_table_data), use_container_width=True, hide_index=True)

        else:
            st.subheader(f"Class Ancestry: {selected_class} (from {selected_lib})")
            st.table(pd.DataFrame([{"Library": selected_lib, "Class": selected_class,
                                    "Ancestral Chain": formatted_table_data[0]["Ancestral Chain"]}]))
        st.markdown("---")

    # --- PyVis Graph Generation ---
    net = Network(height='700px', width='100%', directed=True, bgcolor='#ffffff', font_color='black')

    if layout_style == "Top-Down Tree":
        net.set_options(
            '{"interaction": {"hover": true, "hoverConnectedEdges": true, "selectConnectedEdges": true}, "layout": {"hierarchical": {"enabled": true, "direction": "UD", "sortMethod": "directed", "nodeSpacing": 150, "levelSeparation": 200}}, "physics": {"enabled": false}}')
    elif layout_style == "Left-Right Tree":
        net.set_options(
            '{"interaction": {"hover": true, "hoverConnectedEdges": true, "selectConnectedEdges": true}, "layout": {"hierarchical": {"enabled": true, "direction": "LR", "sortMethod": "directed", "nodeSpacing": 100, "levelSeparation": 350}}, "physics": {"enabled": false}}')
    else:
        net.set_options(
            '{"interaction": {"hover": true, "hoverConnectedEdges": true, "selectConnectedEdges": true}, "physics": {"barnesHut": {"gravitationalConstant": -8000, "centralGravity": 0.3, "springLength": 250, "springConstant": 0.04, "damping": 0.09}}}')

    # Draw Library Nodes
    libs_to_draw = [selected_lib] if selected_lib != "All Libraries" else unique_libs_list
    for lib in libs_to_draw:
        net.add_node(lib, label=lib, shape='box', color='#a0c4ff', size=40)

    # Draw Class Nodes (Removing duplicates strictly based on Library AND Name)
    for index, row in current_df.drop_duplicates(subset=["RoleClassLibName", "Name"]).iterrows():
        l_name = str(row.get("RoleClassLibName")).strip()
        c_name = str(row.get("Name")).strip()

        if c_name != 'nan' and c_name:
            node_id = f"{l_name}::{c_name}"

            # Filter logic
            if selected_lib != "All Libraries" and node_id not in nodes_to_draw:
                continue

            tooltip_html = f"<b>Class:</b> {c_name}<br><b>ID:</b> {row.get('ID', 'N/A')}<br><b>Desc:</b> {row.get('Description', 'N/A')}"

            display_label = c_name
            if selected_lib != "All Libraries" and l_name != selected_lib:
                display_label = f"{c_name}\n({l_name})"
                node_color = '#ffd6a5'
            else:
                node_color = '#caffbf'

            net.add_node(node_id, label=display_label, shape='dot', color=node_color, size=20, title=tooltip_html,
                         font={'color': 'black'})

    # Draw Edges
    for index, row in current_df.iterrows():
        l_name = str(row.get("RoleClassLibName")).strip()
        c_name = str(row.get("Name")).strip()
        p_name = row.get("Parent")

        if c_name != 'nan' and c_name:
            node_id = f"{l_name}::{c_name}"

            if selected_lib != "All Libraries" and node_id not in nodes_to_draw:
                continue

            # Containment Edge (Lib -> Class)
            if l_name != 'nan' and l_name in libs_to_draw:
                net.add_edge(l_name, node_id, color='grey', dashes=True, smooth={'type': 'continuous'})

            # Inheritance Edge (Parent -> Class)
            parent_id = node_to_parent_id.get(node_id)
            if parent_id:
                if parent_id not in net.get_nodes():
                    p_disp = node_id_to_display.get(parent_id, parent_id.split("::")[-1])
                    p_lib = node_id_to_lib.get(parent_id, "Unknown Library")
                    display_lbl = f"{p_disp}\n({p_lib})" if selected_lib != "All Libraries" else p_disp
                    net.add_node(parent_id, label=display_lbl, shape='dot', color='#ffadad', size=20,
                                 title="Implied Parent", font={'color': 'black'})

                hover_title = f"Child: {c_name} inherits from Parent: {node_id_to_display.get(parent_id, '')}"
                net.add_edge(parent_id, node_id, color='black', title=hover_title,
                             smooth={'type': 'curvedCW', 'roundness': 0.2},
                             arrows={'from': {'enabled': True, 'scaleFactor': 1.5}})

    # Render
    net.save_graph("graph.html")
    with open("graph.html", 'r', encoding='utf-8') as html_file:
        source_code = html_file.read()
    components.html(source_code, height=720)