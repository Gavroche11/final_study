"""Analytics charts and visualizations."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render_analytics(df: pd.DataFrame):
    """Render analytics charts.

    Args:
        df: Filtered DataFrame
    """
    st.header("📊 Analytics")

    if len(df) == 0:
        st.warning("No data to display analytics.")
        return

    # Create tabs for different chart categories
    tab1, tab2, tab3, tab4 = st.tabs([
        "Decision Analysis",
        "Confidence Distribution",
        "Answer Distribution",
        "Advanced Metrics"
    ])

    with tab1:
        render_decision_charts(df)

    with tab2:
        render_confidence_charts(df)

    with tab3:
        render_answer_distribution(df)

    with tab4:
        render_advanced_metrics(df)


def render_decision_charts(df: pd.DataFrame):
    """Render decision-related charts.

    Args:
        df: DataFrame with questions
    """
    st.subheader("Decision Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Accuracy vs Key pie chart
        decision_counts = df['final_decision'].value_counts()

        fig = go.Figure(data=[go.Pie(
            labels=decision_counts.index,
            values=decision_counts.values,
            marker=dict(colors=['#00cc66', '#ff4b4b', '#808080']),
            hole=0.3
        )])

        fig.update_layout(
            title="Agree vs Override",
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Mismatch analysis
        mismatch_data = df.groupby(['final_decision', 'mismatch']).size().reset_index(name='count')

        fig = px.bar(
            mismatch_data,
            x='final_decision',
            y='count',
            color='mismatch',
            title="Decisions by Mismatch Status",
            barmode='group',
            color_discrete_map={True: '#ffa500', False: '#4a90e2'}
        )

        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


def render_confidence_charts(df: pd.DataFrame):
    """Render confidence distribution charts.

    Args:
        df: DataFrame with questions
    """
    st.subheader("Confidence Distribution")

    col1, col2 = st.columns(2)

    with col1:
        # Confidence histogram
        fig = px.histogram(
            df,
            x='confidence',
            nbins=20,
            title="Confidence Score Distribution",
            labels={'confidence': 'Confidence', 'count': 'Count'},
            color_discrete_sequence=['#4a90e2']
        )

        fig.update_layout(
            xaxis_title="Confidence",
            yaxis_title="Count",
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Confidence by decision
        fig = px.box(
            df,
            x='final_decision',
            y='confidence',
            title="Confidence by Decision Type",
            color='final_decision',
            color_discrete_map={
                'agree_with_key': '#00cc66',
                'override_key': '#ff4b4b'
            }
        )

        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)


def render_answer_distribution(df: pd.DataFrame):
    """Render answer label distribution.

    Args:
        df: DataFrame with questions
    """
    st.subheader("Answer Label Distribution")

    col1, col2 = st.columns(2)

    with col1:
        # Count by answer label
        answer_counts = df['answer_label'].value_counts().sort_index()

        fig = px.bar(
            x=answer_counts.index,
            y=answer_counts.values,
            title="Distribution by Answer Label",
            labels={'x': 'Answer Label', 'y': 'Count'},
            color=answer_counts.values,
            color_continuous_scale='Blues'
        )

        fig.update_layout(
            showlegend=False,
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Answer vs provided key match
        if df['provided_key_label'].notna().any():
            df_with_key = df[df['provided_key_label'].notna()].copy()
            df_with_key['matches_key'] = df_with_key['answer_label'] == df_with_key['provided_key_label']

            match_counts = df_with_key['matches_key'].value_counts()

            fig = go.Figure(data=[go.Pie(
                labels=['Matches Key', 'Differs from Key'],
                values=[match_counts.get(True, 0), match_counts.get(False, 0)],
                marker=dict(colors=['#00cc66', '#ff4b4b']),
                hole=0.3
            )])

            fig.update_layout(
                title="Answer vs Provided Key",
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)


def render_advanced_metrics(df: pd.DataFrame):
    """Render advanced metric charts.

    Args:
        df: DataFrame with questions
    """
    st.subheader("Advanced Metrics")

    col1, col2 = st.columns(2)

    with col1:
        # Overrides by depth
        if df['depth'].notna().any():
            override_by_depth = df.groupby('depth')['final_decision'].apply(
                lambda x: (x == 'override_key').sum()
            ).reset_index(name='override_count')

            total_by_depth = df.groupby('depth').size().reset_index(name='total')
            override_by_depth = override_by_depth.merge(total_by_depth, on='depth')
            override_by_depth['override_rate'] = (
                override_by_depth['override_count'] / override_by_depth['total'] * 100
            )

            fig = px.bar(
                override_by_depth,
                x='depth',
                y='override_rate',
                title="Override Rate by Depth",
                labels={'override_rate': 'Override Rate (%)', 'depth': 'Depth'},
                color='override_rate',
                color_continuous_scale='Reds'
            )

            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Override by has_images
        override_by_images = df.groupby('has_images')['final_decision'].apply(
            lambda x: (x == 'override_key').sum()
        ).reset_index(name='override_count')

        total_by_images = df.groupby('has_images').size().reset_index(name='total')
        override_by_images = override_by_images.merge(total_by_images, on='has_images')
        override_by_images['override_rate'] = (
            override_by_images['override_count'] / override_by_images['total'] * 100
        )

        fig = px.bar(
            override_by_images,
            x='has_images',
            y='override_rate',
            title="Override Rate by Image Presence",
            labels={'override_rate': 'Override Rate (%)', 'has_images': 'Has Images'},
            color='override_rate',
            color_continuous_scale='Oranges'
        )

        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Additional insights
    st.divider()
    st.subheader("📈 Key Insights")

    col1, col2, col3 = st.columns(3)

    # Avg confidence for overrides
    override_conf = df[df['final_decision'] == 'override_key']['confidence'].mean()
    agree_conf = df[df['final_decision'] == 'agree_with_key']['confidence'].mean()

    col1.metric(
        "Avg Confidence (Override)",
        f"{override_conf * 100:.1f}%" if not pd.isna(override_conf) else "N/A"
    )

    col2.metric(
        "Avg Confidence (Agree)",
        f"{agree_conf * 100:.1f}%" if not pd.isna(agree_conf) else "N/A"
    )

    # Questions with low confidence
    low_conf_count = len(df[df['confidence'] < 0.7])
    col3.metric(
        "Low Confidence (<70%)",
        low_conf_count
    )
