from pyvis.network import Network

def generate_pyvis_graph(current_df, layout_style, selected_lib, unique_libs_list, nodes_to_draw, node_to_parent_id,
                         node_id_to_display, node_id_to_lib):
    net = Network(height='700px', width='100%', directed=True, bgcolor='#ffffff', font_color='black')

    net.options.interaction.hover = True
    net.options.interaction.hoverConnectedEdges = True
    net.options.interaction.selectConnectedEdges = True

    # layout logic
    if layout_style == "Top-Down Tree":
        net.set_options('{"layout": {"hierarchical": {"direction": "UD"}}, "physics": {"enabled": false}}')
    elif layout_style == "Left-Right Tree":
        net.set_options('{"layout": {"hierarchical": {"direction": "LR"}}, "physics": {"enabled": false}}')
    else:
        # For physics clusters
        net.set_options('{"physics": {"enabled": true}}')

    # Draw Library nodes
    if selected_lib == "All Libraries":
        libs_to_draw = unique_libs_list
    else:
        libs_to_draw = [selected_lib]

    for lib in libs_to_draw:
        net.add_node(lib, label=lib, shape='box', color='#a0c4ff', size=40)

    # Cleaning dataframe to prevent drawing duplicates
    clean_df = current_df.drop_duplicates(subset=["RoleClassLibName", "Name"])

    # Draw Class nodes
    for index, row in clean_df.iterrows():
        lib_name = str(row.get("RoleClassLibName")).strip()
        class_name = str(row.get("Name")).strip()

        if class_name != 'nan' and class_name != "":
            node_id = f"{lib_name}::{class_name}"
            if selected_lib != "All Libraries" and node_id not in nodes_to_draw:
                continue

            if selected_lib != "All Libraries" and lib_name != selected_lib:
                display_label = f"{class_name}\n({lib_name})"
                node_color = '#ffd6a5'
            else:
                display_label = class_name
                node_color = '#caffbf'

            net.add_node(node_id, label=display_label, shape='dot', color=node_color, size=20,
                         font={'color': 'black'})

    # Draw Edges
    for index, row in current_df.iterrows():
        lib_name = str(row.get("RoleClassLibName")).strip()
        class_name = str(row.get("Name")).strip()

        if class_name != 'nan' and class_name != "":
            node_id = f"{lib_name}::{class_name}"

            if selected_lib != "All Libraries" and node_id not in nodes_to_draw:
                continue

            # Containment Edge
            if lib_name != 'nan' and lib_name in libs_to_draw:
                # DEFENSIVE CHECK: Only draw if BOTH nodes physically exist on the canvas
                if lib_name in net.get_nodes() and node_id in net.get_nodes():
                    net.add_edge(lib_name, node_id, color='grey', dashes=True, smooth={'type': 'continuous'})

            # Inheritance Edge
            parent_id = node_to_parent_id.get(node_id)
            if parent_id is not None:

                # If parent hasn't been drawn yet, draw it as a placeholder
                if parent_id not in net.get_nodes():

                    # 1. Grab the names directly from the dictionaries
                    p_name = node_id_to_display[parent_id]
                    p_lib = node_id_to_lib[parent_id]

                    # 2. Create the text label
                    if selected_lib == "All Libraries":
                        p_label = p_name
                    else:
                        p_label = p_name + "\n(" + p_lib + ")"

                    # 3. Draw the red dot
                    net.add_node(parent_id, label=p_label, shape='dot', color='#ffadad', size=20,
                                 title="Implied Parent", font={'color': 'black'})

                # Draw the arrow back to the parent
                net.add_edge(parent_id, node_id, color='black',
                             smooth={'type': 'curvedCW', 'roundness': 0.2},
                             arrows={'from': {'enabled': True, 'scaleFactor': 1.5}})

    return net