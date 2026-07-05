# -*- coding: utf-8 -*-
"""
plot_results.py —— 读取 C++ 输出的 CSV 文件, 绘制测线分布图
任务 1: 单线剖面覆盖示意图 + 水深/覆盖宽度/重叠率变化曲线
任务 2: 全域测线分布俯视图 + 覆盖宽度随位置变化曲线
"""
import csv
import math
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import matplotlib.font_manager as fm

# ---- 中文字体设置 ----
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'output')
PLOT_DIR   = os.path.join(os.path.dirname(__file__), '..', 'plot')
os.makedirs(PLOT_DIR, exist_ok=True)

NM = 1852.0  # 1 海里

# ================================================================
#  读取 CSV 工具函数
# ================================================================
def read_csv(path):
    """读取 CSV, 返回表头 + 数据行列表"""
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    return rows

def parse_overlap(s):
    """解析重叠率字符串, 返回 float 或 None"""
    if s == '-' or s == '' or s.strip() == '-':
        return None
    s = s.strip().rstrip('%')
    try:
        return float(s)
    except ValueError:
        return None

# ================================================================
#  任务 1 可视化
# ================================================================
def plot_task1():
    rows = read_csv(os.path.join(OUTPUT_DIR, 'task1_result.csv'))
    # 跳过表头, 解析数据
    data = []
    for r in rows[1:]:
        if len(r) < 7 or r[0] == '':
            continue
        try:
            idx = int(r[0])
        except ValueError:
            break
        x       = float(r[1])
        depth_v = float(r[2])
        xL      = float(r[3])
        xR      = float(r[4])
        W       = float(r[5])
        ov      = parse_overlap(r[6])
        data.append(dict(idx=idx, x=x, depth=depth_v, xL=xL, xR=xR, W=W, ov=ov))

    xs      = [d['x'] for d in data]
    depths  = [d['depth'] for d in data]
    widths  = [d['W'] for d in data]
    overlaps = [d['ov'] for d in data]
    xLs     = [d['xL'] for d in data]
    xRs     = [d['xR'] for d in data]

    # ---- 图 1: 覆盖剖面示意图 ----
    fig, ax = plt.subplots(figsize=(14, 7))

    # 海底斜面
    x_seafloor = np.linspace(-1000, 1000, 200)
    alpha = math.radians(1.5)
    D0 = 70.0
    y_seafloor = D0 - x_seafloor * math.tan(alpha)
    ax.plot(x_seafloor, y_seafloor, 'b-', linewidth=2, label='海底斜面')
    ax.fill_between(x_seafloor, y_seafloor, 0, alpha=0.08, color='blue')

    # 每条测线的覆盖条带 (在海面上用竖线标示船位, 用水平线标示覆盖范围)
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(data)))
    for i, d in enumerate(data):
        # 船位竖线
        ax.plot([d['x'], d['x']], [0, d['depth']], '--', color=colors[i],
                linewidth=0.8, alpha=0.6)
        # 覆盖范围 (在海面上方用半透明条带)
        rect = Rectangle((d['xL'], -8 + i * 0.3), d['xR'] - d['xL'], 2,
                         facecolor=colors[i], alpha=0.5, edgecolor=colors[i],
                         linewidth=0.5)
        ax.add_patch(rect)
        # 标注
        ax.annotate(f'#{d["idx"]}', xy=(d['x'], -8 + i * 0.3 + 1),
                    fontsize=7, ha='center', va='center')

    ax.set_xlabel('沿坡度方向位置 x (m)', fontsize=12)
    ax.set_ylabel('深度 (m)', fontsize=12)
    ax.set_title('任务 1: 单线剖面覆盖示意图 (D0=70m, α=1.5°, 半开角60°)',
                 fontsize=14)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_xlim(-1050, 1050)
    ax.set_ylim(-15, 100)
    ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='-')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'task1_profile.png'), dpi=150)
    plt.close(fig)

    # ---- 图 2: 水深 / 覆盖宽度 / 重叠率 变化曲线 ----
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # 水深
    axes[0].plot(xs, depths, 'o-', color='steelblue', markersize=6, linewidth=2)
    axes[0].set_ylabel('海水深度 (m)', fontsize=11)
    axes[0].set_title('任务 1: 水深、覆盖宽度、重叠率随测线位置的变化',
                      fontsize=14)
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=70, color='gray', linewidth=0.5, linestyle='--',
                    label='D0=70m')
    axes[0].legend(fontsize=9)
    for i, (x, d) in enumerate(zip(xs, depths)):
        axes[0].annotate(f'{d:.1f}', (x, d), textcoords='offset points',
                         xytext=(0, 8), ha='center', fontsize=8)

    # 覆盖宽度
    axes[1].plot(xs, widths, 's-', color='darkorange', markersize=6, linewidth=2)
    axes[1].set_ylabel('覆盖宽度 W (m)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    for i, (x, w) in enumerate(zip(xs, widths)):
        axes[1].annotate(f'{w:.1f}', (x, w), textcoords='offset points',
                         xytext=(0, 8), ha='center', fontsize=8)

    # 重叠率
    valid_x = [x for x, o in zip(xs, overlaps) if o is not None]
    valid_o = [o for o in overlaps if o is not None]
    colors_ov = ['green' if 10 <= o <= 20 else 'red' for o in valid_o]
    axes[2].bar(valid_x, valid_o, width=120, color=colors_ov, alpha=0.7,
                edgecolor='black', linewidth=0.5)
    axes[2].axhspan(10, 20, alpha=0.15, color='green', label='目标区间 10%~20%')
    axes[2].axhline(y=10, color='green', linewidth=1, linestyle='--')
    axes[2].axhline(y=20, color='green', linewidth=1, linestyle='--')
    axes[2].axhline(y=0,  color='red',   linewidth=1, linestyle='--',
                    label='零重叠(盲区)')
    axes[2].set_ylabel('重叠率 (%)', fontsize=11)
    axes[2].set_xlabel('测线位置 x (m)', fontsize=12)
    axes[2].legend(fontsize=9)
    axes[2].grid(True, alpha=0.3)
    for x, o in zip(valid_x, valid_o):
        axes[2].annotate(f'{o:.1f}%', (x, o), textcoords='offset points',
                         xytext=(0, 5), ha='center', fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'task1_curves.png'), dpi=150)
    plt.close(fig)
    print('[任务1] 可视化完成: task1_profile.png, task1_curves.png')

# ================================================================
#  任务 2 可视化
# ================================================================
def plot_task2():
    rows = read_csv(os.path.join(OUTPUT_DIR, 'task2_result.csv'))
    data = []
    for r in rows[1:]:
        if len(r) < 7 or r[0] == '':
            continue
        try:
            idx = int(r[0])
        except ValueError:
            break
        x       = float(r[1])
        depth_v = float(r[2])
        xL      = float(r[3])
        xR      = float(r[4])
        W       = float(r[5])
        ov      = parse_overlap(r[6])
        data.append(dict(idx=idx, x=x, depth=depth_v, xL=xL, xR=xR, W=W, ov=ov))

    xs      = [d['x'] for d in data]
    depths  = [d['depth'] for d in data]
    widths  = [d['W'] for d in data]
    xLs     = [d['xL'] for d in data]
    xRs     = [d['xR'] for d in data]
    n       = len(data)

    x_min = -2 * NM
    x_max =  2 * NM
    y_min = -1 * NM  # 南
    y_max =  1 * NM  # 北

    # ---- 图 1: 测线分布俯视图 ----
    fig, ax = plt.subplots(figsize=(16, 6))

    # 测区边界
    ax.add_patch(Rectangle((x_min, y_min), x_max - x_min, y_max - y_min,
                           fill=False, edgecolor='black', linewidth=2))
    ax.text(x_min + 50, y_max - 100, '测区 (4海里×2海里)',
            fontsize=10, va='top')

    # 每条测线的覆盖条带
    colors = plt.cm.coolwarm(np.linspace(0, 1, n))
    for i, d in enumerate(data):
        # 覆盖条带
        rect = Rectangle((d['xL'], y_min), d['xR'] - d['xL'], y_max - y_min,
                         facecolor=colors[i], alpha=0.25,
                         edgecolor=colors[i], linewidth=0.3)
        ax.add_patch(rect)
        # 测线本身
        ax.plot([d['x'], d['x']], [y_min, y_max], '-', color=colors[i],
                linewidth=1.0, alpha=0.8)
        # 标号 (每隔几条标一次, 避免拥挤)
        if i % 5 == 0 or i == n - 1:
            ax.annotate(f'#{d["idx"]}', xy=(d['x'], y_max + 100),
                        fontsize=8, ha='center', va='bottom',
                        color='black', rotation=45)

    ax.set_xlabel('东西方向 (沿坡度) x (m)', fontsize=12)
    ax.set_ylabel('南北方向 (测线方向) y (m)', fontsize=12)
    ax.set_title(f'任务 2: 全域最优测线分布俯视图 (共{n}条, 总长{n*2:.0f}海里, '
                 f'重叠率均卡10%下限)', fontsize=14)
    ax.set_xlim(x_min - 200, x_max + 200)
    ax.set_ylim(y_min - 300, y_max + 300)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'task2_overview.png'), dpi=150)
    plt.close(fig)

    # ---- 图 2: 覆盖宽度 & 水深 随位置变化 ----
    fig, ax1 = plt.subplots(figsize=(14, 6))

    color1 = 'steelblue'
    ax1.plot(xs, widths, 'o-', color=color1, markersize=4, linewidth=1.5,
             label='覆盖宽度 W')
    ax1.set_xlabel('测线位置 x (m)', fontsize=12)
    ax1.set_ylabel('覆盖宽度 W (m)', fontsize=12, color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    color2 = 'crimson'
    ax2.plot(xs, depths, 's--', color=color2, markersize=4, linewidth=1.5,
             label='水深 D')
    ax2.set_ylabel('水深 D (m)', fontsize=12, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right',
               fontsize=10)
    ax1.set_title('任务 2: 覆盖宽度与水深随测线位置的变化 (深→浅)', fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'task2_width_depth.png'), dpi=150)
    plt.close(fig)

    # ---- 图 3: 测线间距分布 ----
    fig, ax = plt.subplots(figsize=(14, 5))
    spacings = [xs[i+1] - xs[i] for i in range(n - 1)]
    ax.bar(range(1, n), spacings, color='teal', alpha=0.7, edgecolor='black',
           linewidth=0.3)
    ax.set_xlabel('测线序号 (第 i → 第 i+1 条)', fontsize=12)
    ax.set_ylabel('相邻测线间距 (m)', fontsize=12)
    ax.set_title('任务 2: 相邻测线间距分布 (从深水到浅水, 间距递减)', fontsize=14)
    ax.grid(True, alpha=0.3, axis='y')
    for i, sp in enumerate(spacings):
        ax.annotate(f'{sp:.0f}', (i + 1, sp), textcoords='offset points',
                    xytext=(0, 3), ha='center', fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOT_DIR, 'task2_spacing.png'), dpi=150)
    plt.close(fig)

    print(f'[任务2] 可视化完成: task2_overview.png, task2_width_depth.png, '
          f'task2_spacing.png (共{n}条测线)')

# ================================================================
if __name__ == '__main__':
    plot_task1()
    plot_task2()
    print('\n所有可视化图已保存至 plot/ 目录')
