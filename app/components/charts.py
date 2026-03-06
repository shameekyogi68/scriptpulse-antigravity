import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from app.components.theme import Theme

@st.cache_resource
def get_engagement_chart(df_trace):
    """Generates the engagement journey chart with color-coded zones."""
    fig = go.Figure()
    
    # Color-coded background zones so the writer instantly knows what the graph means
    # Green zone: Calm / Story Building (0% - 35%)
    fig.add_hrect(y0=0, y1=0.35, fillcolor="rgba(0, 210, 160, 0.06)", line_width=0,
                  annotation_text="😌 Calm / Story Building", annotation_position="top left",
                  annotation_font=dict(size=10, color="rgba(0, 210, 160, 0.5)"))
    # Yellow zone: Rising Action (35% - 65%)
    fig.add_hrect(y0=0.35, y1=0.65, fillcolor="rgba(245, 121, 70, 0.06)", line_width=0,
                  annotation_text="⚡ Rising Action", annotation_position="top left",
                  annotation_font=dict(size=10, color="rgba(245, 121, 70, 0.5)"))
    # Red zone: Climax / High Stress (65% - 100%)
    fig.add_hrect(y0=0.65, y1=1.0, fillcolor="rgba(217, 41, 135, 0.06)", line_width=0,
                  annotation_text="🔥 High Tension / Climax", annotation_position="top left",
                  annotation_font=dict(size=10, color="rgba(217, 41, 135, 0.5)"))
    
    # Dynamic Hover text if available
    hover_template = '<b>Scene %{x}</b><br>Tension Level: %{y:.0%}<br>%{customdata[0]}<extra></extra>' if 'Hover_Text' in df_trace.columns else '<b>Scene %{x}</b><br>Tension Level: %{y:.0%}<extra></extra>'
    custom_data = [df_trace['Hover_Text']] if 'Hover_Text' in df_trace.columns else None
    
    # Main engagement line
    fig.add_trace(go.Scatter(
        x=df_trace.index,
        y=df_trace['attentional_signal'],
        fill='tozeroy',
        mode='lines',
        name='Tension Level',
        line=dict(color='rgba(106, 72, 187, 0.9)', width=2.5, shape='spline'),
        fillcolor='rgba(106, 72, 187, 0.12)',
        customdata=custom_data[0] if custom_data else None,
        hovertemplate=hover_template
    ))
    
    fig.update_layout(
        xaxis=dict(title="Scene Number →", range=[0, len(df_trace)-1]),
        yaxis=dict(title="Tension & Conflict →", range=[0, 1], tickformat='.0%'),
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
    
    fig.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.add_vline(x=0.5, line_dash="dash", line_color="rgba(255,255,255,0.2)")
    fig.update_traces(marker=dict(size=8, line=dict(width=1, color='rgba(255,255,255,0.8)')))
    
    fig.update_layout(
        height=350, margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(tickfont=dict(size=10), title="Story Detail (Dialogue, Clues, World-Building) →"),
        yaxis=dict(tickfont=dict(size=10), title="Pacing Speed (Action, Conflict) →"),
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
            theta=['Vocabulary Level', 'Positivity / Mood', 'Amount of Dialogue'], 
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
    fig.add_hline(y=0.5, line_dash="dash", line_color="rgba(255,255,255,0.1)")
    fig.add_vline(x=0.5, line_dash="dash", line_color="rgba(255,255,255,0.1)")
    
    fig.update_traces(marker=dict(size=10, color=Theme.ACCENT_PRIMARY, opacity=0.7, line=dict(width=1, color='white')))
    
    fig.update_layout(
        height=400, margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(title="Cognitive Effort →", range=[0, 1], tickformat='.0%'),
        yaxis=dict(title="Narrative Conflict →", range=[0, 1], tickformat='.0%'),
    )
    
    # Annotate quadrants
    fig.add_annotation(x=0.85, y=0.85, text="🔥 High Payoff", showarrow=False, font=dict(color=Theme.SEMANTIC_GOOD, size=10))
    fig.add_annotation(x=0.15, y=0.15, text="💤 Filler", showarrow=False, font=dict(color=Theme.TEXT_MUTED, size=10))
    fig.add_annotation(x=0.85, y=0.15, text="🧠 Dense / Heavy", showarrow=False, font=dict(color=Theme.SEMANTIC_WARNING, size=10))
    fig.add_annotation(x=0.15, y=0.85, text="⚡ Efficient Action", showarrow=False, font=dict(color=Theme.ACCENT_TEAL, size=10))

    return fig
