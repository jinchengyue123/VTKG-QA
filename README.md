# 🚀 VTKG-QA: Visual Temporal Knowledge Graph Question Answering

**VTKG-QA** 是一个大规模基准测试数据集，专注于评估多模态大模型（MLLMs）在动态可视化图谱序列上的时空推理与拓扑感知能力。

---

## 📂 目录结构 (Directory Structure)

本仓库的文件组织如下：

* **[📁 Supplementary_Material](./Supplementary_Material)**:
* **📁 VTKG-QA**: 数据集核心文件。
    * `🖼️ image_tkg/`: 时序知识图谱的图像序列。
    * `📝 text_tkg/`: 图像对应的文本描述信息。
    * `📊 tkg_qa.jsonl`: 包含 QA 对及推理标注的主数据文件。
* **📁 Visualizer**: 可视化工具包。
    * `🐍 TemporalVisualizer.py`: 动态图渲染核心代码。
    * `▶️ run_demo.py`: 示例运行脚本。
* **[📁 html](./html)**: 交互式可视化 Demo 存放处。
* **📁 source_data**: 原始数据源（ICEWS, Wikidata, YAGO 等）。

---

## 🔗 快速访问 (Quick Access)

### 📖 补充材料 (Supplementary Materials)
关于数据集的详细 Taxonomy 和实验设置，请参阅：
👉 **[点击进入补充材料页面](./Supplementary_Material)**

### 🌐 交互式可视化 Demo (Interactive Demo)
无需下载，直接点击下方链接即可在浏览器中预览 VTKG 的动态演化过程：
👉 **[🚀 点击直接弹出可视化 Demo](https://raw.githack.com/jinchengyue123/VTKG-QA/main/html/Citizen_1_2014-03-12_10.html)**

---

