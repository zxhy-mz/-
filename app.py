import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# 1. 网页标题与侧边栏设置 (这就是你的交互控制台)
st.title("🧬 DNA 多米诺阵列能量景观模拟器")
st.sidebar.header("核心物理参数调节")

# 创建交互式组件 (文本框和滑块)
topology_input = st.sidebar.text_input("阵列拓扑比例 (用英文逗号分隔)", "1, 3, 3, 3")
E0 = st.sidebar.slider("单体固有势垒 (E0)", min_value=5, max_value=30, value=10, step=1)
alpha = st.sidebar.slider("能量传递效率 (α)", min_value=0.0, max_value=1.0, value=0.7, step=0.05)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **提示:** 尝试拉动传递效率，观察右侧何时发生完全的**无势垒雪崩**。")

# 2. 解析输入并运行底层物理算法
try:
    topology = [int(x.strip()) for x in topology_input.split(',')]

    x_valid = [0]
    y_valid = [0]
    current_x = 0
    current_energy = 0

    for k in topology:
        peak_energy = k * E0
        valley_energy = peak_energy * alpha

        x_peak = current_x + (k / 2.0)
        x_valley = current_x + k

        if current_energy > peak_energy:
            x_valid.append(x_valley)
            y_valid.append(valley_energy)
        else:
            x_valid.append(x_peak)
            y_valid.append(peak_energy)
            x_valid.append(x_valley)
            y_valid.append(valley_energy)

        current_energy = valley_energy
        current_x = x_valley

    x_smooth = np.linspace(min(x_valid), max(x_valid), 800)
    spline = make_interp_spline(x_valid, y_valid, k=2)
    y_smooth = spline(x_smooth)

    # 3. 在网页上实时绘制图表
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    ax.plot(x_smooth, y_smooth, linewidth=3, color='#d62728', label='Energy Envelope')
    ax.scatter(x_valid, y_valid, color='black', zorder=5, label='Physical Anchors')

    # 填充颜色增加高级感
    ax.fill_between(x_smooth, y_smooth, 0, color='#d62728', alpha=0.1)

    ax.set_title(f'Topology: {topology} | Efficiency: {alpha}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Cumulative Flipped Nodes', fontsize=12)
    ax.set_ylabel('Total System Energy', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()

    # 将图像推送到 Streamlit 网页
    st.pyplot(fig)

    # 提供数据下载按钮
    df = pd.DataFrame({'x': x_smooth, 'y': y_smooth})
    st.download_button("下载 CSV 数据用于 Origin", df.to_csv(index=False), "avalanche_data.csv")

except Exception as e:
    st.error("拓扑输入格式有误，请确保输入的是数字加逗号，例如: 1, 2, 3, 2, 1")