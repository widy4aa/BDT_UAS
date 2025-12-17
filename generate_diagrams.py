"""
Script untuk menghasilkan diagram-diagram untuk laporan
Basis Data Terdistribusi - Implementasi Database Sharding
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ConnectionPatch
import numpy as np
import os

# Buat folder untuk menyimpan diagram
os.makedirs('diagrams', exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10


def create_erd_diagram():
    """Gambar 3.1 - Entity Relationship Diagram (ERD)"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Colors
    entity_color = '#E3F2FD'
    entity_border = '#1976D2'
    pk_color = '#FFF3E0'
    fk_color = '#E8F5E9'
    
    def draw_entity(ax, x, y, width, height, title, attributes):
        """Draw an entity box with attributes"""
        # Main box
        rect = FancyBboxPatch((x, y), width, height, 
                               boxstyle="round,pad=0.02,rounding_size=0.1",
                               facecolor=entity_color, edgecolor=entity_border, linewidth=2)
        ax.add_patch(rect)
        
        # Title bar
        title_height = 0.6
        title_rect = FancyBboxPatch((x, y + height - title_height), width, title_height,
                                     boxstyle="round,pad=0.02,rounding_size=0.1",
                                     facecolor=entity_border, edgecolor=entity_border, linewidth=2)
        ax.add_patch(title_rect)
        ax.text(x + width/2, y + height - title_height/2, title, 
                ha='center', va='center', fontsize=12, fontweight='bold', color='white')
        
        # Attributes
        attr_y = y + height - title_height - 0.4
        for attr, attr_type, key_type in attributes:
            if key_type == 'PK':
                bg_color = pk_color
                prefix = '🔑 '
            elif key_type == 'FK':
                bg_color = fk_color
                prefix = '🔗 '
            else:
                bg_color = 'white'
                prefix = '   '
            
            attr_rect = plt.Rectangle((x + 0.1, attr_y - 0.25), width - 0.2, 0.4,
                                       facecolor=bg_color, edgecolor='#BDBDBD', linewidth=0.5)
            ax.add_patch(attr_rect)
            ax.text(x + 0.2, attr_y, f"{prefix}{attr}", ha='left', va='center', fontsize=9)
            ax.text(x + width - 0.2, attr_y, attr_type, ha='right', va='center', fontsize=8, color='#666')
            attr_y -= 0.5
        
        return (x + width/2, y + height), (x + width/2, y), (x, y + height/2), (x + width, y + height/2)
    
    # Draw entities
    # USER
    user_attrs = [
        ('id', 'BIGINT', 'PK'),
        ('username', 'VARCHAR(255)', ''),
        ('created_at', 'TIMESTAMP', '')
    ]
    user_points = draw_entity(ax, 1, 6, 3.5, 2.5, 'USER', user_attrs)
    
    # ROOM
    room_attrs = [
        ('id', 'BIGINT', 'PK'),
        ('codename', 'VARCHAR(8)', ''),
        ('type', 'VARCHAR(50)', ''),
        ('created_at', 'TIMESTAMP', '')
    ]
    room_points = draw_entity(ax, 9.5, 6, 3.5, 3, 'ROOM', room_attrs)
    
    # ROOM_MEMBER
    rm_attrs = [
        ('room_id', 'BIGINT', 'FK'),
        ('user_id', 'BIGINT', 'FK')
    ]
    rm_points = draw_entity(ax, 5.25, 7, 3.5, 2, 'ROOM_MEMBER', rm_attrs)
    
    # MESSAGE
    msg_attrs = [
        ('id', 'BIGINT', 'PK'),
        ('room_id', 'BIGINT', 'FK'),
        ('sender_id', 'BIGINT', 'FK'),
        ('content', 'TEXT', ''),
        ('created_at', 'TIMESTAMP', '')
    ]
    msg_points = draw_entity(ax, 5.25, 1.5, 3.5, 3.5, 'MESSAGE', msg_attrs)
    
    # Draw relationships
    # USER - ROOM_MEMBER
    ax.annotate('', xy=(5.25, 8), xytext=(4.5, 7.5),
                arrowprops=dict(arrowstyle='->', color='#1976D2', lw=2))
    ax.text(4.3, 8.2, '1', fontsize=10, fontweight='bold', color='#1976D2')
    ax.text(5.0, 8.5, 'N', fontsize=10, fontweight='bold', color='#1976D2')
    
    # ROOM_MEMBER - ROOM
    ax.annotate('', xy=(9.5, 8), xytext=(8.75, 7.5),
                arrowprops=dict(arrowstyle='->', color='#1976D2', lw=2))
    ax.text(9.0, 8.5, 'N', fontsize=10, fontweight='bold', color='#1976D2')
    ax.text(9.7, 8.2, '1', fontsize=10, fontweight='bold', color='#1976D2')
    
    # MESSAGE - USER (sender)
    ax.annotate('', xy=(2.75, 6), xytext=(5.25, 3.5),
                arrowprops=dict(arrowstyle='->', color='#4CAF50', lw=2))
    ax.text(3.5, 4.5, 'sender_id', fontsize=8, color='#4CAF50', rotation=30)
    
    # MESSAGE - ROOM
    ax.annotate('', xy=(11.25, 6), xytext=(8.75, 3.5),
                arrowprops=dict(arrowstyle='->', color='#FF9800', lw=2))
    ax.text(9.5, 4.5, 'room_id', fontsize=8, color='#FF9800', rotation=-30)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=pk_color, edgecolor='#BDBDBD', label='🔑 Primary Key'),
        mpatches.Patch(facecolor=fk_color, edgecolor='#BDBDBD', label='🔗 Foreign Key'),
        mpatches.Patch(facecolor='#FFCDD2', edgecolor='#BDBDBD', label='⚡ Sharding Key (room_id)')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    # Title
    ax.text(7, 9.8, 'Gambar 3.1 Entity Relationship Diagram (ERD)', 
            ha='center', va='top', fontsize=14, fontweight='bold')
    ax.text(7, 9.4, 'Sistem Aplikasi Chat dengan Database Sharding', 
            ha='center', va='top', fontsize=11, style='italic', color='#666')
    
    # Sharding note
    ax.add_patch(FancyBboxPatch((4.5, 0.3), 5, 0.8, 
                                 boxstyle="round,pad=0.02,rounding_size=0.1",
                                 facecolor='#FFCDD2', edgecolor='#D32F2F', linewidth=2))
    ax.text(7, 0.7, '⚡ Tabel MESSAGE di-shard berdasarkan room_id % 4', 
            ha='center', va='center', fontsize=10, fontweight='bold', color='#D32F2F')
    
    plt.tight_layout()
    plt.savefig('diagrams/gambar_3_1_erd.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Gambar 3.1 ERD berhasil dibuat")


def create_architecture_diagram():
    """Gambar 3.2 - Arsitektur Fisik Sistem Terdistribusi"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 12))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors
    app_color = '#E8F5E9'
    proxy_color = '#FFF3E0'
    primary_shard_color = '#E3F2FD'
    shard_color = '#F3E5F5'
    
    def draw_box(ax, x, y, width, height, title, subtitle, color, border_color):
        rect = FancyBboxPatch((x, y), width, height,
                               boxstyle="round,pad=0.03,rounding_size=0.2",
                               facecolor=color, edgecolor=border_color, linewidth=2)
        ax.add_patch(rect)
        ax.text(x + width/2, y + height - 0.4, title, 
                ha='center', va='top', fontsize=11, fontweight='bold')
        if subtitle:
            ax.text(x + width/2, y + height - 0.8, subtitle, 
                    ha='center', va='top', fontsize=9, color='#666')
        return (x + width/2, y + height), (x + width/2, y)
    
    # Flask Application
    flask_box = draw_box(ax, 5, 10, 4, 1.5, '🌐 Flask Application', 'Port 5001', app_color, '#4CAF50')
    
    # ShardingSphere Proxy
    proxy_box = draw_box(ax, 4.5, 7, 5, 2, '⚙️ Apache ShardingSphere Proxy', 'Port 3307 | Query Router', proxy_color, '#FF9800')
    
    # Arrow Flask -> Proxy
    ax.annotate('', xy=(7, 9), xytext=(7, 10),
                arrowprops=dict(arrowstyle='->', color='#333', lw=2))
    ax.text(7.3, 9.5, 'SQL Query', fontsize=9, color='#666')
    
    # Shards
    shard_y = 2
    shard_height = 3.5
    
    # ds_0 (Primary)
    rect0 = FancyBboxPatch((0.5, shard_y), 3, shard_height,
                            boxstyle="round,pad=0.03,rounding_size=0.2",
                            facecolor=primary_shard_color, edgecolor='#1976D2', linewidth=3)
    ax.add_patch(rect0)
    ax.text(2, shard_y + shard_height - 0.3, '🗄️ PostgreSQL ds_0', ha='center', fontsize=10, fontweight='bold')
    ax.text(2, shard_y + shard_height - 0.7, 'PRIMARY SHARD', ha='center', fontsize=8, color='#1976D2', fontweight='bold')
    ax.text(2, shard_y + 2.2, '• users', ha='center', fontsize=9)
    ax.text(2, shard_y + 1.8, '• rooms', ha='center', fontsize=9)
    ax.text(2, shard_y + 1.4, '• room_members', ha='center', fontsize=9)
    ax.text(2, shard_y + 0.9, '• messages', ha='center', fontsize=9, fontweight='bold')
    ax.text(2, shard_y + 0.5, '(room_id % 4 = 0)', ha='center', fontsize=8, color='#666')
    
    # ds_1
    rect1 = FancyBboxPatch((3.8, shard_y), 2.5, shard_height,
                            boxstyle="round,pad=0.03,rounding_size=0.2",
                            facecolor=shard_color, edgecolor='#7B1FA2', linewidth=2)
    ax.add_patch(rect1)
    ax.text(5.05, shard_y + shard_height - 0.3, '🗄️ PostgreSQL ds_1', ha='center', fontsize=10, fontweight='bold')
    ax.text(5.05, shard_y + shard_height - 0.7, 'Shard 1', ha='center', fontsize=9, color='#7B1FA2')
    ax.text(5.05, shard_y + 1.5, '• messages', ha='center', fontsize=9, fontweight='bold')
    ax.text(5.05, shard_y + 1.0, '(room_id % 4 = 1)', ha='center', fontsize=8, color='#666')
    
    # ds_2
    rect2 = FancyBboxPatch((6.6, shard_y), 2.5, shard_height,
                            boxstyle="round,pad=0.03,rounding_size=0.2",
                            facecolor=shard_color, edgecolor='#7B1FA2', linewidth=2)
    ax.add_patch(rect2)
    ax.text(7.85, shard_y + shard_height - 0.3, '🗄️ PostgreSQL ds_2', ha='center', fontsize=10, fontweight='bold')
    ax.text(7.85, shard_y + shard_height - 0.7, 'Shard 2', ha='center', fontsize=9, color='#7B1FA2')
    ax.text(7.85, shard_y + 1.5, '• messages', ha='center', fontsize=9, fontweight='bold')
    ax.text(7.85, shard_y + 1.0, '(room_id % 4 = 2)', ha='center', fontsize=8, color='#666')
    
    # ds_3
    rect3 = FancyBboxPatch((9.4, shard_y), 2.5, shard_height,
                            boxstyle="round,pad=0.03,rounding_size=0.2",
                            facecolor=shard_color, edgecolor='#7B1FA2', linewidth=2)
    ax.add_patch(rect3)
    ax.text(10.65, shard_y + shard_height - 0.3, '🗄️ PostgreSQL ds_3', ha='center', fontsize=10, fontweight='bold')
    ax.text(10.65, shard_y + shard_height - 0.7, 'Shard 3', ha='center', fontsize=9, color='#7B1FA2')
    ax.text(10.65, shard_y + 1.5, '• messages', ha='center', fontsize=9, fontweight='bold')
    ax.text(10.65, shard_y + 1.0, '(room_id % 4 = 3)', ha='center', fontsize=8, color='#666')
    
    # Resource info
    ax.add_patch(FancyBboxPatch((12.2, shard_y), 1.5, shard_height,
                                 boxstyle="round,pad=0.02",
                                 facecolor='#FFEBEE', edgecolor='#D32F2F', linewidth=1))
    ax.text(12.95, shard_y + 3, '📊 Resource', ha='center', fontsize=9, fontweight='bold')
    ax.text(12.95, shard_y + 2.5, 'per Shard:', ha='center', fontsize=8)
    ax.text(12.95, shard_y + 1.8, '• 1 CPU', ha='center', fontsize=9)
    ax.text(12.95, shard_y + 1.3, '• 100MB', ha='center', fontsize=9)
    ax.text(12.95, shard_y + 0.9, '  RAM', ha='center', fontsize=9)
    
    # Arrows from Proxy to Shards
    arrows_data = [
        (7, 7, 2, shard_y + shard_height),
        (7, 7, 5.05, shard_y + shard_height),
        (7, 7, 7.85, shard_y + shard_height),
        (7, 7, 10.65, shard_y + shard_height)
    ]
    
    for start_x, start_y, end_x, end_y in arrows_data:
        ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle='->', color='#FF9800', lw=1.5,
                                   connectionstyle='arc3,rad=0'))
    
    # Docker Network
    docker_rect = FancyBboxPatch((0.2, 1.5), 13.6, 6.2,
                                  boxstyle="round,pad=0.05",
                                  facecolor='none', edgecolor='#2196F3', 
                                  linewidth=2, linestyle='--')
    ax.add_patch(docker_rect)
    ax.text(13.5, 7.5, '🐳 Docker Network', ha='right', fontsize=10, 
            color='#2196F3', fontweight='bold')
    
    # Title
    ax.text(7, 11.8, 'Gambar 3.2 Arsitektur Fisik Sistem Terdistribusi', 
            ha='center', fontsize=14, fontweight='bold')
    ax.text(7, 11.4, 'Apache ShardingSphere dengan 4 Shard PostgreSQL', 
            ha='center', fontsize=11, style='italic', color='#666')
    
    plt.tight_layout()
    plt.savefig('diagrams/gambar_3_2_arsitektur.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Gambar 3.2 Arsitektur berhasil dibuat")


def create_query_routing_diagram():
    """Gambar 3.3 - Alur Routing Query pada ShardingSphere"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colors
    step_colors = ['#E8F5E9', '#FFF3E0', '#E3F2FD', '#F3E5F5', '#FFEBEE']
    
    def draw_step_box(ax, x, y, width, height, step_num, title, content, color):
        rect = FancyBboxPatch((x, y), width, height,
                               boxstyle="round,pad=0.03,rounding_size=0.2",
                               facecolor=color, edgecolor='#333', linewidth=2)
        ax.add_patch(rect)
        
        # Step number circle
        circle = plt.Circle((x + 0.4, y + height - 0.4), 0.3, 
                            facecolor='#333', edgecolor='white', linewidth=2)
        ax.add_patch(circle)
        ax.text(x + 0.4, y + height - 0.4, str(step_num), 
                ha='center', va='center', fontsize=11, fontweight='bold', color='white')
        
        ax.text(x + 0.9, y + height - 0.4, title, 
                ha='left', va='center', fontsize=11, fontweight='bold')
        
        content_y = y + height - 1
        for line in content:
            ax.text(x + 0.3, content_y, line, ha='left', va='top', fontsize=9)
            content_y -= 0.4
    
    # Title
    ax.text(7, 9.7, 'Gambar 3.3 Alur Routing Query pada ShardingSphere', 
            ha='center', fontsize=14, fontweight='bold')
    
    # Step 1: Application
    draw_step_box(ax, 0.5, 7, 4, 2, 1, 'Aplikasi Flask',
                  ['Query: INSERT INTO messages', '(room_id=5, content=..., ...)'], step_colors[0])
    
    # Arrow 1->2
    ax.annotate('', xy=(5, 8), xytext=(4.5, 8),
                arrowprops=dict(arrowstyle='->', color='#4CAF50', lw=2))
    
    # Step 2: Parse
    draw_step_box(ax, 5, 7, 3.5, 2, 2, 'Parse SQL',
                  ['Identifikasi tabel: messages', 'Ekstrak kolom & nilai'], step_colors[1])
    
    # Arrow 2->3
    ax.annotate('', xy=(9, 8), xytext=(8.5, 8),
                arrowprops=dict(arrowstyle='->', color='#FF9800', lw=2))
    
    # Step 3: Extract Key
    draw_step_box(ax, 9, 7, 4.5, 2, 3, 'Extract Sharding Key',
                  ['Sharding Key: room_id', 'Nilai: 5'], step_colors[2])
    
    # Arrow 3->4
    ax.annotate('', xy=(11.25, 6.8), xytext=(11.25, 7),
                arrowprops=dict(arrowstyle='->', color='#2196F3', lw=2))
    
    # Step 4: Calculate
    draw_step_box(ax, 9, 4.3, 4.5, 2.2, 4, 'Kalkulasi Shard',
                  ['Algoritma: INLINE', 'Ekspresi: ds_${room_id % 4}', 
                   'Hasil: 5 % 4 = 1 → ds_1'], step_colors[3])
    
    # Arrow 4->5
    ax.annotate('', xy=(8.8, 5.4), xytext=(9, 5.4),
                arrowprops=dict(arrowstyle='->', color='#9C27B0', lw=2))
    
    # Step 5: Route
    draw_step_box(ax, 4, 4.3, 4.5, 2.2, 5, 'Route Query',
                  ['Target: PostgreSQL ds_1', 'Execute INSERT on ds_1'], step_colors[4])
    
    # Database boxes at bottom
    db_y = 1
    db_height = 2
    db_width = 2.8
    
    dbs = [
        ('ds_0', '#E0E0E0', 0.8),
        ('ds_1', '#C8E6C9', 4),  # Highlighted
        ('ds_2', '#E0E0E0', 7.2),
        ('ds_3', '#E0E0E0', 10.4)
    ]
    
    for db_name, color, x in dbs:
        rect = FancyBboxPatch((x, db_y), db_width, db_height,
                               boxstyle="round,pad=0.02",
                               facecolor=color, edgecolor='#333', 
                               linewidth=3 if db_name == 'ds_1' else 1)
        ax.add_patch(rect)
        ax.text(x + db_width/2, db_y + db_height - 0.4, f'🗄️ {db_name}', 
                ha='center', fontsize=10, fontweight='bold')
        ax.text(x + db_width/2, db_y + 0.8, 'PostgreSQL', 
                ha='center', fontsize=9, color='#666')
        
        if db_name == 'ds_1':
            ax.text(x + db_width/2, db_y + 0.3, '✓ TARGET', 
                    ha='center', fontsize=9, fontweight='bold', color='#4CAF50')
    
    # Arrow from Route to ds_1
    ax.annotate('', xy=(5.4, db_y + db_height), xytext=(6.25, 4.3),
                arrowprops=dict(arrowstyle='->', color='#4CAF50', lw=3,
                               connectionstyle='arc3,rad=0.2'))
    
    # Legend box
    legend_box = FancyBboxPatch((0.5, 0.5), 3.5, 3.2,
                                 boxstyle="round,pad=0.02",
                                 facecolor='#FAFAFA', edgecolor='#BDBDBD', linewidth=1)
    ax.add_patch(legend_box)
    ax.text(2.25, 3.5, '📋 Contoh Query:', ha='center', fontsize=10, fontweight='bold')
    ax.text(0.7, 3.0, 'INSERT INTO messages', ha='left', fontsize=8, family='monospace')
    ax.text(0.7, 2.6, '  (room_id, sender_id,', ha='left', fontsize=8, family='monospace')
    ax.text(0.7, 2.2, '   content)', ha='left', fontsize=8, family='monospace')
    ax.text(0.7, 1.8, 'VALUES (5, 1,', ha='left', fontsize=8, family='monospace')
    ax.text(0.7, 1.4, '  \'Hello World\')', ha='left', fontsize=8, family='monospace')
    ax.text(0.7, 0.8, '→ Routed to ds_1', ha='left', fontsize=9, fontweight='bold', color='#4CAF50')
    
    plt.tight_layout()
    plt.savefig('diagrams/gambar_3_3_query_routing.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Gambar 3.3 Query Routing berhasil dibuat")


def create_performance_comparison():
    """Gambar 4.1 - Grafik Perbandingan Kinerja"""
    # Data
    metrics = ['Throughput\n(ops/sec)', 'Avg Response\n(ms)', 'P50\n(ms)', 
               'P95\n(ms)', 'P99\n(ms)', 'Max Response\n(ms)']
    single_db = [25.66, 1925, 1899, 2300, 2675, 3836]
    sharded_db = [50.67, 968, 965, 1154, 1260, 1921]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Left: Bar chart comparison
    ax1 = axes[0]
    bars1 = ax1.bar(x - width/2, single_db, width, label='Single Database', color='#EF5350', edgecolor='#C62828')
    bars2 = ax1.bar(x + width/2, sharded_db, width, label='Sharded Database', color='#66BB6A', edgecolor='#388E3C')
    
    ax1.set_ylabel('Nilai', fontsize=12)
    ax1.set_title('Perbandingan Kinerja: Single DB vs Sharded DB', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics, fontsize=10)
    ax1.legend(loc='upper right', fontsize=10)
    ax1.set_yscale('log')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars1, single_db):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.0f}',
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    for bar, val in zip(bars2, sharded_db):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{val:.0f}',
                ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Right: Improvement percentage
    ax2 = axes[1]
    improvements = [
        ('Throughput', 97.4, '#4CAF50'),
        ('Avg Response', -49.7, '#4CAF50'),
        ('P50 Latency', -49.2, '#4CAF50'),
        ('P95 Latency', -49.8, '#4CAF50'),
        ('P99 Latency', -52.9, '#4CAF50'),
        ('Max Response', -49.9, '#4CAF50')
    ]
    
    y_pos = np.arange(len(improvements))
    values = [imp[1] for imp in improvements]
    colors = ['#66BB6A' if v > 0 else '#42A5F5' for v in values]
    
    bars = ax2.barh(y_pos, [abs(v) for v in values], color=colors, edgecolor='#333')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([imp[0] for imp in improvements], fontsize=11)
    ax2.set_xlabel('Persentase (%)', fontsize=12)
    ax2.set_title('Peningkatan Kinerja Sharded DB', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 110)
    ax2.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        label = f'+{val:.1f}%' if val > 0 else f'{val:.1f}%'
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                label, ha='left', va='center', fontsize=11, fontweight='bold',
                color='#2E7D32' if val > 0 else '#1565C0')
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#66BB6A', label='↑ Lebih Tinggi (Throughput)'),
        mpatches.Patch(facecolor='#42A5F5', label='↓ Lebih Rendah (Latency)')
    ]
    ax2.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    plt.suptitle('Gambar 4.1 Hasil Pengujian Kinerja Database Sharding', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig('diagrams/gambar_4_1_performance.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Gambar 4.1 Performance Comparison berhasil dibuat")


def create_shard_distribution():
    """Gambar 4.2 - Distribusi Data pada Shard"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Pie chart
    ax1 = axes[0]
    labels = ['ds_0\n(25 rooms)', 'ds_1\n(25 rooms)', 'ds_2\n(25 rooms)', 'ds_3\n(25 rooms)']
    sizes = [25, 25, 25, 25]
    colors = ['#42A5F5', '#66BB6A', '#FFA726', '#AB47BC']
    explode = (0.02, 0.02, 0.02, 0.02)
    
    wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
                                        autopct='%1.0f%%', shadow=True, startangle=90,
                                        textprops={'fontsize': 11})
    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    ax1.set_title('Distribusi Room per Shard', fontsize=14, fontweight='bold')
    
    # Right: Horizontal bar showing message distribution concept
    ax2 = axes[1]
    
    room_ids = ['Room 0, 4, 8...', 'Room 1, 5, 9...', 'Room 2, 6, 10...', 'Room 3, 7, 11...']
    shard_names = ['ds_0', 'ds_1', 'ds_2', 'ds_3']
    messages_per_shard = [1500, 1500, 1500, 1500]  # Simulated
    
    y_pos = np.arange(len(shard_names))
    bars = ax2.barh(y_pos, messages_per_shard, color=colors, edgecolor='#333', height=0.6)
    
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([f'{shard}\n({room})' for shard, room in zip(shard_names, room_ids)], fontsize=10)
    ax2.set_xlabel('Jumlah Pesan (estimasi)', fontsize=12)
    ax2.set_title('Distribusi Pesan Berdasarkan room_id % 4', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 2000)
    ax2.grid(axis='x', alpha=0.3)
    
    # Add formula annotation
    ax2.text(1000, 4.2, 'Algoritma: room_id % 4', ha='center', fontsize=12, 
             fontweight='bold', style='italic', color='#666')
    
    for bar, val in zip(bars, messages_per_shard):
        ax2.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2,
                f'{val}', ha='left', va='center', fontsize=11, fontweight='bold')
    
    plt.suptitle('Gambar 4.2 Distribusi Data pada Arsitektur Sharding', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig('diagrams/gambar_4_2_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Gambar 4.2 Shard Distribution berhasil dibuat")


def create_cap_theorem_diagram():
    """Gambar 2.1 - Visualisasi Teorema CAP"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 9))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Triangle vertices
    top = (5, 8.5)
    left = (1.5, 2)
    right = (8.5, 2)
    
    # Draw triangle
    triangle = plt.Polygon([top, left, right], fill=False, edgecolor='#333', linewidth=3)
    ax.add_patch(triangle)
    
    # Labels at vertices
    ax.text(top[0], top[1] + 0.5, 'Consistency (C)', ha='center', va='bottom', 
            fontsize=14, fontweight='bold', color='#1976D2')
    ax.text(top[0], top[1] + 0.1, 'Semua node melihat\ndata yang sama', 
            ha='center', va='bottom', fontsize=9, color='#666')
    
    ax.text(left[0] - 0.3, left[1], 'Availability (A)', ha='right', va='center', 
            fontsize=14, fontweight='bold', color='#388E3C')
    ax.text(left[0] - 0.3, left[1] - 0.6, 'Setiap request\nmendapat response', 
            ha='right', va='top', fontsize=9, color='#666')
    
    ax.text(right[0] + 0.3, right[1], 'Partition\nTolerance (P)', ha='left', va='center', 
            fontsize=14, fontweight='bold', color='#F57C00')
    ax.text(right[0] + 0.3, right[1] - 0.6, 'Sistem tetap jalan\nsaat network partition', 
            ha='left', va='top', fontsize=9, color='#666')
    
    # CP, AP, CA regions
    # CP (top-right edge)
    cp_x, cp_y = (top[0] + right[0])/2 + 0.3, (top[1] + right[1])/2
    ax.add_patch(FancyBboxPatch((cp_x - 0.8, cp_y - 0.4), 1.6, 0.8,
                                 boxstyle="round,pad=0.02",
                                 facecolor='#E3F2FD', edgecolor='#1976D2', linewidth=2))
    ax.text(cp_x, cp_y, 'CP', ha='center', va='center', fontsize=12, fontweight='bold', color='#1976D2')
    
    # AP (bottom edge)
    ap_x, ap_y = (left[0] + right[0])/2, left[1] - 0.6
    ax.add_patch(FancyBboxPatch((ap_x - 0.8, ap_y - 0.4), 1.6, 0.8,
                                 boxstyle="round,pad=0.02",
                                 facecolor='#E8F5E9', edgecolor='#388E3C', linewidth=2))
    ax.text(ap_x, ap_y, 'AP', ha='center', va='center', fontsize=12, fontweight='bold', color='#388E3C')
    
    # CA (top-left edge)
    ca_x, ca_y = (top[0] + left[0])/2 - 0.3, (top[1] + left[1])/2
    ax.add_patch(FancyBboxPatch((ca_x - 0.8, ca_y - 0.4), 1.6, 0.8,
                                 boxstyle="round,pad=0.02",
                                 facecolor='#FFF3E0', edgecolor='#F57C00', linewidth=2))
    ax.text(ca_x, ca_y, 'CA', ha='center', va='center', fontsize=12, fontweight='bold', color='#F57C00')
    
    # Center text
    center_x, center_y = 5, 4.5
    ax.text(center_x, center_y, 'Pilih 2 dari 3', ha='center', va='center', 
            fontsize=16, fontweight='bold', color='#D32F2F')
    
    # Project note
    ax.add_patch(FancyBboxPatch((2.5, 0.3), 5, 1.2,
                                 boxstyle="round,pad=0.02",
                                 facecolor='#FFEBEE', edgecolor='#D32F2F', linewidth=2))
    ax.text(5, 1.1, '⚡ Proyek ini: CP (Consistency + Partition Tolerance)', 
            ha='center', va='center', fontsize=11, fontweight='bold', color='#D32F2F')
    ax.text(5, 0.6, 'ShardingSphere menjaga konsistensi routing', 
            ha='center', va='center', fontsize=9, color='#666')
    
    # Title
    ax.text(5, 9.7, 'Gambar 2.1 Visualisasi Teorema CAP', ha='center', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('diagrams/gambar_2_1_cap_theorem.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Gambar 2.1 CAP Theorem berhasil dibuat")


def create_duration_comparison():
    """Gambar 4.3 - Perbandingan Durasi Total Pengujian"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    categories = ['Single Database', 'Sharded Database']
    durations = [256, 129]
    colors = ['#EF5350', '#66BB6A']
    
    bars = ax.bar(categories, durations, color=colors, edgecolor='#333', width=0.5)
    
    ax.set_ylabel('Durasi (detik)', fontsize=12)
    ax.set_title('Gambar 4.3 Perbandingan Total Durasi Pengujian\n(6.000 operasi, 50 concurrent workers)', 
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 300)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars, durations):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{val} detik', ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # Add improvement arrow
    ax.annotate('', xy=(1, 150), xytext=(0, 220),
                arrowprops=dict(arrowstyle='->', color='#4CAF50', lw=3))
    ax.text(0.5, 200, '-49.6%\nlebih cepat', ha='center', fontsize=12, 
            fontweight='bold', color='#4CAF50')
    
    plt.tight_layout()
    plt.savefig('diagrams/gambar_4_3_duration.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✓ Gambar 4.3 Duration Comparison berhasil dibuat")


if __name__ == '__main__':
    print("\n" + "="*50)
    print("Generating Diagrams for Laporan BDT")
    print("="*50 + "\n")
    
    create_cap_theorem_diagram()      # Gambar 2.1
    create_erd_diagram()              # Gambar 3.1
    create_architecture_diagram()     # Gambar 3.2
    create_query_routing_diagram()    # Gambar 3.3
    create_performance_comparison()   # Gambar 4.1
    create_shard_distribution()       # Gambar 4.2
    create_duration_comparison()      # Gambar 4.3
    
    print("\n" + "="*50)
    print("✅ Semua diagram berhasil dibuat!")
    print("📁 Lokasi: ./diagrams/")
    print("="*50 + "\n")
    
    # List created files
    print("Daftar file yang dibuat:")
    for f in sorted(os.listdir('diagrams')):
        print(f"  - diagrams/{f}")
