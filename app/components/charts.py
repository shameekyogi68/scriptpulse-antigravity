import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.components.theme import Theme

@st.cache_resource
def get_engagement_chart(df_trace):
    """Generates the engagement journey chart with caching."""
    fig = go.Figure()
    
    # Gradient fill area for attention
    fig.add_trace(go.Scatter(
        x=df_trace.index,
        y=df_trace['attentional_signal'],
        fill='tozeroy',
        mode='lines',
        name='Reader Engagement',
        line=dict(color='rgba(106, 72, 187, 0.9)', width=2.5, shape='spline'),
        fillcolor='rgba(106, 72, 187, 0.12)',
        hovertemplate='Scene %{x}<br>Engagement: %{y:.0%}<extra></extra>'
    ))
    
    # Base layout is already set by pio.templates.default, but we can override specifics
    fig.update_layout(
        xaxis=dict(title="Scene Number →", range=[0, len(df_trace)-1]),
        yaxis=dict(title="Reader Engagement →", range=[0, 1], tickformat='.0%'),
        height=350,
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
    """Generates the advanced lab trace array."""
    fig = go.Figure()
    
    # Area for composite
    fig.add_trace(go.Scatter(
        x=df['T_Index'], y=df['Composite_Attention'], name='Composite_Attention_µ', 
        line=dict(color=Theme.ACCENT_PRIMARY, width=1), fill='tozeroy',
        fillcolor='rgba(106, 72, 187, 0.15)', mode='lines'
    ))
    
    # Lines for raw vectors
    signals = [
        ('Strain_Tension', Theme.SEMANTIC_CRITICAL, 'solid'),
        ('Load_Effort', Theme.SEMANTIC_WARNING, 'solid'),
        ('Recovery_Valence', Theme.SEMANTIC_GOOD, 'dash')
    ]
    
    for col, color, dash in signals:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['T_Index'], y=df[col], name=f"{col}_λ", 
                line=dict(color=color, width=1.5, dash=dash),
                mode='lines+markers', marker=dict(size=4)
            ))
    
    fig.update_layout(
        hovermode='x unified', height=350,
        margin=dict(l=40, r=20, t=10, b=40),
        xaxis=dict(title='Sequence Vector (T)', tickfont=dict(family='monospace', size=10)),
        yaxis=dict(title='Signal Amplitude', range=[0, 1], tickfont=dict(family='monospace', size=10)),
        legend=dict(font=dict(color=Theme.TEXT_SECONDARY, size=10, family='monospace'), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

@st.cache_resource
def get_phase_space_chart(df_q):
    """Generates the energy/entropy scatter plot."""
    fig = px.scatter(
        df_q, x='Entropy_Complexity', y='Energy_Signal', 
        hover_data=['T_Index'], color='Quadrant',
        color_discrete_map={
            'Q1': Theme.SEMANTIC_CRITICAL, 
            'Q2': Theme.SEMANTIC_WARNING, 
            'Q3': Theme.SEMANTIC_GOOD, 
            'Q4': Theme.ACCENT_PRIMARY
        }
    )
    
    fig.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.add_vline(x=0.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color='rgba(255,255,255,0.8)')))
    
    fig.update_layout(
        height=350, margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(tickfont=dict(family='monospace', size=10), title="Semantic Entropy (H) ->"),
        yaxis=dict(tickfont=dict(family='monospace', size=10), title="Kinetic Energy (E) ->"),
        showlegend=False
    )
    return fig

@st.cache_resource
def get_arc_chart(s_delta, a_delta):
    """Generates the character arc bar chart."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['Emotional Change', 'Agency Change'], y=[s_delta, a_delta],
        marker_color=[Theme.SEMANTIC_GOOD if s_delta >= 0 else Theme.SEMANTIC_CRITICAL, 
                        Theme.SEMANTIC_GOOD if a_delta >= 0 else Theme.SEMANTIC_WARNING],
        text=[f"{'+' if s_delta >= 0 else ''}{s_delta:.2f}", f"{'+' if a_delta >= 0 else ''}{a_delta:.2f}"],
        textposition='outside', textfont=dict(color=Theme.TEXT_SECONDARY, size=11)
    ))
    fig.update_layout(height=120, margin=dict(l=0, r=0, t=5, b=5), showlegend=False, bargap=0.5,
                        yaxis=dict(range=[-1, 1], showticklabels=False, showgrid=False))
    return fig

@st.cache_resource
def get_purpose_chart(purpose_list):
    """Generates the scene purpose distribution bar chart."""
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
        text=[p['purpose'] for p in purpose_list], textposition='inside', textfont=dict(size=8, color='white')
    )])
    fig.update_layout(height=120, margin=dict(l=10, r=10, t=5, b=30), showlegend=False, 
                        xaxis=dict(title="Scene →"), yaxis=dict(showticklabels=False))
    return fig

@st.cache_resource
def get_voice_radar(top_chars):
    """Generates the vocal fingerprint radar chart."""
    fig = go.Figure()
    colors = [Theme.SEMANTIC_CRITICAL, Theme.SEMANTIC_GOOD, Theme.ACCENT_PURPLE]
    for i, (char, data) in enumerate(top_chars):
        fig.add_trace(go.Scatterpolar(
            r=[data.get('complexity', 0), data.get('positivity', 0), data.get('line_count', 0)/top_chars[0][1].get('line_count', 1)],
            theta=['Complexity', 'Positivity', 'Dominance'], 
            fill='toself', name=char, line_color=colors[i % len(colors)]
        ))
    fig.update_layout(
        height=350, margin=dict(l=40, r=40, t=20, b=20), 
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], gridcolor='rgba(255,255,255,0.1)'),
            bgcolor='rgba(0,0,0,0)'
        ),
        legend=dict(font=dict(family='monospace', size=10, color=Theme.TEXT_SECONDARY))
    )
    return fig
