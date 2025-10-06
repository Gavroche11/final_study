"""KPI summary header rendering."""

from typing import Dict
import streamlit as st
import pandas as pd


def render_kpis(df: pd.DataFrame, doc_metadata: Dict):
    """Render KPI summary header.

    Args:
        df: Filtered DataFrame
        doc_metadata: Document metadata
    """
    st.title("📊 Exam Solution Audit Dashboard")

    # Document info
    if doc_metadata.get('has_global_answer_key'):
        st.info(
            f"**Document:** {doc_metadata.get('source', 'Unknown')} | "
            f"**Has Global Answer Key** | "
            f"Pages: {doc_metadata.get('pages_parsed', 'N/A')}"
        )

    st.divider()

    # KPI metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)

    # Total questions
    total_questions = len(df)
    col1.metric("Total Questions", total_questions)

    # Agreement metrics
    agree_count = len(df[df['final_decision'] == 'agree_with_key'])
    override_count = len(df[df['final_decision'] == 'override_key'])

    col2.metric(
        "Agree with Key",
        f"{agree_count} ({agree_count / total_questions * 100:.1f}%)" if total_questions > 0 else "0 (0%)"
    )

    col3.metric(
        "Override Key",
        f"{override_count} ({override_count / total_questions * 100:.1f}%)" if total_questions > 0 else "0 (0%)",
        delta=None,
        delta_color="inverse"
    )

    # Average confidence
    avg_confidence = df['confidence'].mean() if len(df) > 0 else 0.0
    col4.metric("Avg Confidence", f"{avg_confidence * 100:.1f}%")

    # Has images count
    has_images_count = len(df[df['has_images'] == True])
    col5.metric("With Images", has_images_count)

    st.divider()


def render_mini_stats(df: pd.DataFrame):
    """Render mini statistics below main KPIs.

    Args:
        df: Filtered DataFrame
    """
    col1, col2, col3, col4 = st.columns(4)

    # Mismatch count
    mismatch_count = len(df[df['mismatch'] == True])
    col1.metric(
        "Mismatches",
        mismatch_count,
        help="Questions where initial guess differed from provided key"
    )

    # Illegible count
    illegible_count = len(df[df['illegible'] == True])
    col2.metric(
        "Illegible",
        illegible_count,
        help="Questions flagged as illegible"
    )

    # Mixed language count
    mixed_lang_count = len(df[df['mixed_lang'] == True])
    col3.metric(
        "Mixed Language",
        mixed_lang_count,
        help="Questions with mixed language content"
    )

    # Runner-up count
    runner_up_count = len(df[df['runner_up'].str.len() > 0]) if 'runner_up' in df.columns else 0
    col4.metric(
        "Has Runner-up",
        runner_up_count,
        help="Questions with a close second choice"
    )

    st.divider()
