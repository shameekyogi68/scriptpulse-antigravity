import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.components.theme import Theme

@st.cache_resource
def get_engagement_chart(df_trace):
    """Generates the engagement journey chart with color-coded zones."""
    fig = go.Figure()
    
    # Color-coded background zones so the writer instantly knows what the graph means
    # Green zone: Calm / Recovery (0% - 35%)
    fig.add_hrect(y0=0, y1=0.35, fillcolor="rgba(0, 210, 160, 0.06)", line_width=0,
                  annotation_text="😌 Calm / Recovery", annotation_position="top left",
                  annotation_font=dict(size=10, color="rgba(0, 210, 160, 0.5)"))
    # Yellow zone: Engaging / Balanced (35% - 65%)
    fig.add_hrect(y0=0.35, y1=0.65, fillcolor="rgba(245, 121, 70, 0.06)", line_width=0,
                  annotation_text="⚡ Engaging", annotation_position="top left",
                  annotation_font=dict(size=10, color="rgba(245, 121, 70, 0.5)"))
    # Red zone: High Intensity / Risk of Fatigue (65% - 100%)
    fig.add_hrect(y0=0.65, y1=1.0, fillcolor="rgba(217, 41, 135, 0.06)", line_width=0,
                  annotation_text="🔥 Intense (Risk of Fatigue)", annotation_position="top left",
                  annotation_font=dict(size=10, color="rgba(217, 41, 135, 0.5)"))
    
    # Main engagement line
    fig.add_trace(go.Scatter(
        x=df_trace.index,
        y=df_trace['attentional_signal'],
        fill='tozeroy',
        mode='lines',
        name='Reader Engagement',
        line=dict(color='rgba(106, 72, 187, 0.9)', width=2.5, shape='spline'),
        fillcolor='rgba(106, 72, 187, 0.12)',
        hovertemplate='<b>Scene %{x}</b><br>How intense: %{y:.0%}<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis=dict(title="Scene Number →", range=[0, len(df_trace)-1]),
        yaxis=dict(title="How Intense Does It Feel? →", range=[0, 1], tickformat='.0%'),
        height=380,
        showlegend=False,
        hovermode='x unified'
    )
    return fig

@st.cache_resource
def get_stakes_chart(stake_labels, stake_values, stake_colors_map):
    """Generates the stakes donut chart."""
    colors = [stake_colors_map.get(s, Theme.SEMANTIC_INFO) for s in stake_labels]
    
    fig = go.Figure(data=[go.Pie(
        labels=stake_labels,
        values=stake_values,
        hole=0.55,
        marker_colors=colors,
        textinfo='label+percent',
        textfont=dict(size=12, color=Theme.TEXT_PRIMARY),
        hovertemplate='%{label}: %{value} scenes (%{percent})<extra></extra>'
    )])
    
    fig.update_layout(
        height=300, 
        margin=dict(l=20, r=20, t=10, b=10),
        legend=dict(font=dict(color=Theme.TEXT_SECONDARY, size=11)),
        showlegend=True
    )
    
    fig.add_annotation(
        text=f"<b>{sum(stake_values)}</b><br>scenes",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color=Theme.TEXT_PRIMARY)
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
        fillcolor='rgba(106, 72, 187, 0.15)', mode='lines',
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
        hovermode='x unified', height=350,
        margin=dict(l=40, r=20, t=10, b=40),
        xaxis=dict(title='Scene Number →', tickfont=dict(size=10)),
        yaxis=dict(title='How Strong Is Each Signal? →', range=[0, 1], tickformat='.0%', tickfont=dict(size=10)),
        legend=dict(font=dict(color=Theme.TEXT_SECONDARY, size=11), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

@st.cache_resource
def get_phase_space_chart(df_q):
    """Generates the energy/entropy scatter plot — writer friendly."""
    fig = px.scatter(
        df_q, x='Entropy_Complexity', y='Energy_Signal', 
        hover_data=['T_Index'], color='Quadrant',
        color_discrete_map={
            '🔥 Climax': Theme.SEMANTIC_CRITICAL, 
            '⚡ Action': Theme.SEMANTIC_WARNING, 
            '😌 Breather': Theme.SEMANTIC_GOOD, 
            '🔮 Mystery': Theme.ACCENT_PRIMARY
        },
        labels={'T_Index': 'Scene', 'Energy_Signal': 'How Intense?', 'Entropy_Complexity': 'How Complex?'}
    )
    
    fig.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.add_vline(x=0.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color='rgba(255,255,255,0.8)')))
    
    fig.update_layout(
        height=350, margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(tickfont=dict(size=10), title="How Complex / Dense Is the Language? →"),
        yaxis=dict(tickfont=dict(size=10), title="How Intense / Fast Is the Scene? →"),
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
        textposition='outside', textfont=dict(color=Theme.TEXT_SECONDARY, size=11),
        hovertemplate='%{x}: %{y:.2f}<extra></extra>'
    ))
    fig.update_layout(height=120, margin=dict(l=0, r=0, t=5, b=5), showlegend=False, bargap=0.5,
                        yaxis=dict(range=[-1, 1], showticklabels=False, showgrid=False))
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
        text=[p['purpose'] for p in purpose_list], textposition='inside', textfont=dict(size=8, color='white'),
        hovertemplate='<b>Scene %{x}</b><br>Purpose: %{text}<extra></extra>'
    )])
    fig.update_layout(height=120, margin=dict(l=10, r=10, t=5, b=30), showlegend=False, 
                        xaxis=dict(title="Scene Number →"), yaxis=dict(showticklabels=False))
    return fig

@st.cache_resource
def get_voice_radar(top_chars):
    """Generates the vocal fingerprint radar chart — writer friendly."""
    fig = go.Figure()
    colors = [Theme.SEMANTIC_CRITICAL, Theme.SEMANTIC_GOOD, Theme.ACCENT_PURPLE]
    for i, (char, data) in enumerate(top_chars):
        fig.add_trace(go.Scatterpolar(
            r=[data.get('complexity', 0), data.get('positivity', 0), data.get('line_count', 0)/top_chars[0][1].get('line_count', 1)],
            theta=['How Complex They Speak', 'How Positive They Sound', 'How Much They Talk'], 
            fill='toself', name=char, line_color=colors[i % len(colors)]
        ))
    fig.update_layout(
        height=350, margin=dict(l=40, r=40, t=20, b=20), 
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor='rgba(255,255,255,0.1)'),
            bgcolor='rgba(0,0,0,0)'
        ),
        legend=dict(font=dict(size=11, color=Theme.TEXT_SECONDARY))
    )
    return fig
