"""Detail drawer/view for individual questions."""

import json
from typing import Any, Dict
import streamlit as st
import pandas as pd


KOREAN_LABELS = {
    '1': '①',
    '2': '②',
    '3': '③',
    '4': '④',
    '5': '⑤',
}


def format_label(label: str, show_korean: bool = False) -> str:
    """Format answer label with optional Korean characters.

    Args:
        label: Label (e.g., '1', '2')
        show_korean: Whether to show Korean labels

    Returns:
        Formatted label
    """
    if not label:
        return ""

    if show_korean and str(label) in KOREAN_LABELS:
        return KOREAN_LABELS[str(label)]

    return str(label)

def render_detail_view(row: pd.Series, show_korean: bool = False, show_raw_json: bool = False):
    """Render detail view for a selected question.

    Args:
        row: DataFrame row for the question
        show_korean: Whether to show Korean labels
        show_raw_json: Whether to show raw JSON
    """
    raw_data = row.get('_raw', {})

    # Compact metadata line
    decision = row.get('final_decision', '')
    if decision == 'override_key':
        decision_icon = '🔴'
    elif decision == 'agree_with_key':
        decision_icon = '🟢' if not row.get('mismatch') else '🟠'
    else:
        decision_icon = '⚪'

    confidence_pct = row['confidence'] * 100
    flags = []
    if row.get('illegible'):
        flags.append("⚠️")
    if row.get('mixed_lang'):
        flags.append("🌐")
    if row.get('has_images'):
        flags.append("📷")

    flag_str = " ".join(flags) if flags else ""

    st.markdown(f"**Q{row['question_no']}** | {decision_icon} {decision} | Confidence {confidence_pct:.0f}%")

    # Chosen answer (compact)
    answer_label = format_label(row['answer_label'], show_korean)
    provided_key_label = format_label(row.get('provided_key_label', ''), show_korean)

    key_info = f" | Key: {provided_key_label}" if provided_key_label else ""
    runner_info = f" | Runner-up: {row['runner_up']}" if row.get('runner_up') else ""

    st.markdown(f"**✓ Answer {answer_label}**{key_info}{runner_info}")
    st.markdown(f"{row['answer_text']}")

    # Why section - compact (concatenated)
    st.markdown("**💡 Why:**")
    why_list = row.get('why', [])
    if why_list and isinstance(why_list, list):
        why_text = "\n".join(why_list)
        st.markdown(why_text)
    else:
        st.markdown("_No reasons provided_")

    # Findings - compact
    findings_list = row.get('findings', [])
    if findings_list and isinstance(findings_list, list):
        st.markdown("**🔍 Findings:**")
        findings_text = "  \n".join([f"• {finding}" for finding in findings_list])
        st.markdown(findings_text)

    # Other options - compact
    st.markdown("**❌ Distractors:**")
    others_list = row.get('others', [])
    if others_list and isinstance(others_list, list):
        for other in others_list:
            if isinstance(other, dict):
                label = format_label(other.get('label', ''), show_korean)
                text = other.get('text', '')
                reason = other.get('reason', '')

                st.markdown(f"**{label}.** {text}")
                if reason:
                    st.markdown(f"   ↳ _{reason}_")
    else:
        st.markdown("_No other options_")

    # Mismatch note at the bottom
    if row.get('mismatch'):
        rethink_note = row.get('_raw', {}).get('rethink', {}).get('note', '')
        first_guess = row.get('first_guess', 'unknown')
        if isinstance(first_guess, dict):
            if 'label' in first_guess and 'text' in first_guess:
                first_guess = f"{format_label(first_guess['label'], show_korean)}. {first_guess['text']}"
        st.markdown(f"**⚠️ Mismatch:** First guess was **{first_guess}**.")
        if rethink_note:
            st.markdown(f"_{rethink_note}_")

    # Erratum note at the bottom
    erratum_note = row.get('_raw', {}).get('metadata', {}).get('erratum_note', '')
    if erratum_note:
        st.markdown(f"**📝 Erratum:** {erratum_note}")

    # Teaching points at the bottom
    teaching_points = row.get('_raw', {}).get('teaching_points', [])
    if teaching_points and isinstance(teaching_points, list):
        st.markdown("**📚 Teaching Points:**")
        teaching_points_text = "\n".join(teaching_points)
        st.markdown(teaching_points_text)


def render_detail_sidebar(row: pd.Series, show_korean: bool = False, show_raw_json: bool = False):
    """Render detail view in a more compact sidebar-style layout.

    Args:
        row: DataFrame row for the question
        show_korean: Whether to show Korean labels
        show_raw_json: Whether to show raw JSON
    """
    raw_data = row.get('_raw', {})

    with st.container():
        st.markdown(f"### Question {row['question_no']}")

        # Quick stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Confidence", f"{row['confidence'] * 100:.1f}%")
        with col2:
            decision = row.get('final_decision', 'N/A')
            st.metric("Decision", decision)

        st.markdown(f"**Depth:** {row['depth']}")

        # Answer
        answer_label = format_label(row['answer_label'], show_korean)
        st.success(f"**Answer {answer_label}:** {row['answer_text'][:100]}...")

        # Why (condensed)
        why_list = row.get('why', [])
        if why_list:
            with st.expander("💡 Why", expanded=True):
                for idx, item in enumerate(why_list[:2], 1):  # Show first 2
                    st.write(f"{idx}. {item[:150]}...")

        # Others (condensed)
        others_list = row.get('others', [])
        if others_list:
            with st.expander(f"📚 Other Options ({len(others_list)})"):
                for other in others_list:
                    if isinstance(other, dict):
                        label = format_label(other.get('label', ''), show_korean)
                        st.write(f"**{label}:** {other.get('text', '')[:80]}...")

        # Raw JSON
        if show_raw_json:
            with st.expander("📄 Raw JSON"):
                st.json(raw_data)
