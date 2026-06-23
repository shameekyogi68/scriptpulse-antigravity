# MODULE: charts.py
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.components.theme import Theme

def hex_to_rgba(hex_str: str, alpha: float) -> str:
    h = hex_str.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"

@st.cache_resource
def get_engagement_chart(df_trace, act_structure=None):
    """Generates the engagement journey chart with clean spline design matching the mockup."""
    fig = go.Figure()
    
    # 1. Background shading for Acts
    shapes = []
    if act_structure and isinstance(act_structure, dict):
        act1 = act_structure.get('act1', 0)
        act2 = act_structure.get('act2', 0)
        act3 = act_structure.get('act3', 0)
        total = len(df_trace)
        
        # Check that we have valid numbers
        if isinstance(act1, int) and isinstance(act2, int) and isinstance(act3, int):
            if act1 > 0:
                shapes.append(dict(
                    type="rect",
                    xref="x", yref="paper",
                    x0=-0.5, x1=act1 - 0.5,
                    y0=0, y1=1,
                    fillcolor="rgba(245, 121, 70, 0.015)",
                    layer="below",
                    line_width=0,
                ))
            if act2 > 0:
                shapes.append(dict(
                    type="rect",
                    xref="x", yref="paper",
                    x0=act1 - 0.5, x1=act1 + act2 - 0.5,
                    y0=0, y1=1,
                    fillcolor="rgba(155, 81, 224, 0.015)",
                    layer="below",
                    line_width=0,
                ))
            if act3 > 0:
                shapes.append(dict(
                    type="rect",
                    xref="x", yref="paper",
                    x0=act1 + act2 - 0.5, x1=total - 0.5,
                    y0=0, y1=1,
                    fillcolor="rgba(0, 210, 160, 0.015)",
                    layer="below",
                    line_width=0,
                ))

    # Dynamic Hover text if available
    hover_template = '<b>Scene %{x}</b><br>Tension Level: %{y:.0%}<br>%{customdata[0]}<extra></extra>' if 'Hover_Text' in df_trace.columns else '<b>Scene %{x}</b><br>Tension Level: %{y:.0%}<extra></extra>'
    custom_data = [df_trace['Hover_Text']] if 'Hover_Text' in df_trace.columns else None
    
    # 2. Glowing Shadow Line Trace (Thick and blurry underneath)
    fig.add_trace(go.Scatter(
        x=df_trace.index,
        y=df_trace['attentional_signal'],
        mode='lines',
        line=dict(color='#A56DFF', width=8, shape='spline'),
        opacity=0.15,
        showlegend=False,
        hoverinfo='skip'
    ))

    # 3. Main engagement line with area fill
    fig.add_trace(go.Scatter(
        x=df_trace.index,
        y=df_trace['attentional_signal'],
        fill='tozeroy',
        mode='lines',
        name='Tension Level',
        line=dict(color='#A56DFF', width=3, shape='spline'),
        fillcolor='rgba(165, 109, 255, 0.06)',
        customdata=custom_data[0] if custom_data else None,
        hovertemplate=hover_template
    ))
    
    # 4. Colored Category Markers at each data point removed to clean up visual clutter
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        xaxis=dict(
            title="Scene Number →", 
            range=[0, len(df_trace)-1],
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.02)',
            zeroline=False,
            showspikes=True,
            spikethickness=1,
            spikedash="solid",
            spikecolor="rgba(165, 109, 255, 0.4)",
            spikemode="across"
        ),
        yaxis=dict(
            title="Tension & Conflict →", 
            range=[0, 1], 
            tickformat='.0%',
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.02)',
            zeroline=False
        ),
        height=380,
        margin=dict(l=40, r=20, t=30, b=40),
        showlegend=False,
        hovermode='x unified',
        shapes=shapes
    )
    return fig

@st.cache_resource
def get_stakes_chart(stake_labels, stake_values, stake_colors_map):
    """Generates the stakes horizontal bar chart matching the premium theme."""
    colors = [stake_colors_map.get(s, Theme.SEMANTIC_INFO) for s in stake_labels]
    
    # Pair up and sort descending by value so the highest stake is at the top
    paired = sorted(zip(stake_values, stake_labels, colors), key=lambda x: x[0], reverse=True)
    sorted_values, sorted_labels, sorted_colors = zip(*paired)
    
    total = sum(sorted_values)
    percentages = [v / total if total > 0 else 0 for v in sorted_values]
    text_labels = [f" <b>{v}</b> scenes ({p:.0%})" for v, p in zip(sorted_values, percentages)]
    
    fig = go.Figure(data=[go.Bar(
        y=sorted_labels,
        x=sorted_values,
        orientation='h',
        marker=dict(
            color=sorted_colors,
            line=dict(color='rgba(0,0,0,0)', width=0)
        ),
        text=text_labels,
        textposition='outside',
        textfont=dict(size=11, color=Theme.TEXT_PRIMARY, family="'Outfit', sans-serif"),
        hovertemplate='<b>%{y} Stakes</b><br>%{x} scenes<extra></extra>',
        width=0.45
    )])
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        height=240,
        margin=dict(l=100, r=100, t=10, b=10),
        xaxis=dict(
            showgrid=False,
            visible=False,
            range=[0, max(sorted_values) * 1.35] if sorted_values else [0, 1]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=12, color=Theme.TEXT_SECONDARY, family="'Outfit', sans-serif"),
            autorange="reversed"
        ),
        showlegend=False
    )
    return fig

@st.cache_resource
def get_lab_trace_chart(df):
    """Generates the advanced lab trace array — writer friendly."""
    fig = go.Figure()
    
    # Area for composite
    fig.add_trace(go.Scatter(
        x=df['T_Index'], y=df['Composite_Attention'], name='Overall Intensity', 
        line=dict(color=Theme.ACCENT_PRIMARY, width=1), fill='tozeroy',
        fillcolor=hex_to_rgba(Theme.ACCENT_PRIMARY, 0.15), mode='lines',
        hovertemplate='<b>Scene %{x}</b><br>Overall: %{y:.0%}<extra></extra>'
    ))
    
    # Lines for raw vectors
    signals = [
        ('Strain_Tension', Theme.SEMANTIC_CRITICAL, 'solid', 'Tension / Conflict'),
        ('Load_Effort', Theme.SEMANTIC_WARNING, 'solid', 'Mental Effort'),
        ('Recovery_Valence', Theme.SEMANTIC_GOOD, 'dash', 'Recovery / Calm')
    ]
    
    for col, color, dash, label in signals:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['T_Index'], y=df[col], name=label, 
                line=dict(color=color, width=1.5, dash=dash),
                mode='lines+markers', marker=dict(size=4),
                hovertemplate=f'{label}: %{{y:.0%}}<extra></extra>'
            ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        hovermode='x unified', height=350,
        margin=dict(l=40, r=20, t=10, b=40),
        xaxis=dict(
            title='Scene Number →', 
            tickfont=dict(family="'Inter', sans-serif", size=10),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.04)',
            zeroline=False
        ),
        yaxis=dict(
            title='How Strong Is Each Signal? →', 
            range=[0, 1], 
            tickformat='.0%', 
            tickfont=dict(family="'Inter', sans-serif", size=10),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.04)',
            zeroline=False
        ),
        legend=dict(
            font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY, size=11), 
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1
        )
    )
    return fig

@st.cache_resource
def get_phase_space_chart(df_q):
    """Generates the energy/entropy scatter plot — writer friendly."""
    fig = px.scatter(
        df_q, x='Story_Detail', y='Pacing_Speed', 
        hover_data=['T_Index'], color='Quadrant',
        color_discrete_map={
            '🔥 Climax / Major Setpiece': Theme.SEMANTIC_CRITICAL, 
            '🏃 Fast-Paced Action': Theme.SEMANTIC_WARNING, 
            '😌 Breather / Quiet Moment': Theme.SEMANTIC_GOOD, 
            '🕵️ World-Building / Detail': Theme.ACCENT_PRIMARY
        },
        labels={'T_Index': 'Scene', 'Pacing_Speed': 'Action / Speed', 'Story_Detail': 'Information / Detail'}
    )
    
    fig.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    fig.add_vline(x=0.5, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color='rgba(255,255,255,0.8)')))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        height=350, 
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(
            tickfont=dict(family="'Inter', sans-serif", size=10), 
            title="Story Detail (Dialogue, Clues, World-Building) →",
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.04)',
            zeroline=False
        ),
        yaxis=dict(
            tickfont=dict(family="'Inter', sans-serif", size=10), 
            title="Pacing Speed (Action, Conflict) →",
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.04)',
            zeroline=False
        ),
        showlegend=False
    )
    return fig

@st.cache_resource
def get_arc_chart(s_delta, a_delta):
    """Generates the character arc bar chart — writer friendly."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Mood Shift', 'Power Shift'], y=[s_delta, a_delta],
        marker_color=[Theme.SEMANTIC_GOOD if s_delta >= 0 else Theme.SEMANTIC_CRITICAL, 
                        Theme.SEMANTIC_GOOD if a_delta >= 0 else Theme.SEMANTIC_WARNING],
        text=[f"{'+'if s_delta >= 0 else ''}{s_delta:.2f}", f"{'+'if a_delta >= 0 else ''}{a_delta:.2f}"],
        textposition='outside', 
        textfont=dict(family="'Outfit', sans-serif", color=Theme.TEXT_SECONDARY, size=11),
        hovertemplate='%{x}: %{y:.2f}<extra></extra>'
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        height=120, 
        margin=dict(l=0, r=0, t=5, b=5), 
        showlegend=False, 
        bargap=0.5,
        yaxis=dict(range=[-1, 1], showticklabels=False, showgrid=False, zeroline=False)
    )
    return fig

@st.cache_resource
def get_purpose_chart(purpose_list):
    """Generates the scene purpose distribution bar chart — writer friendly."""
    purpose_colors = {
        'Conflict': Theme.SEMANTIC_CRITICAL, 
        'Exposition': Theme.ACCENT_PURPLE, 
        'Transition': Theme.SEMANTIC_INFO,
        'Climax': Theme.SEMANTIC_WARNING, 
        'Resolution': Theme.SEMANTIC_INFO, 
        'Setup': Theme.ACCENT_PRIMARY
    }
    fig = go.Figure(data=[go.Bar(
        x=[p['scene'] for p in purpose_list], y=[1]*len(purpose_list),
        marker_color=[purpose_colors.get(p['purpose'], 'rgba(255,255,255,0.1)') for p in purpose_list],
        text=[p['purpose'] for p in purpose_list], 
        textposition='inside', 
        textfont=dict(family="'Outfit', sans-serif", size=8, color='white'),
        hovertemplate='<b>Scene %{x}</b><br>Purpose: %{text}<extra></extra>'
    )])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        height=120, 
        margin=dict(l=10, r=10, t=5, b=30), 
        showlegend=False, 
        xaxis=dict(
            title="Scene Number →", 
            tickfont=dict(family="'Inter', sans-serif", size=10),
            showgrid=False
        ), 
        yaxis=dict(showticklabels=False, showgrid=False)
    )
    return fig

@st.cache_resource
def get_voice_radar(top_chars):
    """Generates the vocal fingerprint radar chart — writer friendly."""
    fig = go.Figure()
    colors = [Theme.SEMANTIC_CRITICAL, Theme.SEMANTIC_GOOD, Theme.ACCENT_PURPLE]
    for i, (char, data) in enumerate(top_chars):
        fig.add_trace(go.Scatterpolar(
            r=[data.get('complexity', 0), data.get('positivity', 0), data.get('line_count', 0)/top_chars[0][1].get('line_count', 1)],
            theta=['Vocabulary Level', 'Positivity / Mood', 'Amount of Dialogue'], 
            fill='toself', name=char, line_color=colors[i % len(colors)]
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        height=350, margin=dict(l=40, r=40, t=20, b=20), 
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 1], 
                gridcolor='rgba(255,255,255,0.06)',
                tickfont=dict(family="'Inter', sans-serif", size=9, color=Theme.TEXT_MUTED)
            ),
            angularaxis=dict(
                tickfont=dict(family="'Outfit', sans-serif", size=10, color=Theme.TEXT_SECONDARY)
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        legend=dict(font=dict(family="'Inter', sans-serif", size=11, color=Theme.TEXT_SECONDARY))
    )
    return fig

@st.cache_resource
def get_efficiency_frontier(df):
    """Generates the Narrative Conflict vs Cognitive Effort scatter plot."""
    # Ensure columns exist
    y_col = 'attentional_signal' if 'attentional_signal' in df.columns else 'Composite_Attention'
    x_col = 'referential_load' if 'referential_load' in df.columns else 'Load_Effort'
    
    if x_col not in df.columns or y_col not in df.columns:
        # Fallback if names differ
        x_col = df.columns[0]
        y_col = df.columns[1]

    fig = px.scatter(
        df, x=x_col, y=y_col, 
        hover_data=[df.index], 
        labels={x_col: 'Cognitive Effort (Complexity)', y_col: 'Narrative Conflict (Tension)'},
        title="Scene Efficiency Frontier"
    )
    
    # Add quadrants
    fig.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    fig.add_vline(x=0.5, line_dash="dash", line_color="rgba(255,255,255,0.15)")
    
    fig.update_traces(marker=dict(size=10, color=Theme.ACCENT_PRIMARY, opacity=0.7, line=dict(width=1, color='white')))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        height=400, margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(
            title="Cognitive Effort →", 
            range=[0, 1], 
            tickformat='.0%',
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.04)',
            zeroline=False
        ),
        yaxis=dict(
            title="Narrative Conflict →", 
            range=[0, 1], 
            tickformat='.0%',
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.04)',
            zeroline=False
        ),
    )
    
    # Annotate quadrants
    fig.add_annotation(x=0.85, y=0.85, text="🔥 High Payoff", showarrow=False, font=dict(family="'Outfit', sans-serif", color=Theme.SEMANTIC_GOOD, size=10))
    fig.add_annotation(x=0.15, y=0.15, text="💤 Filler", showarrow=False, font=dict(family="'Outfit', sans-serif", color=Theme.TEXT_MUTED, size=10))
    fig.add_annotation(x=0.85, y=0.15, text="🧠 Dense / Heavy", showarrow=False, font=dict(family="'Outfit', sans-serif", color=Theme.SEMANTIC_WARNING, size=10))
    fig.add_annotation(x=0.15, y=0.85, text="⚡ Efficient Action", showarrow=False, font=dict(family="'Outfit', sans-serif", color=Theme.ACCENT_TEAL, size=10))

    return fig

@st.cache_resource
def get_stakes_donut_chart(stake_labels, stake_values, stake_colors_map):
    """Generates the stakes donut chart (rounded pie chart) matching the premium theme."""
    colors = [stake_colors_map.get(s, Theme.SEMANTIC_INFO) for s in stake_labels]
    
    # Pair up and sort descending by value so the highest stake is first
    paired = sorted(zip(stake_values, stake_labels, colors), key=lambda x: x[0], reverse=True)
    sorted_values, sorted_labels, sorted_colors = zip(*paired)
    
    fig = go.Figure(data=[go.Pie(
        labels=sorted_labels,
        values=sorted_values,
        hole=0.6,
        marker=dict(
            colors=sorted_colors,
            line=dict(color='#1A1729', width=2)
        ),
        textinfo='percent',
        textposition='inside',
        insidetextorientation='horizontal',
        textfont=dict(size=11, color='white', family="'Outfit', sans-serif"),
        hovertemplate='<b>%{label} Stakes</b><br>%{value} scenes (%{percent})<extra></extra>'
    )])
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        height=260,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY, size=11),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        showlegend=True
    )
    return fig

@st.cache_resource
def get_engagement_bar_chart(df_trace):
    """Generates the engagement journey as a vertical bar chart with category-based colors."""
    fig = go.Figure()
    
    # Determine bar colors dynamically based on tension level
    colors = []
    for val in df_trace['attentional_signal']:
        if val < 0.25:
            colors.append("#2F48B9") # Breather (Cool Blue)
        elif val < 0.50:
            colors.append("#00D2A0") # Moderate (Mint Green)
        elif val < 0.75:
            colors.append("#F57946") # High (Amber Orange)
        else:
            colors.append("#D92987") # Climax (Rose-Crimson)
            
    # Dynamic Hover text if available
    hover_template = '<b>Scene %{x}</b><br>Tension Level: %{y:.0%}<br>%{customdata[0]}<extra></extra>' if 'Hover_Text' in df_trace.columns else '<b>Scene %{x}</b><br>Tension Level: %{y:.0%}<extra></extra>'
    custom_data = [df_trace['Hover_Text']] if 'Hover_Text' in df_trace.columns else None
    
    fig.add_trace(go.Bar(
        x=df_trace.index,
        y=df_trace['attentional_signal'],
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0)', width=0)
        ),
        name='Tension Level',
        customdata=custom_data[0] if custom_data else None,
        hovertemplate=hover_template
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="'Inter', sans-serif", color=Theme.TEXT_SECONDARY),
        xaxis=dict(
            title="Scene Number →", 
            range=[-0.5, len(df_trace)-0.5],
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.04)',
            zeroline=False
        ),
        yaxis=dict(
            title="Tension & Conflict →", 
            range=[0, 1], 
            tickformat='.0%',
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.04)',
            zeroline=False
        ),
        height=380,
        margin=dict(l=40, r=20, t=30, b=40),
        showlegend=False,
        hovermode='x unified'
    )
    return fig
