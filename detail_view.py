"""Detail drawer/view for individual questions."""

import json
from typing import Any, Dict
import streamlit as st
import pandas as pd
from table_view import format_label, get_decision_color


def truncate_expandable(text: str, max_lines: int = 3) -> str:
    """Truncate text to max lines with expand option.

    Args:
        text: Text to truncate
        max_lines: Maximum number of lines

    Returns:
        Truncated text
    """
    if not text:
        return ""

    lines = text.split('\n')
    if len(lines) <= max_lines:
        return text

    # Estimate character limit (assuming ~80 chars per line)
    char_limit = max_lines * 80
    if len(text) <= char_limit:
        return text

    return text[:char_limit] + "..."


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
        why_text = " ".join(why_list)
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
        st.markdown(f"**⚠️ Mismatch:** First guess was **{first_guess}**")
        if rethink_note:
            st.markdown(f"_{rethink_note}_")


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
