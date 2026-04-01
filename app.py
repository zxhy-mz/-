import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# 1. 网页标题与侧边栏设置 (去除了 layout="wide"，使页面居中且紧凑)
st.set_page_config(page_title="DNA 多米诺阵列物理仿真")
st.title("🧬 DNA 多米诺阵列能量景观")
st.sidebar.header("核心物理参数调节")

# 交互式组件：将 m 和 n 改为数字输入框，彻底解除大小限制
m = st.sidebar.number_input("短边行数 (m) - 决定最高势垒", min_value=1, value=2, step=1)
n = st.sidebar.number_input("长边列数 (n) - 决定总跨度", min_value=1, value=4, step=1)
E0 = st.sidebar.slider("单体固有势垒 (E0)", min_value=5, max_value=20, value=10, step=1)
alpha = st.sidebar.slider("能量传递效率 (α)", min_value=0.0, max_value=1.0, value=0.70, step=0.01)

# 2. 严格按“奇数激增法则”生成物理拓扑
actual_m = min(m, n)
actual_n = max(m, n)
total_stages = actual_m + actual_n - 1

topology = []
for k in range(1, total_stages + 1):
    depth = min(k, total_stages - k + 1, actual_m)
    nodes = 2 * depth - 1  # 奇数倍激增法则
    topology.append(nodes)

# 智能折叠超长序列展示
if len(topology) > 15:
    display_seq = f"[{', '.join(map(str, topology[:5]))}, ..., {', '.join(map(str, topology[-5:]))}]"
else:
    display_seq = str(topology)

st.markdown(
    f"**阵列规模**: `{actual_m} x {actual_n}` | **最高并发节点**: `{max(topology)}` | **拓扑序列**: {display_seq}")

# 3. 能量包络线物理计算
x_anchors = [0]
y_anchors = [0]
current_x = 0
current_energy = 0

for k_nodes in topology:
    peak_energy = k_nodes * E0
    valley_energy = peak_energy * alpha

    x_peak = current_x + (k_nodes / 2.0)
    x_valley = current_x + k_nodes

    if current_energy > peak_energy:
        # 势垒被淹没 (顺畅雪崩)
        x_anchors.append(x_valley)
        y_anchors.append(valley_energy)
    else:
        # 受激爬坡
        x_anchors.append(x_peak)
        y_anchors.append(peak_energy)
        x_anchors.append(x_valley)
        y_anchors.append(valley_energy)

    current_energy = valley_energy
    current_x = x_valley

# 4. 样条插值生成平滑曲线
x_anchors = np.array(x_anchors)
y_anchors = np.array(y_anchors)

# 防止数据点过少导致插值报错
if len(x_anchors) > 3:
    x_smooth = np.linspace(x_anchors.min(), x_anchors.max(), 800)
    spline = make_interp_spline(x_anchors, y_anchors, k=2)
    y_smooth = spline(x_smooth)
else:
    x_smooth = x_anchors
    y_smooth = y_anchors

# 5. 在网页上绘制高清纯净图表 (去除了所有背景阴影区块)
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)  # 进一步缩小画布比例，显得更精致
ax.plot(x_smooth, y_smooth, linewidth=2.5, color='#d62728', label='Energy Envelope')
ax.scatter(x_anchors, y_anchors, color='black', s=25, zorder=5, label='Physical Anchors')

ax.set_title(f'Energy Landscape ({actual_m}x{actual_n} Array, alpha={alpha:.2f})', fontsize=12, fontweight='bold')
ax.set_xlabel('Cumulative Flipped Nodes (Reaction Coordinate)', fontsize=10)
ax.set_ylabel('Total System Energy', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.4)
ax.legend(loc='upper right', fontsize=9)
fig.tight_layout()

# 将图像推送到网页，取消强制拉伸以保持原生精细度
st.pyplot(fig, use_container_width=False)

# 6. 一键导出 CSV 功能
df = pd.DataFrame({'Reaction_Coordinate_X': x_smooth, 'System_Energy_Y': y_smooth})
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 下载 CSV 数据",
    data=csv_data,
    file_name=f'Domino_{actual_m}x{actual_n}_Energy.csv',
    mime='text/csv',
)