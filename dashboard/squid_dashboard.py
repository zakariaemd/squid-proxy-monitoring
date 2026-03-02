# ============================================
# SQUID PROXY MONITORING DASHBOARD
# Author: [Ton Prénom]
# Stack: Python, Pandas, Plotly
# ============================================

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from parse_logs import generate_synthetic_logs, compute_kpis

# ============================================
# LOAD DATA
# ============================================
print("🔄 Chargement des données...")
df   = generate_synthetic_logs(5000)
kpis = compute_kpis(df)

# Agrégations
df_monthly   = df.groupby('month').agg(
    requetes=('timestamp','count'),
    bloquees=('is_blocked','sum'),
    volume_mb=('bytes', lambda x: round(x.sum()/1e6, 2)),
    hit_rate=('is_hit', lambda x: round(x.mean()*100, 2))
).reset_index()

df_category  = df.groupby('category').agg(
    requetes=('timestamp','count'),
    volume_mb=('bytes', lambda x: round(x.sum()/1e6, 2))
).reset_index().sort_values('requetes', ascending=False)

df_hourly    = df.groupby('hour').agg(
    requetes=('timestamp','count')
).reset_index()

df_top_users = df.groupby('user').agg(
    requetes=('timestamp','count'),
    volume_mb=('bytes', lambda x: round(x.sum()/1e6, 2)),
    bloquees=('is_blocked','sum')
).reset_index().sort_values('requetes', ascending=False).head(10)

df_top_domains = df.groupby('domain').agg(
    requetes=('timestamp','count')
).reset_index().sort_values('requetes', ascending=False).head(10)

df_status    = df['squid_status'].value_counts().reset_index()
df_status.columns = ['status','count']

# ============================================
# COLORS
# ============================================
C = {
    'bg':      '#0a0e1a',
    'card':    '#141828',
    'c1':      '#00d4ff',
    'c2':      '#7c3aed',
    'c3':      '#10b981',
    'c4':      '#f59e0b',
    'danger':  '#ef4444',
    'text':    '#e2e8f0',
    'sub':     '#94a3b8'
}

# ============================================
# SUBPLOTS
# ============================================
fig = make_subplots(
    rows=3, cols=3,
    subplot_titles=(
        '📈 Requêtes & Blocages Mensuels',
        '🌐 Requêtes par Catégorie',
        '⏰ Activité par Heure',
        '💾 Volume Trafic Mensuel (MB)',
        '🔄 Statuts Squid',
        '🏆 Top 10 Utilisateurs',
        '🌍 Top 10 Domaines', '', ''
    ),
    specs=[
        [{"type": "xy"},     {"type": "xy"},     {"type": "xy"}],
        [{"type": "xy"},     {"type": "domain"},  {"type": "xy"}],
        [{"type": "xy", "colspan": 2}, None, {"type": "xy"}]
    ],
    vertical_spacing=0.13,
    horizontal_spacing=0.08
)

# --- R1C1 : Requêtes & Blocages mensuels
fig.add_trace(go.Bar(
    x=df_monthly['month'], y=df_monthly['requetes'],
    name='Requêtes totales',
    marker_color=C['c1'], opacity=0.85,
    hovertemplate='%{x}<br>Requêtes: %{y:,}<extra></extra>'
), row=1, col=1)
fig.add_trace(go.Bar(
    x=df_monthly['month'], y=df_monthly['bloquees'],
    name='Bloquées',
    marker_color=C['danger'], opacity=0.85,
    hovertemplate='%{x}<br>Bloquées: %{y:,}<extra></extra>'
), row=1, col=1)

# --- R1C2 : Catégories (horizontal bar)
fig.add_trace(go.Bar(
    y=df_category['category'], x=df_category['requetes'],
    orientation='h',
    marker_color=[C['c3'],C['c1'],C['c4'],C['c2'],C['danger'],C['sub'],C['c3']],
    hovertemplate='%{y}<br>Requêtes: %{x:,}<extra></extra>',
    showlegend=False
), row=1, col=2)

# --- R1C3 : Activité par heure
fig.add_trace(go.Scatter(
    x=df_hourly['hour'], y=df_hourly['requetes'],
    mode='lines+markers',
    line=dict(color=C['c4'], width=3),
    marker=dict(size=6),
    fill='tozeroy', fillcolor='rgba(245,158,11,0.15)',
    hovertemplate='%{x}h00<br>Requêtes: %{y:,}<extra></extra>',
    showlegend=False
), row=1, col=3)

# --- R2C1 : Volume mensuel
fig.add_trace(go.Scatter(
    x=df_monthly['month'], y=df_monthly['volume_mb'],
    mode='lines+markers',
    line=dict(color=C['c2'], width=3),
    marker=dict(size=8),
    fill='tozeroy', fillcolor='rgba(124,58,237,0.15)',
    hovertemplate='%{x}<br>Volume: %{y:,.0f} MB<extra></extra>',
    showlegend=False
), row=2, col=1)

# --- R2C2 : Statuts Squid (Donut)
status_colors = {
    'TCP_MISS':    C['c1'],
    'TCP_HIT':     C['c3'],
    'TCP_DENIED':  C['danger'],
    'TCP_EXPIRED': C['c4'],
    'TCP_ERROR':   C['c2']
}
fig.add_trace(go.Pie(
    labels=df_status['status'],
    values=df_status['count'],
    hole=0.55,
    marker_colors=[status_colors.get(s, C['sub']) for s in df_status['status']],
    hovertemplate='%{label}<br>%{value:,} requêtes (%{percent})<extra></extra>',
    showlegend=True
), row=2, col=2)

# --- R2C3 : Top utilisateurs
fig.add_trace(go.Bar(
    y=df_top_users['user'], x=df_top_users['requetes'],
    orientation='h',
    marker_color=C['c3'],
    hovertemplate='%{y}<br>Requêtes: %{x:,}<extra></extra>',
    showlegend=False
), row=2, col=3)

# --- R3C1-2 : Top domaines
fig.add_trace(go.Bar(
    x=df_top_domains['domain'], y=df_top_domains['requetes'],
    marker_color=C['c1'],
    hovertemplate='%{x}<br>Requêtes: %{y:,}<extra></extra>',
    showlegend=False
), row=3, col=1)

# --- R3C3 : Cache hit rate mensuel
fig.add_trace(go.Scatter(
    x=df_monthly['month'], y=df_monthly['hit_rate'],
    mode='lines+markers',
    line=dict(color=C['c3'], width=3),
    marker=dict(size=8),
    fill='tozeroy', fillcolor='rgba(16,185,129,0.15)',
    hovertemplate='%{x}<br>Hit Rate: %{y:.1f}%<extra></extra>',
    showlegend=False,
    name='Cache Hit Rate'
), row=3, col=3)

# ============================================
# KPI CARDS
# ============================================
kpi_cards = [
    ('🔢 Requêtes Totales',   f"{kpis['total_requetes']:,}"),
    ('🚫 Taux Blocage',        f"{kpis['taux_blocage_pct']}%"),
    ('⚡ Cache Hit Rate',      f"{kpis['cache_hit_rate_pct']}%"),
    ('💾 Volume Total',        f"{kpis['volume_total_gb']} GB"),
    ('👥 Utilisateurs',        str(kpis['utilisateurs_uniques'])),
    ('⏱️ Latence Moy.',        f"{kpis['latence_moy_ms']} ms"),
]
card_x = [0.08, 0.25, 0.42, 0.59, 0.76, 0.93]
for idx, (label, value) in enumerate(kpi_cards):
    fig.add_annotation(
        x=card_x[idx], y=1.07,
        xref='paper', yref='paper',
        text=f"<b>{value}</b><br><span style='font-size:9px'>{label}</span>",
        showarrow=False,
        font=dict(size=14, color=C['c3']),
        align='center',
        bgcolor=C['card'],
        bordercolor=C['c1'],
        borderwidth=1,
        borderpad=8,
        opacity=0.95
    )

# ============================================
# LAYOUT
# ============================================
fig.update_layout(
    title=dict(
        text='🌐 Squid Proxy Monitoring Dashboard 2024',
        font=dict(size=26, color=C['text'], family='Inter'),
        x=0.5, xanchor='center', y=0.98
    ),
    paper_bgcolor=C['bg'],
    plot_bgcolor=C['card'],
    font=dict(color=C['text'], family='Inter'),
    height=1300,
    barmode='overlay',
    showlegend=True,
    legend=dict(bgcolor=C['card'], bordercolor=C['c1'], borderwidth=1),
    margin=dict(t=150, b=40, l=40, r=40)
)

for ann in fig['layout']['annotations']:
    if ann.get('text','').startswith('📈') or \
       ann.get('text','').startswith('🌐') or \
       ann.get('text','').startswith('⏰') or \
       ann.get('text','').startswith('💾') or \
       ann.get('text','').startswith('🔄') or \
       ann.get('text','').startswith('🏆') or \
       ann.get('text','').startswith('🌍'):
        ann['font'] = dict(size=12, color=C['c1'])

fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)',
                 linecolor='rgba(255,255,255,0.1)',
                 tickfont=dict(size=9))
fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)',
                 linecolor='rgba(255,255,255,0.1)',
                 tickfont=dict(size=9))

fig.write_html("dashboard/squid_dashboard.html")
fig.write_image("dashboard/squid_dashboard.png", width=1400, height=1300, scale=2)
print("✅ Squid Dashboard exporté : squid_dashboard.html & squid_dashboard.png")
