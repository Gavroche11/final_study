"""Sidebar filters and controls."""

from typing import Dict, List, Optional, Tuple
import streamlit as st
import pandas as pd


def build_sidebar(df: pd.DataFrame) -> Dict:
    """Build sidebar with filters and controls.

    Args:
        df: DataFrame with question data

    Returns:
        Dictionary with filter values and toggle states
    """
    st.sidebar.title("🔍 Filters & Controls")

    # Question range
    st.sidebar.subheader("Question Range")
    if len(df) > 0:
        # Try to convert question_no to numeric for proper ordering
        question_nos = df['question_no'].tolist()
        try:
            # Try numeric conversion
            numeric_questions = [int(q) for q in question_nos if str(q).strip()]
            min_q, max_q = min(numeric_questions), max(numeric_questions)
            q_range = st.sidebar.slider(
                "Select range",
                min_value=min_q,
                max_value=max_q,
                value=(min_q, max_q),
                key="question_range"
            )
        except (ValueError, TypeError):
            # Fall back to index-based range
            q_range = st.sidebar.slider(
                "Select range (by index)",
                min_value=0,
                max_value=len(df) - 1,
                value=(0, len(df) - 1),
                key="question_range"
            )
    else:
        q_range = (0, 0)

    st.sidebar.divider()

    # Multi-filters
    st.sidebar.subheader("Filters")

    # Has images filter
    has_images_filter = st.sidebar.radio(
        "Has Images",
        options=["All", "Yes", "No"],
        index=0,
        key="has_images_filter"
    )

    # Final decision filter
    decision_options = df['final_decision'].dropna().unique().tolist()
    decision_filter = st.sidebar.multiselect(
        "Final Decision",
        options=["All"] + sorted([d for d in decision_options if d]),
        default=["All"],
        key="decision_filter"
    )

    # Illegible flag
    illegible_filter = st.sidebar.radio(
        "Illegible",
        options=["All", "Yes", "No"],
        index=0,
        key="illegible_filter"
    )

    # Mixed language flag
    mixed_lang_filter = st.sidebar.radio(
        "Mixed Language",
        options=["All", "Yes", "No"],
        index=0,
        key="mixed_lang_filter"
    )

    # Depth filter
    depth_options = df['depth'].dropna().unique().tolist()
    depth_filter = st.sidebar.multiselect(
        "Depth",
        options=sorted([d for d in depth_options if d]),
        default=[],
        key="depth_filter"
    )

    # Confidence slider
    st.sidebar.subheader("Confidence Range")
    confidence_range = st.sidebar.slider(
        "Min - Max Confidence",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.05,
        key="confidence_range"
    )

    st.sidebar.divider()

    # Text search
    st.sidebar.subheader("Search")
    search_term = st.sidebar.text_input(
        "Search in why/others/findings/answer",
        value="",
        key="search_term"
    )

    st.sidebar.divider()

    # Display toggles
    st.sidebar.subheader("Display Options")
    show_korean = st.sidebar.checkbox(
        "Show Korean labels (①–⑤)",
        value=False,
        key="show_korean"
    )

    show_raw_json = st.sidebar.checkbox(
        "Show raw JSON per row",
        value=False,
        key="show_raw_json"
    )

    compact_mode = st.sidebar.checkbox(
        "Compact mode",
        value=False,
        key="compact_mode"
    )

    return {
        'question_range': q_range,
        'has_images': has_images_filter,
        'final_decision': decision_filter,
        'illegible': illegible_filter,
        'mixed_lang': mixed_lang_filter,
        'depth': depth_filter,
        'confidence_range': confidence_range,
        'search_term': search_term,
        'show_korean': show_korean,
        'show_raw_json': show_raw_json,
        'compact_mode': compact_mode
    }


def apply_filters(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Apply all filters to the DataFrame.

    Args:
        df: Original DataFrame
        filters: Filter values from sidebar

    Returns:
        Filtered DataFrame
    """
    filtered = df.copy()

    # Question range filter
    q_range = filters['question_range']
    try:
        # Try numeric filtering
        filtered['_q_num'] = pd.to_numeric(filtered['question_no'], errors='coerce')
        filtered = filtered[
            (filtered['_q_num'] >= q_range[0]) &
            (filtered['_q_num'] <= q_range[1])
        ]
        filtered = filtered.drop(columns=['_q_num'])
    except Exception:
        # Fall back to index filtering
        filtered = filtered.iloc[q_range[0]:q_range[1] + 1]

    # Has images filter
    if filters['has_images'] != "All":
        has_images_val = filters['has_images'] == "Yes"
        filtered = filtered[filtered['has_images'] == has_images_val]

    # Final decision filter
    if "All" not in filters['final_decision'] and len(filters['final_decision']) > 0:
        filtered = filtered[filtered['final_decision'].isin(filters['final_decision'])]

    # Illegible filter
    if filters['illegible'] != "All":
        illegible_val = filters['illegible'] == "Yes"
        filtered = filtered[filtered['illegible'] == illegible_val]

    # Mixed language filter
    if filters['mixed_lang'] != "All":
        mixed_lang_val = filters['mixed_lang'] == "Yes"
        filtered = filtered[filtered['mixed_lang'] == mixed_lang_val]

    # Depth filter
    if len(filters['depth']) > 0:
        filtered = filtered[filtered['depth'].isin(filters['depth'])]

    # Confidence range
    conf_range = filters['confidence_range']
    filtered = filtered[
        (filtered['confidence'] >= conf_range[0]) &
        (filtered['confidence'] <= conf_range[1])
    ]

    # Text search
    if filters['search_term'].strip():
        from data_loader import search_text_fields
        mask = filtered.apply(
            lambda row: search_text_fields(row, filters['search_term']),
            axis=1
        )
        filtered = filtered[mask]

    return filtered
