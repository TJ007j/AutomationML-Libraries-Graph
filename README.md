# AutomationML Libraries Graph

A Python-based visualization and graph analysis tool for exploring relationships between AutomationML (AML) libraries, classes, interfaces, and system structures using interactive graph representations.

The project enables users to transform AutomationML structures into connected graph networks for analysis, visualization, and engineering interpretation. It is designed for Model-Based Systems Engineering (MBSE), industrial automation, and AutomationML-driven workflows.

AutomationML is an open, vendor-neutral standard for industrial engineering data exchange based on CAEX/XML. ([GitHub][1])

---

# Features

## Interactive Graph Visualization

* Visualize AutomationML entities as graph nodes and edges
* Interactive graph rendering using `PyVis`
* Zoom, drag, inspect, and explore graph structures directly in browser

## AutomationML Structure Analysis

* Parse AutomationML-related data structures
* Represent:

  * Libraries
  * Classes
  * Interfaces
  * Relationships
  * Hierarchies
* Convert engineering structures into graph-based models

## Streamlit-Based User Interface

* Lightweight interactive web application using Streamlit
* Easy-to-use interface for graph generation and exploration
* Browser-based visualization workflow

## Graph-Based Engineering Representation

Supports graph-oriented modelling concepts frequently used in:

* MBSE
* Digital engineering
* Knowledge graphs
* Industrial system modelling
* Semantic engineering workflows

Graph-based modelling is increasingly important for industrial knowledge representation and automation workflows. ([arXiv][2])

---

# Technologies Used

* Python
* Streamlit
* PyVis
* Pandas
* NumPy
* HTML Graph Rendering
* AutomationML concepts
* Graph-based visualization

---

# Project Structure

```text
AutomationML-Libraries-Graph/
│
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── data/                      # Input AML or graph data
├── output/                    # Generated graph outputs
├── utils/                     # Helper and processing modules
└── assets/                    # Images or supporting files
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/TJ007j/AutomationML-Libraries-Graph.git
cd AutomationML-Libraries-Graph
```

---

# 2. Create Virtual Environment

## Windows

```bash
py -m venv .venv
.venv\Scripts\activate
```

## Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

# 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Required Libraries

The project uses libraries such as:

```text
streamlit
pandas
numpy
pyvis
```

---

# Running the Application

Launch the Streamlit app:

```bash
streamlit run app.py
```

---

# Example Workflow

1. Load AutomationML-related structures or datasets
2. Process relationships between engineering entities
3. Generate graph nodes and edges
4. Render interactive visualization
5. Explore graph topology and connections

---

# Visualization Capabilities

The graph visualization supports:

* Node highlighting
* Interactive navigation
* Dynamic edge rendering
* Relationship exploration
* Structural dependency visualization

---

# Use Cases

## Industrial Automation

* Analyze AutomationML libraries
* Explore engineering hierarchies
* Visualize component relationships

## MBSE and Systems Engineering

* Graph-based system representation
* Architecture exploration
* Relationship tracing

## Research and Education

* AutomationML learning
* Engineering data visualization
* Knowledge graph experimentation

---

# Future Improvements

Possible future extensions include:

* Graph database export
* Advanced filtering and search
* Semantic relationship analysis
* AutomationML ontology integration
* Multi-layer engineering graph support

AutomationML integration with graph and ontology systems is an active research area for industrial knowledge modelling and validation.

---

# Contributing

Contributions, improvements, and feature suggestions are welcome.

Typical workflow:

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push branch
5. Open pull request

---

# Author

Tirth Joshi
