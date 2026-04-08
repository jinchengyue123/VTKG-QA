# 🚀 TVKG-QA: Temporal Visual Knowledge Graph Question Answering

本项目是一个大规模的时序视觉知识图谱问答基准测试。以下是仓库的核心目录结构及其功能说明，旨在帮助研究人员快速了解数据集构成与工具使用。

---

## 📂 目录结构说明 (Project Structure)

项目文件按照功能模块清晰划分：

### 📚 [Supplementary Material](./Supplementary_Material)
* **[📁 补充材料快捷访问](./Supplementary_Material)**：包含 Level 1-3 的详细问题模板、逻辑路径定义、Bad Cases 分析以及详细的实验结果补充。

### 📊 VTKG-QA (核心数据集)
* **📁 image_tkg/**: 存放生成的时序知识图谱图像序列（.png/.jpg）。
* **📁 text_tkg/**: 对应的图谱文本描述，包含节点与关系的属性信息。
* **📄 tkg_qa.jsonl**: 核心 QA 数据集文件，包含问题、标准答案以及推理路径标注。

### 🛠️ Visualizer (可视化工具)
* **🐍 TemporalVisualizer.py**: 负责动态图谱演化与渲染的核心 Python 模块。
* **▶️ run_demo.py**: 快速演示脚本，用于生成图谱序列的视觉呈现。
* **📄 icews14.jsonl**: 用于演示的采样数据片段。

### 🌐 html (交互式演示)
* **📁 html/**: 存放导出的交互式可视化页面，可通过浏览器直接查看图谱的动态变化。

### 💾 source_data (原始数据源)
* **📁 entity_relation_mapping/**: 实体与关系的映射表，确保不同数据源间的一致性。
* **📁 icews05-15 / icews14 / wikidata / yago**: 包含各个原始知识库（ICEWS, Wikidata, YAGO）的结构化数据，用于构建时序图谱。

---

## 🔗 快速链接 (Quick Links)

* 📖 **[查看补充材料 (Supplementary Materials)](./Supplementary_Material)**
* 🖼️ **[浏览图像数据 (Image TKG)](./VTKG-QA/image_tkg)**
* 🖥️ **[运行可视化 Demo (Visualizer)](./Visualizer/run_demo.py)**

---
