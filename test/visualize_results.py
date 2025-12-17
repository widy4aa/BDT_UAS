"""
Visualization Script - Performance Test Results
Membuat grafik perbandingan performa Single DB vs Sharded DB
"""

import json
import matplotlib.pyplot as plt
import numpy as np

# Load test results
with open("performance_results.json", "r") as f:
    results = json.load(f)

single = results[0]
sharded = results[1]

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

# Create figure with subplots
fig = plt.figure(figsize=(16, 12))
fig.suptitle('Performance Comparison: Single DB vs Sharded DB (4 Nodes)\n300 Users | 100 Rooms | 6000 Operations', 
             fontsize=14, fontweight='bold', y=0.98)

# Color scheme
colors = {'single': '#e74c3c', 'sharded': '#27ae60'}

# ============================================
# 1. Throughput Comparison (Bar Chart)
# ============================================
ax1 = fig.add_subplot(2, 3, 1)
databases = ['Single DB', 'Sharded DB\n(4 Nodes)']
throughputs = [single['throughput'], sharded['throughput']]
bars1 = ax1.bar(databases, throughputs, color=[colors['single'], colors['sharded']], edgecolor='black', linewidth=1.2)
ax1.set_ylabel('Operations per Second')
ax1.set_title('Throughput Comparison')
ax1.set_ylim(0, max(throughputs) * 1.3)

# Add value labels
for bar, val in zip(bars1, throughputs):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{val:.1f}\nops/sec', ha='center', va='bottom', fontweight='bold', fontsize=9)

# Add improvement percentage
improvement = ((sharded['throughput'] - single['throughput']) / single['throughput'] * 100)
ax1.annotate(f'+{improvement:.1f}%', xy=(1, sharded['throughput']), 
             xytext=(1.3, sharded['throughput'] * 0.8),
             fontsize=11, fontweight='bold', color='green',
             arrowprops=dict(arrowstyle='->', color='green'))

# ============================================
# 2. Response Time Comparison (Grouped Bar)
# ============================================
ax2 = fig.add_subplot(2, 3, 2)
metrics = ['Avg', 'P50', 'P95', 'P99', 'Max']
single_times = [
    single['perf_stats']['avg'],
    single['perf_stats']['p50'],
    single['perf_stats']['p95'],
    single['perf_stats']['p99'],
    single['perf_stats']['max']
]
sharded_times = [
    sharded['perf_stats']['avg'],
    sharded['perf_stats']['p50'],
    sharded['perf_stats']['p95'],
    sharded['perf_stats']['p99'],
    sharded['perf_stats']['max']
]

x = np.arange(len(metrics))
width = 0.35

bars2a = ax2.bar(x - width/2, single_times, width, label='Single DB', color=colors['single'], edgecolor='black')
bars2b = ax2.bar(x + width/2, sharded_times, width, label='Sharded DB', color=colors['sharded'], edgecolor='black')

ax2.set_ylabel('Response Time (ms)')
ax2.set_title('Response Time Metrics')
ax2.set_xticks(x)
ax2.set_xticklabels(metrics)
ax2.legend()
ax2.set_ylim(0, max(single_times) * 1.2)

# Add value labels on top
for bar in bars2a:
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
             f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=7, color=colors['single'])
for bar in bars2b:
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
             f'{bar.get_height():.0f}', ha='center', va='bottom', fontsize=7, color=colors['sharded'])

# ============================================
# 3. Latency Improvement (Horizontal Bar)
# ============================================
ax3 = fig.add_subplot(2, 3, 3)
improvements = []
labels = ['Avg Response', 'P50 Response', 'P95 Response', 'P99 Response', 'Max Response']

for s, sh in zip(single_times, sharded_times):
    imp = ((s - sh) / s * 100)
    improvements.append(imp)

y_pos = np.arange(len(labels))
colors_imp = ['#27ae60' if x > 0 else '#e74c3c' for x in improvements]
bars3 = ax3.barh(y_pos, improvements, color=colors_imp, edgecolor='black')
ax3.set_yticks(y_pos)
ax3.set_yticklabels(labels)
ax3.set_xlabel('Improvement (%)')
ax3.set_title('Sharding Performance Gain')
ax3.axvline(x=0, color='black', linewidth=0.5)

for bar, val in zip(bars3, improvements):
    ax3.text(val + 1, bar.get_y() + bar.get_height()/2, 
             f'+{val:.1f}%', va='center', fontweight='bold', fontsize=9)

# ============================================
# 4. Response Time Distribution (Box Plot Style)
# ============================================
ax4 = fig.add_subplot(2, 3, 4)

# Create box plot data
box_data = [single['response_times'], sharded['response_times']]
bp = ax4.boxplot(box_data, tick_labels=['Single DB', 'Sharded DB'], patch_artist=True)

# Color the boxes
bp['boxes'][0].set_facecolor(colors['single'])
bp['boxes'][1].set_facecolor(colors['sharded'])

ax4.set_ylabel('Response Time (ms)')
ax4.set_title('Response Time Distribution')

# ============================================
# 5. Response Time Histogram
# ============================================
ax5 = fig.add_subplot(2, 3, 5)

# Plot histograms
ax5.hist(single['response_times'], bins=30, alpha=0.7, label='Single DB', 
         color=colors['single'], edgecolor='black')
ax5.hist(sharded['response_times'], bins=30, alpha=0.7, label='Sharded DB', 
         color=colors['sharded'], edgecolor='black')

ax5.set_xlabel('Response Time (ms)')
ax5.set_ylabel('Frequency')
ax5.set_title('Response Time Histogram')
ax5.legend()

# ============================================
# 6. Summary Stats Table
# ============================================
ax6 = fig.add_subplot(2, 3, 6)
ax6.axis('off')

# Create summary table
table_data = [
    ['Metric', 'Single DB', 'Sharded DB', 'Winner'],
    ['Throughput', f"{single['throughput']:.2f} ops/s", f"{sharded['throughput']:.2f} ops/s", 'Sharded'],
    ['Avg Response', f"{single['perf_stats']['avg']:.0f} ms", f"{sharded['perf_stats']['avg']:.0f} ms", 'Sharded'],
    ['P50 Response', f"{single['perf_stats']['p50']:.0f} ms", f"{sharded['perf_stats']['p50']:.0f} ms", 'Sharded'],
    ['P95 Response', f"{single['perf_stats']['p95']:.0f} ms", f"{sharded['perf_stats']['p95']:.0f} ms", 'Sharded'],
    ['P99 Response', f"{single['perf_stats']['p99']:.0f} ms", f"{sharded['perf_stats']['p99']:.0f} ms", 'Sharded'],
    ['Total Time', f"{single['total_duration']:.0f} sec", f"{sharded['total_duration']:.0f} sec", 'Sharded'],
]

table = ax6.table(cellText=table_data, loc='center', cellLoc='center',
                  colWidths=[0.25, 0.25, 0.25, 0.2])
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.2, 1.8)

# Style header row
for i in range(4):
    table[(0, i)].set_facecolor('#34495e')
    table[(0, i)].set_text_props(color='white', fontweight='bold')

# Style data rows
for i in range(1, len(table_data)):
    for j in range(4):
        if j == 3:  # Winner column
            table[(i, j)].set_facecolor('#d5f5e3')
        elif j == 1:  # Single DB
            table[(i, j)].set_facecolor('#fadbd8')
        elif j == 2:  # Sharded DB
            table[(i, j)].set_facecolor('#d4efdf')

ax6.set_title('Performance Summary', pad=20, fontweight='bold')

# Adjust layout
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save figure
plt.savefig('performance_comparison.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("Graph saved: performance_comparison.png")

# Show the figure
plt.show()
