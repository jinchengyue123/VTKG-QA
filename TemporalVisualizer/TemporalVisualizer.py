import json
import os
import networkx as nx
from pyvis.network import Network
import random
from collections import defaultdict
from typing import Dict, List, Tuple, Set

"""
修改说明：
1. 节点命名同步：新节点 ID 直接采用用户输入的名称，确保导出的 JSONL 保持一致。
2. 快捷颜色面板：在节点编辑区新增 6 个特定颜色的点击按钮。
3. 增强版重名检测：
   - 如果节点在当前帧已存在且为显示状态，禁止添加并报错。
   - 如果节点在当前帧存在但为隐藏状态，将其设为显示。
   - 如果节点在当前帧完全不存在，直接新增。
4. UI 优化：增加错误提示区域，避免使用 alert()。
存在问题：
ui界面删除当前时间帧的节点后，再保存jsonl文件里面还有对应的三元组。
但是删除边之后，jsonl文件对应的三元组被删除。
"""

class TemporalKnowledgeGraph:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.temporal_triples = defaultdict(list)
        self.all_dates = []

    def load(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"未找到文件: {self.file_path}")
            
        with open(self.file_path, "r", encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line.strip())
                    head, rel, tail = data["triple"]
                    time_str = data["time"].replace("Time: ", "").strip()
                    self.temporal_triples[time_str].append((head, rel, tail))
                except Exception:
                    pass
        
        self.all_dates = sorted(list(self.temporal_triples.keys()))
        print(f"成功加载 {len(self.all_dates)} 个时间切片的数据。")
        return self.temporal_triples

class TemporalSubgraphExtractor:
    def __init__(self, temporal_data: Dict[str, List[Tuple]]):
        self.temporal_data = temporal_data
        self.all_dates = sorted(list(temporal_data.keys()))

    def _get_bfs_neighbors(self, graph, center, k, limits):
        relevant = {center}
        layer = {center}
        for hop in range(k):
            next_layer = set()
            limit = limits[hop] if hop < len(limits) else 10
            for node in layer:
                if graph.has_node(node):
                    neighbors = list(set(graph.successors(node)) | set(graph.predecessors(node)))
                    potential = [n for n in neighbors if n not in relevant]
                    if len(potential) > limit:
                        sampled = random.sample(potential, limit)
                    else:
                        sampled = potential
                    next_layer.update(sampled)
            relevant.update(next_layer)
            layer = next_layer
        return list(relevant)

    def extract(self, center_node: str, k_hop: int, max_neighbors: List[int], start_date: str, num_frames: int, is_logical: bool = True):
        if start_date not in self.all_dates:
            start_idx = 0
        else:
            start_idx = self.all_dates.index(start_date)
        
        target_dates = self.all_dates[start_idx : start_idx + num_frames]
        raw_window_data = {d: self.temporal_data[d] for d in target_dates}

        pool_nodes = set()
        for d in target_dates:
            for h, r, t in self.temporal_data[d]:
                pool_nodes.add(h); pool_nodes.add(t)

        if is_logical:
            full_window_g = nx.DiGraph()
            for d in target_dates:
                for h, r, t in self.temporal_data[d]:
                    full_window_g.add_edge(h, t)
            master_nodes = self._get_bfs_neighbors(full_window_g, center_node, k_hop, max_neighbors)
            
            frames_info = []
            for d in target_dates:
                subG = nx.MultiDiGraph()
                for h, r, t in self.temporal_data[d]:
                    if h in master_nodes and t in master_nodes:
                        subG.add_edge(h, t, label=r)
                frames_info.append({"date": d, "graph": subG, "active_nodes": master_nodes, "center": center_node})
            return frames_info, set(master_nodes), raw_window_data, pool_nodes
        else:
            frames_info = []
            all_union = set()
            for d in target_dates:
                instant_g = nx.DiGraph()
                for h, r, t in self.temporal_data[d]:
                    instant_g.add_edge(h, t)
                frame_neighbors = self._get_bfs_neighbors(instant_g, center_node, k_hop, max_neighbors)
                all_union.update(frame_neighbors)
                subG = nx.MultiDiGraph()
                for h, r, t in self.temporal_data[d]:
                    if h in frame_neighbors and t in frame_neighbors:
                        subG.add_edge(h, t, label=r)
                frames_info.append({"date": d, "graph": subG, "active_nodes": frame_neighbors, "center": center_node})
            return frames_info, all_union, raw_window_data, pool_nodes

class TemporalVisualizer:
    def __init__(self, height="950px", bgcolor="#f8fafc"):
        self.height = height
        self.width = "100%"
        self.bgcolor = bgcolor
        self.fixed_diameter = 90

    def get_color_by_degree(self, degree: int) -> str:
        if degree <= 1: return "#D1D5DB"
        elif degree <= 2: return "#93C5FD"
        elif degree <= 3: return "#2DD4BF"
        elif degree <= 4: return "#FBBF24"
        elif degree <= 5: return "#F97316"
        else: return "#F87171"

    def visualize(self, frames_info: List[Dict], master_nodes: Set[str], raw_window_data: Dict, pool_nodes: Set[str], output_path: str, init_k: int = 3, init_max_n: str = "5, 3, 2"):
        center_node = frames_info[0]["center"] if frames_info else None
        
        layout_G = nx.Graph()
        layout_G.add_nodes_from(pool_nodes)
        pos = nx.spring_layout(layout_G, k=1.8, iterations=50)
        
        if center_node and center_node in pos:
            offset_x, offset_y = pos[center_node]
            for n in pos:
                pos[n] = (pos[n][0] - offset_x, pos[n][1] - offset_y)

        frames_data = []
        for frame in frames_info:
            date, g, active_set = frame["date"], frame["graph"], set(frame["active_nodes"])
            current_pair_totals = defaultdict(int)
            for u, v in g.edges():
                current_pair_totals[tuple(sorted((u, v)))] += 1
            
            pair_occurrence_index = defaultdict(int)
            subgraph_degrees = dict(g.degree())

            nodes_list = []
            for node in pool_nodes:
                x, y = pos.get(node, (0, 0))
                is_active = node in active_set and node in g.nodes()
                deg = subgraph_degrees.get(node, 0)
                bg_color = self.get_color_by_degree(deg) if is_active else "#F3F4F6"
                
                nodes_list.append({
                    "id": node, 
                    "label": f"<b>{node}</b>", 
                    "x": x * 1800, 
                    "y": y * 1800, 
                    "shape": "circle",
                    "widthConstraint": {"minimum": self.fixed_diameter, "maximum": self.fixed_diameter},
                    "heightConstraint": {"minimum": self.fixed_diameter, "maximum": self.fixed_diameter},
                    "color": {
                        "background": bg_color, 
                        "border": "#97999C",
                        "highlight": {"background": bg_color, "border": "#97999C"},
                        "hover": {"background": bg_color, "border": "#97999C"}
                    },
                    "borderWidth": 2, 
                    "hidden": not is_active, 
                    "font": {"multi": "html", "size": 22, "color": "#000000", "face": "Arial"}
                })
            
            edges_list = []
            for u, v, d in g.edges(data=True):
                pair = tuple(sorted((u, v)))
                total_edges = current_pair_totals[pair]
                idx = pair_occurrence_index[pair]
                pair_occurrence_index[pair] += 1
                
                if total_edges == 1:
                    smooth = {"enabled": False}
                else:
                    side = "curvedCW" if idx % 2 == 0 else "curvedCCW"
                    roundness = 0.2 + (idx // 2) * 0.15
                    smooth = {"enabled": True, "type": side, "roundness": roundness}

                edges_list.append({
                    "from": u, "to": v, "label": d.get("label", ""), 
                    "arrows": {"to": {"enabled": True, "scaleFactor": 1.5}},
                    "color": {"color": "#000000", "highlight": "#000000", "hover": "#000000"},
                    "width": 2.5, 
                    "smooth": smooth, 
                    "font": {
                        "align": "top", "size": 20, "vadjust": -5, "color": "#000000", 
                        "strokeWidth": 6, "strokeColor": "#ffffff", "bold": True, "face": "Arial"
                    } 
                })
            frames_data.append({"date": date, "nodes": nodes_list, "edges": edges_list})

        net = Network(height=self.height, width=self.width, directed=True, bgcolor=self.bgcolor, cdn_resources="in_line")
        if frames_data:
            for n in frames_data[0]["nodes"]: net.add_node(n["id"], **{k:v for k,v in n.items() if k!='id'})
            for e in frames_data[0]["edges"]: net.add_edge(e["from"], e["to"], **{k:v for k,v in e.items() if k not in ['from', 'to']})

        html_str = net.generate_html()
        enhanced_html = self._inject_ultimate_temporal_editor(html_str, frames_data, center_node, raw_window_data, init_k, init_max_n)
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(enhanced_html)
        print(f"🚀 专业级时序编辑器已就绪: {output_path}")

    def _inject_ultimate_temporal_editor(self, html_str, frames_data, center_node, raw_window_data, init_k, init_max_n):
        json_frames = json.dumps(frames_data, ensure_ascii=False)
        json_raw = json.dumps(raw_window_data, ensure_ascii=False)
        
        editor_ui = f"""
        <style>
            :root {{ --bg: #f8fafc; --panel: #ffffff; --accent: #3b82f6; --text: #1e293b; --danger: #ef4444; --success: #22c55e; }}
            body {{ margin: 0; background: var(--bg); font-family: 'Segoe UI', sans-serif; color: var(--text); overflow: hidden; }}
            #sidebar {{ position: fixed; top: 0; left: 0; width: 350px; height: 100vh; background: var(--panel); border-right: 1px solid #e2e8f0; z-index: 2000; display: flex; flex-direction: column; box-shadow: 2px 0 10px rgba(0,0,0,0.05); }}
            .panel-header {{ background: #0f172a; color: #fff; padding: 20px; font-weight: 700; font-size: 18px; }}
            .tab-nav {{ display: flex; background: #f1f5f9; padding: 4px; gap: 4px; }}
            .tab-btn {{ flex: 1; padding: 10px; border: none; background: none; cursor: pointer; border-radius: 6px; font-size: 13px; font-weight: 600; color: #64748b; transition: 0.2s; }}
            .tab-btn.active {{ background: #fff; color: var(--accent); box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            .content-area {{ flex: 1; overflow-y: auto; padding: 20px; display: none; }}
            .content-area.active {{ display: block; }}
            #time-display {{ position: fixed; top: 90px; left: 370px; z-index: 1000; background: rgba(15, 23, 42, 0.8); color: white; padding: 10px 20px; border-radius: 10px; font-size: 42px; font-weight: bold; pointer-events: none; border: 2px solid rgba(255,255,255,0.1); }}
            .ctrl {{ margin-bottom: 16px; }}
            label {{ display: block; font-size: 12px; margin-bottom: 6px; font-weight: 600; color: #64748b; }}
            input, select, textarea {{ width: 100%; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; box-sizing: border-box; }}
            .action-btn {{ width: 100%; padding: 12px; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; margin-top: 5px; font-size: 13px; }}
            .primary {{ background: var(--accent); color: white; }}
            .success {{ background: var(--success); color: white; }}
            .warning {{ background: #f59e0b; color: white; }}
            .danger {{ background: #ef4444; color: white; }}
            .color-palette {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }}
            .color-box {{ width: 30px; height: 30px; border-radius: 6px; cursor: pointer; border: 2px solid #e2e8f0; transition: 0.2s; }}
            .color-box:hover {{ transform: scale(1.1); border-color: var(--accent); }}
            #error-msg {{ color: var(--danger); font-size: 12px; margin-top: 4px; display: none; font-weight: bold; }}
            #export-preview-container {{ margin-top: 15px; border: 2px dashed #cbd5e1; border-radius: 10px; padding: 5px; background: #fff; position: relative; }}
            #export-preview-canvas {{ width: 100%; height: auto; display: block; border-radius: 5px; }}
            .preview-tag {{ position: absolute; top: 5px; right: 5px; background: rgba(15, 23, 42, 0.6); color: white; font-size: 9px; padding: 2px 6px; border-radius: 4px; pointer-events: none; }}
            .nav-panel {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); background: rgba(255,255,255,0.95); padding: 10px 20px; border-radius: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); z-index: 1000; display: flex; align-items: center; gap: 30px; border: 1px solid #e2e8f0; }}
            .nav-arrow {{ background: none; border: none; cursor: pointer; padding: 10px; display: flex; align-items: center; justify-content: center; transition: 0.2s; }}
            .nav-arrow:hover {{ color: var(--accent); transform: scale(1.2); }}
            .nav-arrow svg {{ width: 28px; height: 28px; fill: currentColor; }}
            #lock-control {{ position: fixed; top: 20px; right: 20px; z-index: 2500; }}
            .lock-btn {{ background: white; border: 1px solid #e2e8f0; width: 50px; height: 50px; border-radius: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); font-size: 24px; opacity: 0.3; pointer-events: none; transition: 0.3s; }}
            .lock-btn.active {{ opacity: 1; pointer-events: auto; }}
            .lock-btn.locked {{ background: #fef2f2; border-color: var(--danger); color: var(--danger); }}
        </style>

        <div id="time-display">加载中...</div>
        <div id="lock-control"><div id="lock-btn" class="lock-btn" title="锁定记录节点的坐标">🔓</div></div>

        <div id="sidebar">
            <div class="panel-header">时序图谱编辑器 PRO</div>
            <div class="tab-nav">
                <button class="tab-btn active" data-tab="tab-edit">🎯 标注与编辑</button>
                <button class="tab-btn" data-tab="tab-factory">🏭 生产中心</button>
                <button class="tab-btn" data-tab="tab-engine">⚙️ 系统</button>
            </div>

            <div id="tab-edit" class="content-area active">
                <div class="ctrl"><label>标注文本内容</label><input type="text" id="time-text-input"></div>
                <div class="ctrl"><label>标注字号: <span id="time-size-val">42</span>px</label><input type="range" id="time-size-input" min="10" max="150" value="42"></div>
                <hr>
                <div id="nothing-selected" style="text-align:center; padding:20px; color:#94a3b8;">点击元素编辑属性</div>
                <div id="inspector" style="display:none; background:#f1f5f9; padding:15px; border-radius:10px;">
                    <div class="ctrl"><label>标签内容</label><textarea id="f-label" style="height:60px;"></textarea></div>
                    
                    <div class="ctrl">
                        <label>快捷颜色</label>
                        <div class="color-palette">
                            <div class="color-box" style="background:#D1D5DB" data-color="#D1D5DB" title="浅灰色"></div>
                            <div class="color-box" style="background:#93C5FD" data-color="#93C5FD" title="蓝色"></div>
                            <div class="color-box" style="background:#2DD4BF" data-color="#2DD4BF" title="绿色"></div>
                            <div class="color-box" style="background:#FBBF24" data-color="#FBBF24" title="黄色"></div>
                            <div class="color-box" style="background:#F97316" data-color="#F97316" title="橙色"></div>
                            <div class="color-box" style="background:#F87171" data-color="#F87171" title="红色"></div>
                        </div>
                    </div>

                    <div class="ctrl"><label>调色盘</label><input type="color" id="f-color"></div>
                    <div id="size-ctrl-wrapper" class="ctrl"><label>粗细/尺寸</label><input type="range" id="f-size" min="1" max="150"></div>
                    <div id="smooth-ctrl-wrapper" class="ctrl" style="display:none;"><label>边弯曲度</label><input type="range" id="f-smooth" min="-1.5" max="1.5" step="0.05"></div>
                    <button id="btn-del" class="action-btn danger">🗑️ 移除此项</button>
                </div>
                <p style="font-size: 11px; color: #94a3b8; text-align: center; margin-top: 10px;">快捷键: Cmd+Z (Mac) / Ctrl+Z (Win)</p>
            </div>

            <div id="tab-factory" class="content-area">
                <div class="ctrl" style="background:#f0f9ff; padding:15px; border-radius:10px; border:1px solid #bae6fd;">
                    <label style="font-weight:800; color:var(--accent);">🔍 实时密度控制</label>
                    <div class="ctrl"><label>采样跳数 (K-Hop)</label><input type="number" id="ui-k-hop" value="{init_k}" min="1" max="10"></div>
                    <div class="ctrl"><label>每跳限制 (空格分隔)</label><input type="text" id="ui-max-n" value="{init_max_n}"></div>
                    <button id="btn-re-sample" class="action-btn success">🔄 重新采样并应用</button>
                </div>
                <hr>
                <div class="ctrl">
                    <label>新增节点</label>
                    <input type="text" id="add-node-name" placeholder="输入名称...">
                    <div id="error-msg">⚠️ 该节点在当前帧已存在！</div>
                </div>
                <button id="btn-add-node" class="action-btn success">➕ 添加节点</button>
                <hr>
                <div class="ctrl"><label>建立关系</label>
                    <select id="edge-src" style="margin-bottom:5px;"></select>
                    <select id="edge-tgt"></select>
                    <input type="text" id="edge-label" placeholder="关系描述..." style="margin-top:5px;">
                </div>
                <button id="btn-add-edge" class="action-btn primary">🔗 建立连线</button>
            </div>

            <div id="tab-engine" class="content-area">
                <button id="btn-toggle-physics" class="action-btn warning">⚡ 开启防重叠布局引擎</button>
                <hr>
                <div class="ctrl-group">
                    <label>图像导出</label>
                    <div style="display:flex; gap:10px; margin-top:5px;">
                        <button id="btn-save-current-png" class="action-btn success" style="flex:1;">📷 保存当前图像</button>
                        <button id="btn-save-all-png" class="action-btn primary" style="flex:1;">📽️ 保存所有时间图像</button>
                    </div>
                </div>
                <div id="export-preview-container">
                    <span class="preview-tag">实时保存预览</span>
                    <canvas id="export-preview-canvas"></canvas>
                </div>
                <hr>
                <button id="btn-record-pos" class="action-btn primary">📌 1. 记录当前布局</button>
                <button id="btn-align-pos" class="action-btn primary" style="margin-top:10px;">📏 2. 对齐记录实体的坐标</button>
                <button id="btn-export-jsonl" class="action-btn primary" style="margin-top:10px;">📄 导出 JSONL</button>
            </div>
        </div>

        <div class="nav-panel">
            <button class="nav-arrow" id="btn-prev" title="上一帧">
                <svg viewBox="0 0 24 24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
            </button>
            <div id="nav-info" style="font-weight:700; color:#64748b; font-size:14px;">1 / 1</div>
            <button class="nav-arrow" id="btn-next" title="下一帧">
                <svg viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
            </button>
        </div>

        <script>
        let temporalData = {json_frames};
        const rawTriplesPool = {json_raw};
        const CENTER_NODE_ID = "{center_node}";
        let curFrameIdx = 0, curId = null, isNode = false;
        let savedPositions = {{}}, physicsEnabled = false, isLocked = false, hasRecorded = false;

        const NODE_DEFAULTS = {{
            shape: "circle", widthConstraint: 90, heightConstraint: 90, borderWidth: 2, 
            color: {{ background: "#D1D5DB", border: "#97999C", highlight: {{ background: "#D1D5DB", border: "#97999C" }}, hover: {{ background: "#D1D5DB", border: "#97999C" }} }},
            font: {{ size: 22, color: "#000000", multi: "html", face: "Arial" }}
        }};
        const EDGE_DEFAULTS = {{
            width: 2.5, arrows: {{ to: {{ enabled: true, scaleFactor: 1.5 }} }},
            color: {{ color: "#000000", highlight: "#000000", hover: "#000000" }},
            font: {{ align: 'top', size: 20, vadjust: -5, color: "#000000", strokeWidth: 6, strokeColor: "#ffffff", bold: true, face: "Arial" }}
        }};

        const getHexColorByDegree = (degree) => {{
            if (degree <= 1) return "#D1D5DB";
            if (degree <= 2) return "#93C5FD";
            if (degree <= 3) return "#2DD4BF";
            if (degree <= 4) return "#FBBF24";
            if (degree <= 5) return "#F97316";
            return "#F87171";
        }};

        const getBfsNeighbors = (triples, center, k, limits) => {{
            let relevant = new Set([center]);
            let layer = new Set([center]);
            let adj = {{}};
            triples.forEach(([h, r, t]) => {{
                if(!adj[h]) adj[h] = new Set(); if(!adj[t]) adj[t] = new Set();
                adj[h].add(t); adj[t].add(h);
            }});
            for (let i = 0; i < k; i++) {{
                let nextLayer = new Set();
                let limit = limits[i] !== undefined ? limits[i] : 10;
                layer.forEach(node => {{
                    if(adj[node]) {{
                        let neighbors = Array.from(adj[node]).filter(n => !relevant.has(n));
                        neighbors = neighbors.sort(() => 0.5 - Math.random()).slice(0, limit);
                        neighbors.forEach(n => nextLayer.add(n));
                    }}
                }});
                nextLayer.forEach(n => relevant.add(n));
                layer = nextLayer;
            }}
            return relevant;
        }};

        document.getElementById('btn-re-sample').onclick = () => {{
            pushHistory();
            const k = parseInt(document.getElementById('ui-k-hop').value);
            const limits = document.getElementById('ui-max-n').value.trim().split(/[\\s,]+/).map(Number).filter(n => !isNaN(n));
            
            const globalPosMap = {{}};
            temporalData.forEach(frame => {{
                frame.nodes.forEach(n => {{
                    if (!globalPosMap[n.id]) globalPosMap[n.id] = {{ x: n.x, y: n.y }};
                }});
            }});

            Object.keys(rawTriplesPool).forEach((date, idx) => {{
                const triples = rawTriplesPool[date];
                const frameRelevant = getBfsNeighbors(triples, CENTER_NODE_ID, k, limits);
                const existingNodesInFrame = temporalData[idx].nodes;
                const existingNodeIds = new Set(existingNodesInFrame.map(n => n.id));
                
                const filteredEdges = triples.filter(([h,r,t]) => frameRelevant.has(h) && frameRelevant.has(t));
                let localDegrees = {{}};
                filteredEdges.forEach(([h,r,t]) => {{
                   localDegrees[h] = (localDegrees[h]||0) + 1;
                   localDegrees[t] = (localDegrees[t]||0) + 1;
                }});

                frameRelevant.forEach(nodeId => {{
                    const deg = localDegrees[nodeId] || 0;
                    const solidColor = getHexColorByDegree(deg);
                    const colorCfg = {{ 
                        background: solidColor, border: "#97999C", 
                        highlight: {{ background: solidColor, border: "#97999C" }}, 
                        hover: {{ background: solidColor, border: "#97999C" }} 
                    }};

                    if (!existingNodeIds.has(nodeId)) {{
                        if (!globalPosMap[nodeId]) globalPosMap[nodeId] = {{ x: (Math.random() - 0.5) * 1800, y: (Math.random() - 0.5) * 1800 }};
                        temporalData[idx].nodes.push({{
                            id: nodeId, label: "<b>" + nodeId + "</b>", 
                            x: globalPosMap[nodeId].x, y: globalPosMap[nodeId].y,
                            hidden: false, ...NODE_DEFAULTS,
                            color: colorCfg
                        }});
                    }} else {{
                        const nObj = existingNodesInFrame.find(n => n.id === nodeId);
                        if(nObj) {{
                            nObj.hidden = false;
                            nObj.color = colorCfg;
                        }}
                    }}
                }});
                
                temporalData[idx].nodes.forEach(n => {{
                    if (!frameRelevant.has(n.id)) {{
                        n.hidden = true;
                        n.color = {{ 
                            background: "#F3F4F6", border: "#97999C", 
                            highlight: {{ background: "#F3F4F6", border: "#97999C" }}, 
                            hover: {{ background: "#F3F4F6", border: "#97999C" }} 
                        }};
                    }}
                }});
                
                const pairTotals = {{}};
                filteredEdges.forEach(([h,r,t]) => {{
                    const key = [h, t].sort().join('|');
                    pairTotals[key] = (pairTotals[key] || 0) + 1;
                }});

                const pairIndices = {{}};
                temporalData[idx].edges = filteredEdges.map(([h,r,t]) => {{
                    const key = [h, t].sort().join('|');
                    const total = pairTotals[key];
                    const occurrence = pairIndices[key] || 0;
                    pairIndices[key] = occurrence + 1;

                    let smooth = {{ enabled: false }};
                    if (total > 1) {{
                        const side = 'curvedCW';
                        const r_val = 0.15 * (occurrence + 1); 
                        smooth = {{ enabled: true, type: side, roundness: r_val }};
                    }}
                    return {{ from: h, to: t, label: r, smooth: smooth, ...EDGE_DEFAULTS }};
                }});
            }});
            
            updateFrame(curFrameIdx, true);
        }};

        let historyStack = [];
        const pushHistory = () => {{
            if (historyStack.length > 30) historyStack.shift();
            historyStack.push(JSON.stringify(temporalData));
        }};
        const undo = () => {{
            if (historyStack.length === 0) return;
            temporalData = JSON.parse(historyStack.pop());
            updateFrame(curFrameIdx, true);
        }};
        window.addEventListener('keydown', (e) => {{ if ((e.ctrlKey || e.metaKey) && e.key === 'z') {{ e.preventDefault(); undo(); }} }});

        const syncToMemory = () => {{
            const nodesWithPos = nodes.get().map(n => {{
                const pos = network.getPositions([n.id])[n.id];
                return {{ ...n, x: pos?.x || n.x, y: pos?.y || n.y }};
            }});
            if (temporalData[curFrameIdx]) {{
                temporalData[curFrameIdx].nodes = nodesWithPos;
                temporalData[curFrameIdx].edges = edges.get();
            }}
        }};

        const updateExportPreview = () => {{
            const c = document.querySelector('canvas'), p = document.getElementById('export-preview-canvas');
            if (!c || !p) return;
            const ctx = p.getContext('2d');
            p.width = c.width; p.height = c.height;
            ctx.fillStyle = '{self.bgcolor}'; ctx.fillRect(0, 0, p.width, p.height);
            ctx.drawImage(c, 0, 0);
            const tDate = temporalData[curFrameIdx].date, tSize = document.getElementById('time-size-input').value;
            ctx.fillStyle = '#1e293b'; ctx.font = 'bold ' + tSize + 'px Arial';
            ctx.fillText(tDate, 50, 90 + 40);
        }};

        const updateSelectors = () => {{
            const allNodes = nodes.get(), s = document.getElementById('edge-src'), t = document.getElementById('edge-tgt');
            if(!s || !t) return;
            s.innerHTML = ''; t.innerHTML = '';
            allNodes.forEach(n => {{ if(!n.hidden) {{
                let label = n.label.replace(/<[^>]*>/g, '');
                let o = `<option value="${{n.id}}">${{label}}</option>`;
                s.innerHTML += o; t.innerHTML += o;
            }} }});
        }};

        const updateFrame = (i, skipSync = false) => {{
            if (!temporalData[i]) return;
            if (!skipSync) syncToMemory();
            
            curFrameIdx = i; const d = temporalData[i];
            document.getElementById('time-display').innerText = d.date;
            document.getElementById('time-text-input').value = d.date;
            document.getElementById('nav-info').innerText = (i+1) + " / " + temporalData.length;
            const processedNodes = d.nodes.map(n => ({{ ...n, fixed: (isLocked && savedPositions[n.id]) ? {{ x: true, y: true }} : {{ x: false, y: false }} }}));
            nodes.clear(); nodes.add(processedNodes); edges.clear(); edges.add(d.edges);
            updateSelectors();
            setTimeout(() => {{ network.moveTo({{ position: network.getPositions([CENTER_NODE_ID])[CENTER_NODE_ID] || {{x:0, y:0}}, animation: {{ duration: 500 }} }}); }}, 100);
        }};

        window.onload = function() {{
            if (typeof network === 'undefined') return;
            network.on("afterDrawing", updateExportPreview);
            network.on("dragEnd", () => {{ pushHistory(); syncToMemory(); }});

            const lBtn = document.getElementById('lock-btn');
            lBtn.onclick = () => {{
                if (!hasRecorded) return;
                isLocked = !isLocked; lBtn.innerHTML = isLocked ? "🔒" : "🔓"; lBtn.classList.toggle('locked', isLocked);
                nodes.update(nodes.get().map(n => ({{ id: n.id, fixed: (isLocked && savedPositions[n.id]) ? {{ x: true, y: true }} : {{ x: false, y: false }} }})));
            }};

            document.getElementById('btn-toggle-physics').onclick = function() {{
                physicsEnabled = !physicsEnabled;
                this.innerText = physicsEnabled ? "🛑 锁定排版" : "⚡ 开启防重叠布局引擎";
                this.className = "action-btn " + (physicsEnabled ? "danger" : "warning");
                network.setOptions({{ 
                    physics: {{ 
                        enabled: physicsEnabled, solver: 'forceAtlas2Based', 
                        forceAtlas2Based: {{ gravitationalConstant: -1800, centralGravity: 0.1, springLength: 750, springConstant: 0.03, avoidOverlap: 1 }}, 
                        stabilization: {{ iterations: 200 }}, damping: 0.1
                    }}, 
                    edges: {{ smooth: physicsEnabled ? {{ enabled: true, type: 'dynamic' }} : {{ enabled: false }} }} 
                }});
            }};

            document.getElementById('btn-save-current-png').onclick = () => {{
                network.unselectAll();
                setTimeout(() => {{
                    const link = document.createElement('a'); link.href = document.getElementById('export-preview-canvas').toDataURL("image/png");
                    link.download = `{center_node}_${{temporalData[curFrameIdx].date}}.png`; link.click();
                }}, 50);
            }};

            document.getElementById('btn-save-all-png').onclick = async () => {{
                const originalIdx = curFrameIdx; network.unselectAll();
                for (let i = 0; i < temporalData.length; i++) {{
                    updateFrame(i, true);
                    await new Promise(r => setTimeout(r, 600)); 
                    const link = document.createElement('a'); link.href = document.getElementById('export-preview-canvas').toDataURL("image/png");
                    link.download = `{center_node}_${{temporalData[i].date}}.png`; link.click();
                }}
                updateFrame(originalIdx, true); 
            }};

            document.getElementById('btn-record-pos').onclick = () => {{
                savedPositions = network.getPositions(); hasRecorded = true; lBtn.classList.add('active'); alert("坐标已记录。");
            }};

            document.getElementById('btn-align-pos').onclick = () => {{
                if (Object.keys(savedPositions).length === 0) return;
                pushHistory();
                temporalData.forEach(frame => {{ frame.nodes.forEach(n => {{ if (savedPositions[n.id]) {{ n.x = savedPositions[n.id].x; n.y = savedPositions[n.id].y; }} }}); }});
                updateFrame(curFrameIdx, true);
            }};

            document.getElementById('btn-prev').onclick = () => {{ if(curFrameIdx > 0) updateFrame(curFrameIdx-1); }};
            document.getElementById('btn-next').onclick = () => {{ if(curFrameIdx < temporalData.length-1) updateFrame(curFrameIdx+1); }};

            network.on("click", p => {{
                const insp = document.getElementById('inspector'), none = document.getElementById('nothing-selected'), sCtrl = document.getElementById('size-ctrl-wrapper'), smCtrl = document.getElementById('smooth-ctrl-wrapper');
                if (p.nodes.length === 1) {{
                    curId = p.nodes[0]; isNode = true; const d = nodes.get(curId);
                    insp.style.display = 'block'; none.style.display = 'none'; sCtrl.style.display = 'none'; smCtrl.style.display = 'none';
                    document.getElementById('f-label').value = d.label.replace(/<[^>]*>/g, '');
                    let bg = (typeof d.color==='string' ? d.color : d.color?.background) || "#D1D5DB";
                    document.getElementById('f-color').value = bg;
                }} else if (p.edges.length === 1) {{
                    curId = p.edges[0]; isNode = false; const d = edges.get(curId);
                    insp.style.display = 'block'; none.style.display = 'none'; sCtrl.style.display = 'block'; smCtrl.style.display = 'block';
                    document.getElementById('f-label').value = d.label || "";
                    document.getElementById('f-size').value = d.width || 2.5; 
                    document.getElementById('f-color').value = (typeof d.color==='string' ? d.color : d.color?.color) || "#000000";
                    let rd = d.smooth?.roundness || 0;
                    document.getElementById('f-smooth').value = d.smooth?.type === 'curvedCCW' ? -rd : rd;
                }} else {{ insp.style.display='none'; none.style.display='block'; curId=null; }}
            }});

            const pushUpdate = (manualColor) => {{
                if(!curId) return; pushHistory();
                const lv = document.getElementById('f-label').value, 
                      cv = manualColor || document.getElementById('f-color').value, 
                      sv = parseInt(document.getElementById('f-size').value), 
                      rv = parseFloat(document.getElementById('f-smooth').value);
                
                if (manualColor) document.getElementById('f-color').value = manualColor;

                if(isNode) {{
                    nodes.update({{ id: curId, label: "<b>"+lv+"</b>", color: {{ background: cv, border: '#97999C', highlight: cv, hover: cv }}, font: NODE_DEFAULTS.font }});
                }} else {{
                    edges.update({{ id: curId, label: lv, width: sv, color: {{ color: cv, highlight: cv, hover: cv }}, smooth: rv === 0 ? {{ enabled: false }} : {{ enabled: true, type: rv > 0 ? 'curvedCW' : 'curvedCCW', roundness: Math.abs(rv) }}, font: {{ ...EDGE_DEFAULTS.font, color: cv }} }});
                }}
                syncToMemory();
            }};
            
            document.querySelectorAll('.color-box').forEach(box => {{
                box.onclick = () => pushUpdate(box.dataset.color);
            }});

            ['f-label', 'f-color', 'f-size', 'f-smooth'].forEach(id => document.getElementById(id).oninput = () => pushUpdate());

            document.getElementById('btn-del').onclick = () => {{ if(!curId) return; pushHistory(); if(isNode) nodes.remove(curId); else edges.remove(curId); curId=null; document.getElementById('inspector').style.display='none'; syncToMemory(); updateSelectors(); }};
            
            document.getElementById('btn-add-node').onclick = () => {{ 
                const inputName = document.getElementById('add-node-name').value.trim();
                const err = document.getElementById('error-msg');
                
                if (!inputName) return;

                const currentNodes = nodes.get();
                // 查找当前帧中是否存在该 ID
                const existingInCurrentFrame = currentNodes.find(n => n.id === inputName);
                
                // 筛选机制：仅当节点存在且不为隐藏时，才判定为“重复”
                if (existingInCurrentFrame && !existingInCurrentFrame.hidden) {{
                    err.style.display = 'block';
                    setTimeout(() => err.style.display = 'none', 3000);
                    return;
                }}
                
                err.style.display = 'none';
                pushHistory();
                
                if (existingInCurrentFrame && existingInCurrentFrame.hidden) {{
                    // 如果节点存在但被隐藏了（可能是其他帧同步过来的或之前删掉的），则恢复它
                    nodes.update({{ 
                        id: inputName, 
                        hidden: false, 
                        ...NODE_DEFAULTS, 
                        label: "<b>"+inputName+"</b>" 
                    }});
                }} else {{
                    // 如果当前帧完全没有这个节点，则直接新增
                    nodes.add({{ 
                        id: inputName, 
                        label: "<b>"+inputName+"</b>", 
                        x: (Math.random() - 0.5) * 500, 
                        y: (Math.random() - 0.5) * 500, 
                        ...NODE_DEFAULTS 
                    }});
                }}
                
                document.getElementById('add-node-name').value = "";
                syncToMemory(); 
                updateSelectors(); 
            }};

            document.getElementById('btn-add-edge').onclick = () => {{ 
                let s=document.getElementById('edge-src').value, t=document.getElementById('edge-tgt').value, l=document.getElementById('edge-label').value; 
                if(s&&t) {{ pushHistory(); const existing = edges.get().filter(e => (e.from === s && e.to === t) || (e.from === t && e.to === s)); const rd = existing.length >= 1 ? 0.3 : 0.0; edges.add({{ from: s, to: t, label: l, smooth: rd > 0 ? {{ enabled: true, type: 'curvedCW', roundness: rd }} : {{ enabled: false }}, ...EDGE_DEFAULTS }}); }}
                syncToMemory(); 
            }};

            document.getElementById('btn-export-jsonl').onclick = () => {{
                syncToMemory(); let out = "";
                temporalData.forEach(frame => {{ 
                    frame.edges.forEach(e => {{ 
                        out += JSON.stringify({{ triple: [e.from, e.label||"", e.to], time: "Time: "+frame.date }}) + "\\n"; 
                    }}); 
                }});
                const link = document.createElement('a'); 
                link.href = URL.createObjectURL(new Blob([out], {{ type: 'application/x-jsonlines' }})); 
                link.download = `${{CENTER_NODE_ID}}_${{temporalData[curFrameIdx].date}}.jsonl`; 
                link.click();
            }};

            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.onclick = function() {{
                    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                    document.querySelectorAll('.content-area').forEach(c => c.classList.remove('active'));
                    this.classList.add('active'); document.getElementById(this.dataset.tab).classList.add('active');
                    if(this.dataset.tab === 'tab-factory') updateSelectors();
                }};
            }});

            const tDisp = document.getElementById('time-display'), tIn = document.getElementById('time-text-input'), tSize = document.getElementById('time-size-input');
            tIn.oninput = function() {{ tDisp.innerText = this.value; if(temporalData[curFrameIdx]) temporalData[curFrameIdx].date = this.value; updateExportPreview(); }};
            tSize.oninput = function() {{ tDisp.style.fontSize = this.value + 'px'; document.getElementById('time-size-val').innerText = this.value; updateExportPreview(); }};

            network.setOptions({{ physics: {{ enabled: false }}, interaction: {{ hover: true, multiselect: false, dragView: true }}, nodes: {{ font: {{ multi: 'html' }} }} }});
            updateFrame(0);
        }};
        </script>
        """
        return html_str.replace("</body>", editor_ui + "</body>")

# 使用示例
if __name__ == "__main__":
    # 模拟一个简单的数据文件
    mock_data = "temp_data.jsonl"
    with open(mock_data, "w", encoding="utf-8") as f:
        f.write(json.dumps({"triple": ["Alice", "knows", "Bob"], "time": "Time: 2023-01-01"}) + "\n")
        f.write(json.dumps({"triple": ["Bob", "works_at", "TechCorp"], "time": "Time: 2023-01-01"}) + "\n")
        f.write(json.dumps({"triple": ["Alice", "visited", "Paris"], "time": "Time: 2023-01-02"}) + "\n")

    kg = TemporalKnowledgeGraph(mock_data)
    data = kg.load()
    
    extractor = TemporalSubgraphExtractor(data)
    frames, master, raw, pool = extractor.extract("Alice", k_hop=2, max_neighbors=[5, 5], start_date="2023-01-01", num_frames=2)
    
    viz = TemporalVisualizer()
    viz.visualize(frames, master, raw, pool, "temporal_kg_expert.html")