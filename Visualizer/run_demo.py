import json
import os
from TemporalVisualizer import TemporalKnowledgeGraph, TemporalSubgraphExtractor, TemporalVisualizer

def run_demo():
    """
    运行演示脚本：适配支持实时密度控制的 TemporalVisualizer 版本。
    """
    # --- 1. 参数配置 ---
    input_file = "icews14.jsonl"  # 输入原始的文本kg文件：icews14.jsonl
    
    center_node = "South_Korea"
    start_date = "2014-06-20"
    num_frames = 10

    k_hop = 4
    max_neighbors = [5, 1, 1, 1]
    
    # True -> 逻辑连接模式 | False -> 瞬时连接模式
    is_logical = False

    output_html = f"{center_node}_{start_date}_{num_frames}.html"

    # --- 2. 加载数据 ---
    if not os.path.exists(input_file):
        print(f"❌ 错误: 找不到输入文件 '{input_file}'。")
        return

    print(f"📂 正在加载全量时序图谱数据...")
    tkg = TemporalKnowledgeGraph(input_file)
    temporal_data = tkg.load()

    # --- 3. 提取子图序列 ---
    extractor = TemporalSubgraphExtractor(temporal_data)
    
    print(f"🔍 正在执行采样 (中心: {center_node})...")
    
    # 核心修复点：接收 4 个返回值，匹配当前的 TemporalVisualizer.py
    # frames_info: 可视化数据
    # master_nodes: 活跃节点集合
    # raw_window_data: 原始三元组数据（用于UI重采样）
    # pool_nodes: 窗口内全量节点池（用于UI重采样扩展）
    frames_info, master_nodes, raw_window_data, pool_nodes = extractor.extract(
        center_node=center_node,
        k_hop=k_hop,
        max_neighbors=max_neighbors,
        start_date=start_date,
        num_frames=num_frames,
        is_logical=is_logical
    )

    # --- 4. 可视化导出 ---
    visualizer = TemporalVisualizer(height="950px", bgcolor="#f8fafc")
    
    # 将原始数据池及初始参数传给可视化引擎
    visualizer.visualize(
        frames_info=frames_info,
        master_nodes=master_nodes,
        raw_window_data=raw_window_data,
        pool_nodes=pool_nodes,
        output_path=output_html,
        init_k=k_hop,
        init_max_n=",".join(map(str, max_neighbors))
    )

    print("\n" + "="*60)
    print(f"✅ 生成成功: {output_html}")
    print(f"💡 提示: 您的可视化引擎包含实时密度控制功能，请在浏览器侧边栏体验。")
    print("="*60)

if __name__ == "__main__":
    run_demo()