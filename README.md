# 🧩 VTKG-QA: Visual Temporal Knowledge Graph Question Answering Dataset

Welcome to the **VTKG-QA** repository! This project provides a benchmark dataset and visualization tools for evaluating multimodal models on **temporal knowledge graphs**.  

---

## 📂 Repository Structure

```text
Supplementary_Material/          # 📄 PDF/LaTeX supplement
VTKG-QA/                         # 🗃 Main benchmark data
├── image_tkg/                   # 🖼 Visualized KG snapshots
├── text_tkg/                    # 📜 Text-based KG samples
├── tkq_qa.jsonl                  # ❓ QA pairs for VTKG-QA
Visualizer/                      # 🛠 Visualization tools
├── TemporalVisualizer.py         # 🔹 Core visualizer script
├── run_demo.py                   # ▶ Demo runner
├── icews14.jsonl                 # 🗂 Example dataset for visualization
html/                             # 🌐 HTML visualization output
source_data/                       # 🧬 Original sampled KG data
├── entity_relation_mapping/       # 🔗 Mapping of anonymized entities and relations
├── icews05-15/                    # 📅 ICEWS 2005-2015 KG samples
├── icews14/                       # 📅 ICEWS 2014 KG samples
├── wikidata/                       # 🌍 Wikidata KG samples
└── yago/                           # 📚 YAGO KG samples
