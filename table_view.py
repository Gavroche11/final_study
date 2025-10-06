"""Main table view with pagination and selection."""

from typing import Optional
import streamlit as st
import pandas as pd
from streamlit.components.v1 import html


KOREAN_LABELS = {
    '1': '①',
    '2': '②',
    '3': '③',
    '4': '④',
    '5': '⑤',
}


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length.

    Args:
        text: Text to truncate
        max_length: Maximum character length

    Returns:
        Truncated text with ellipsis if needed
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + "..."


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


def get_decision_color(decision: str, mismatch: bool = False) -> str:
    """Get color for decision chip.

    Args:
        decision: Final decision value
        mismatch: Whether there was a mismatch

    Returns:
        CSS color string
    """
    if decision == 'override_key':
        return '#ff4b4b'  # Red
    elif decision == 'agree_with_key':
        if mismatch:
            return '#ffa500'  # Amber/Orange
        return '#00cc66'  # Green
    return '#808080'  # Gray


def render_table(df: pd.DataFrame, show_korean: bool = False, compact_mode: bool = False) -> Optional[int]:
    """Render main table with pagination and keyboard navigation.

    Args:
        df: Filtered DataFrame
        show_korean: Whether to show Korean labels
        compact_mode: Whether to use compact display

    Returns:
        Selected row index (if any)
    """
    if len(df) == 0:
        st.warning("No rows match current filters.")
        return None

    st.subheader(f"📋 Questions ({len(df)} total)")

    # Pagination settings
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 0
    if 'selected_row_in_page' not in st.session_state:
        st.session_state.selected_row_in_page = 0

    items_per_page = 10 if not compact_mode else 20

    # Calculate pagination
    total_pages = (len(df) - 1) // items_per_page + 1
    start_idx = st.session_state.page_number * items_per_page
    end_idx = min(start_idx + items_per_page, len(df))

    # Get current page data
    page_df = df.iloc[start_idx:end_idx].copy()
    page_size = len(page_df)

    # Inject JavaScript for keyboard navigation
    keyboard_js = """
    <script>
    const doc = window.parent.document;

    // Remove existing listener if present
    if (window.parent.keyboardNavHandler) {
        doc.removeEventListener('keydown', window.parent.keyboardNavHandler);
    }

    window.parent.keyboardNavHandler = function(e) {
        // Only handle if not in an input/textarea/select
        const tag = e.target.tagName.toLowerCase();
        if (tag === 'input' || tag === 'textarea' || tag === 'select') {
            return;
        }

        let buttonSelector = null;

        switch(e.key) {
            case 'ArrowUp':
                buttonSelector = 'button[kind="secondary"]';
                // Find the up arrow button
                const buttons = Array.from(doc.querySelectorAll(buttonSelector));
                const upBtn = buttons.find(b => b.innerText.includes('⬆'));
                if (upBtn && !upBtn.disabled) {
                    upBtn.click();
                    e.preventDefault();
                }
                break;
            case 'ArrowDown':
                buttonSelector = 'button[kind="secondary"]';
                const downButtons = Array.from(doc.querySelectorAll(buttonSelector));
                const downBtn = downButtons.find(b => b.innerText.includes('⬇'));
                if (downBtn && !downBtn.disabled) {
                    downBtn.click();
                    e.preventDefault();
                }
                break;
            case 'ArrowLeft':
                buttonSelector = 'button[kind="secondary"]';
                const leftButtons = Array.from(doc.querySelectorAll(buttonSelector));
                const leftBtn = leftButtons.find(b => b.innerText.includes('⬅'));
                if (leftBtn && !leftBtn.disabled) {
                    leftBtn.click();
                    e.preventDefault();
                }
                break;
            case 'ArrowRight':
                buttonSelector = 'button[kind="secondary"]';
                const rightButtons = Array.from(doc.querySelectorAll(buttonSelector));
                const rightBtn = rightButtons.find(b => b.innerText.includes('➡'));
                if (rightBtn && !rightBtn.disabled) {
                    rightBtn.click();
                    e.preventDefault();
                }
                break;
        }
    };

    doc.addEventListener('keydown', window.parent.keyboardNavHandler);
    </script>
    """

    html(keyboard_js, height=0)

    # Navigation buttons
    col_nav1, col_nav2, col_nav3, col_nav4, col_pag1, col_pag2, col_pag3 = st.columns([1, 1, 1, 1, 1, 2, 1])

    with col_nav1:
        if st.button("⬆️", key="nav_up", help="Previous question in page (↑)", type="secondary"):
            if st.session_state.selected_row_in_page > 0:
                st.session_state.selected_row_in_page -= 1
                st.rerun()

    with col_nav2:
        if st.button("⬇️", key="nav_down", help="Next question in page (↓)", type="secondary"):
            if st.session_state.selected_row_in_page < page_size - 1:
                st.session_state.selected_row_in_page += 1
                st.rerun()

    with col_nav3:
        if st.button("⬅️", key="nav_prev", help="Previous question (←)", type="secondary"):
            # Navigate to previous question globally
            if st.session_state.selected_row_in_page > 0:
                st.session_state.selected_row_in_page -= 1
            elif st.session_state.page_number > 0:
                st.session_state.page_number -= 1
                st.session_state.selected_row_in_page = items_per_page - 1
            st.rerun()

    with col_nav4:
        if st.button("➡️", key="nav_next", help="Next question (→)", type="secondary"):
            # Navigate to next question globally
            if st.session_state.selected_row_in_page < page_size - 1:
                st.session_state.selected_row_in_page += 1
            elif st.session_state.page_number < total_pages - 1:
                st.session_state.page_number += 1
                st.session_state.selected_row_in_page = 0
            st.rerun()

    with col_pag1:
        if st.button("◀ Page", disabled=st.session_state.page_number == 0):
            st.session_state.page_number -= 1
            st.session_state.selected_row_in_page = 0
            st.rerun()

    with col_pag2:
        st.write(f"Page {st.session_state.page_number + 1} of {total_pages}")

    with col_pag3:
        if st.button("Page ▶", disabled=st.session_state.page_number >= total_pages - 1):
            st.session_state.page_number += 1
            st.session_state.selected_row_in_page = 0
            st.rerun()

    # Ensure selected_row_in_page is within bounds
    if st.session_state.selected_row_in_page >= page_size:
        st.session_state.selected_row_in_page = page_size - 1

    # Prepare display dataframe
    display_df = pd.DataFrame({
        'Q#': page_df['question_no'],
        'Answer': page_df.apply(
            lambda row: format_label(row['answer_label'], show_korean),
            axis=1
        ),
        'Text': page_df['answer_text'].apply(lambda x: truncate_text(str(x), 40 if compact_mode else 60)),
        'Key': page_df.apply(
            lambda row: format_label(row['provided_key_label'], show_korean),
            axis=1
        ),
        'Decision': page_df['final_decision'],
        'Conf %': (page_df['confidence'] * 100).round(1),
        'Depth': page_df['depth'],
        'Images': page_df['has_images'].apply(lambda x: '✓' if x else ''),
        'Illegible': page_df['illegible'].apply(lambda x: '⚠️' if x else ''),
    })

    # Use Streamlit's native dataframe with selection
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Q#': st.column_config.TextColumn('Q#', width='small'),
            'Answer': st.column_config.TextColumn('Answer', width='small'),
            'Text': st.column_config.TextColumn('Text', width='large'),
            'Key': st.column_config.TextColumn('Key', width='small'),
            'Decision': st.column_config.TextColumn('Decision', width='medium'),
            'Conf %': st.column_config.NumberColumn('Conf %', width='small', format='%.1f%%'),
            'Depth': st.column_config.TextColumn('Depth', width='small'),
            'Images': st.column_config.TextColumn('📷', width='small'),
            'Illegible': st.column_config.TextColumn('⚠️', width='small'),
        }
    )

    # Highlight current selection
    question_options = page_df['question_no'].tolist()
    if question_options:
        current_selection_idx = min(st.session_state.selected_row_in_page, len(question_options) - 1)
        selected_q = question_options[current_selection_idx]

        st.info(f"**Currently viewing:** Question {selected_q} (row {current_selection_idx + 1} of {len(question_options)})")

        # Find the selected row index in original df
        selected_idx = df[df['question_no'] == selected_q].index[0]
        return selected_idx

    return None


def render_decision_chips(df: pd.DataFrame):
    """Render visual decision chips legend.

    Args:
        df: DataFrame with questions
    """
    st.markdown("""
    **Decision Legend:**
    🟢 Agree with Key | 🟠 Agree (with mismatch) | 🔴 Override Key
    """)
