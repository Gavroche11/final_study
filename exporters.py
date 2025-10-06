"""Export functionality for CSV, JSON, and Markdown."""

import json
from typing import List
import pandas as pd
import streamlit as st
from io import StringIO


def export_to_csv(df: pd.DataFrame) -> str:
    """Export filtered DataFrame to CSV.

    Args:
        df: DataFrame to export

    Returns:
        CSV string
    """
    # Select display columns only
    export_df = df[[
        'question_no',
        'answer_label',
        'answer_text',
        'provided_key_label',
        'final_decision',
        'confidence',
        'depth',
        'has_images',
        'illegible',
        'mixed_lang',
        'runner_up'
    ]].copy()

    # Convert confidence to percentage
    export_df['confidence'] = (export_df['confidence'] * 100).round(2)

    return export_df.to_csv(index=False)


def export_to_json(df: pd.DataFrame) -> str:
    """Export filtered rows as JSON.

    Args:
        df: DataFrame to export

    Returns:
        JSON string
    """
    # Get raw data from each row
    raw_questions = []
    for _, row in df.iterrows():
        raw_data = row.get('_raw', {})
        if raw_data:
            raw_questions.append(raw_data)

    export_data = {
        'questions': raw_questions,
        'metadata': {
            'total_exported': len(raw_questions),
            'export_timestamp': pd.Timestamp.now().isoformat()
        }
    }

    return json.dumps(export_data, indent=2, ensure_ascii=False)


def export_to_markdown(df: pd.DataFrame, show_korean: bool = False) -> str:
    """Generate markdown review packet.

    Args:
        df: DataFrame to export
        show_korean: Whether to use Korean labels

    Returns:
        Markdown string
    """
    from table_view import format_label

    md_lines = [
        "# Exam Solution Review Packet\n",
        f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        f"**Total Questions:** {len(df)}\n",
        "---\n"
    ]

    for idx, (_, row) in enumerate(df.iterrows(), 1):
        md_lines.append(f"\n## {idx}. Question {row['question_no']}\n")

        # Basic info
        md_lines.append(f"**Depth:** {row['depth']}  ")
        md_lines.append(f"**Confidence:** {row['confidence'] * 100:.1f}%  ")
        md_lines.append(f"**Decision:** {row['final_decision']}\n")

        # Answer
        answer_label = format_label(row['answer_label'], show_korean)
        md_lines.append(f"\n### Chosen Answer: {answer_label}\n")
        md_lines.append(f"{row['answer_text']}\n")

        # Provided key
        if row.get('provided_key_label'):
            provided_label = format_label(row['provided_key_label'], show_korean)
            md_lines.append(f"\n**Provided Key:** {provided_label}\n")

        # Why (top 2 reasons)
        why_list = row.get('why', [])
        if why_list and isinstance(why_list, list):
            md_lines.append("\n### Why\n")
            for i, reason in enumerate(why_list[:2], 1):
                md_lines.append(f"{i}. {reason}\n")

        # Other options (top 2)
        others_list = row.get('others', [])
        if others_list and isinstance(others_list, list):
            md_lines.append("\n### Other Options\n")
            for other in others_list[:2]:
                if isinstance(other, dict):
                    label = format_label(other.get('label', ''), show_korean)
                    text = other.get('text', '')
                    reason = other.get('reason', '')

                    md_lines.append(f"\n**Option {label}:** {text}\n")
                    if reason:
                        md_lines.append(f"*Reason:* {reason}\n")

        # Flags
        flags = []
        if row.get('illegible'):
            flags.append("Illegible")
        if row.get('mixed_lang'):
            flags.append("Mixed Language")
        if row.get('has_images'):
            flags.append("Has Images")

        if flags:
            md_lines.append(f"\n**Flags:** {', '.join(flags)}\n")

        md_lines.append("\n---\n")

    return "".join(md_lines)


def render_export_section(df: pd.DataFrame, show_korean: bool = False):
    """Render export buttons and functionality.

    Args:
        df: Filtered DataFrame to export
        show_korean: Whether to use Korean labels
    """
    st.header("📤 Export")

    if len(df) == 0:
        st.warning("No data to export. Adjust filters to include data.")
        return

    st.write(f"Export current view ({len(df)} questions)")

    col1, col2, col3 = st.columns(3)

    with col1:
        # CSV Export
        csv_data = export_to_csv(df)
        st.download_button(
            label="📊 Export CSV",
            data=csv_data,
            file_name="exam_solutions_export.csv",
            mime="text/csv",
            help="Download filtered questions as CSV"
        )

    with col2:
        # JSON Export
        json_data = export_to_json(df)
        st.download_button(
            label="📋 Export JSON",
            data=json_data,
            file_name="exam_solutions_export.json",
            mime="application/json",
            help="Download filtered questions as JSON"
        )

    with col3:
        # Markdown Export
        md_data = export_to_markdown(df, show_korean)
        st.download_button(
            label="📝 Review Packet (MD)",
            data=md_data,
            file_name="exam_solutions_review.md",
            mime="text/markdown",
            help="Download review packet as Markdown"
        )

    # Preview section
    st.divider()

    with st.expander("📄 Preview Markdown Review Packet"):
        st.markdown(export_to_markdown(df.head(3), show_korean))
        if len(df) > 3:
            st.info(f"Preview shows first 3 questions. Full export contains all {len(df)} questions.")
