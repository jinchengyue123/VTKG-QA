# 🚀 VTKG-QA: Visual Temporal Knowledge Graph Question Answering

**VTKG-QA** is a large-scale benchmark designed to evaluate the **spatio-temporal reasoning** and **topological awareness** of Large Multimodal Models (LMMs) over dynamic visual graph sequences.

---

## 📂 Directory Structure

The repository is organized as follows to support both dataset access and visualization:

* **[📁 Supplementary_Material](./Supplementary_Material)**: Contains comprehensive supplementary materials for the paper.
* **📁 VTKG-QA**: Core dataset components.
    * `🖼️ image_tkg/`: Sequences of visualized temporal knowledge graphs.
    * `📝 text_tkg/`: Corresponding textual descriptions and metadata for each graph frame.
    * `📊 tkg_qa.jsonl`: The primary dataset file containing QA pairs, ground truth, and reasoning path annotations.
* **📁 Visualizer**: Tools for graph rendering and analysis.
    * `🐍 TemporalVisualizer.py`: The core engine for dynamic graph rendering and temporal evolution.
    * `▶️ run_demo.py`: A quick-start script to execute the visualization pipeline.
* **[📁 html](./html)**: Interactive visualization demos exported as HTML files.
* **📁 source_data**: Original knowledge base records (ICEWS, Wikidata, YAGO, etc.) used for graph construction.

---

## 🔗 Quick Access

### 📖 Supplementary Materials
For a detailed breakdown of the question taxonomy and experimental configurations:
👉 **[View Supplementary Materials](./Supplementary_Material)**

### 🌐 Interactive Visualization Demo
Experience the dynamic evolution of VTKG directly in your browser without any installation:
👉 **[🚀 Launch Interactive Demo (Live View)](https://raw.githack.com/jinchengyue123/VTKG-QA/main/html/Citizen_1_2014-03-12_10.html)**

---

