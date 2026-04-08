# 🚀 TVKG-QA: Temporal Visual Knowledge Graph Question Answering


这是一个关于**时序视觉知识图谱问答 (TVKG-QA)** 的大规模基准数据集。本项目旨在评估多模态大模型 (MLLMs) 在动态图序列中的感知、逻辑推理及拓扑分析能力。

---

## 📂 项目结构 (Repository Structure)

本项目的文件组织如下，涵盖了从原始数据到可视化工具的全流程：

* **[📁 Supplemetary_Material](./Supplemetary_Material)**: 
    * 📖 包含详细的 [补充材料页面](#-supplementary-materials-access)，涉及 Level 1-3 的问题模板、Bad Cases 分析及 LPV 指标定义。
* **📁 VTKG-QA**: 核心数据集存放处。
    * `🖼️ image_tkg/`: 存储生成的时序知识图谱图像序列。
    * `📝 text_tkg/`: 对应的图谱文本描述信息。
    * `📊 tkg_qa.jsonl`: 包含 QA 对、逻辑路径标注的核心数据文件。
* **📁 Visualizer**: 
    * `🖥️ run_demo.py`: 快速启动可视化演示的脚本。
    * `🐍 TemporalVisualizer.py`: 处理动态图谱演进的核心可视化引擎。
* **📁 html**: 
    * 🌐 存放导出后的 [交互式可视化 Demo](#-interactive-visualization-demo)。
* **📁 source_data**: 
    * 💾 原始知识库数据，包括 `ICEWS05-15`, `ICEWS14`, `Wikidata`, `YAGO` 以及实体关系映射表。

---

## 🔗 快速访问 (Quick Access)

### 📚 Supplementary Materials Access
我们提供了详尽的实验数据和详细的 Taxonomy 说明。
👉 **[点击此处跳转至补充材料详情页](./Supplemetary_Material/README.md)** *(注：请确保该目录下存有 README 或相关引导文件)*

### 🌐 Interactive Visualization Demo
你可以通过交互式 HTML 页面直接观察 TVKG 的演进过程。
👉 **[点击此处在线查看可视化 Demo](https://你的用户名.github.io/项目名/html/index.html)** *(注：需在仓库 Settings 中开启 GitHub Pages，或直接指向具体 HTML 文件路径)*



