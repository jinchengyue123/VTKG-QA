# 🚀 TVKG-QA: Temporal Visual Knowledge Graph Question Answering

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Venue: ACM MM 2026](https://img.shields.io/badge/Venue-ACM%20MM%202026-blue.svg)](#)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)

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

---

## 🛠️ 安装与使用 (Getting Started)

1. **克隆仓库**:
   ```bash
   git clone [https://github.com/yourusername/TVKG-QA.git](https://github.com/yourusername/TVKG-QA.git)
   cd TVKG-QA
   ```

2. **环境配置**:
   ```bash
   pip install -r requirements.txt
   ```

3. **运行可视化演示**:
   ```bash
   python Visualizer/run_demo.py
   ```

---

## 📊 数据集统计 (Dataset Statistics)

| 维度 (Dimension) | 子任务 (Sub-task) | 规模 (Size) | 难度等级 (Level) |
| :--- | :--- | :--- | :--- |
| **Basic Elements** | Existence, Counting | 50K+ | Level 1 |
| **Topology** | Community, Cycle, Tree | 30K+ | Level 2 |
| **Reasoning** | Duration, Ordering | 20K+ | Level 3 |

---

## ✉️ 联系方式 (Contact)

如果您对本项目有任何疑问，欢迎通过以下方式联系：
* **Email**: your_email@example.com
* **Issues**: [提交反馈](https://github.com/yourusername/TVKG-QA/issues)

---

⭐ **如果这个项目对您的研究有帮助，请给一个 Star！**
```

---

### 💡 提示与说明：

1.  **关于补充材料链接**：我在代码中使用了 `./Supplemetary_Material` 的相对路径。如果你在该文件夹下也放一个 `README.md`，点击链接会自动展示那个页面的内容。
2.  **关于 HTML Demo 链接**：
    * **最专业的方法**：去你的仓库设置 (**Settings** -> **Pages**)，将 `html` 文件夹部署为 GitHub Pages。这样你可以得到一个 `https://<user>.github.io/<repo>/...` 的链接，点击后可以直接在浏览器里运行交互式网页。
    * **简单的方法**：如果只是想让别人看到代码，保持现状即可。
3.  **拼写检查**：我注意到你的图片中文件夹名为 `Supplemetary_Material`（少了一个 `n`，应该是 `Supplementary`）。为了保证链接生效，**我在 README 里直接匹配了你图片中的拼写**。如果你之后修改了文件夹名，记得在 README 里也同步修改。
4.  **图标说明**：使用了标准的 GitHub Emoji（如 🚀, 📂, 📝），这些在 GitHub 页面上会自动渲染成精美的小图标。
