"""Main Streamlit app for exam solution dashboard."""

import os
import glob
import streamlit as st
from streamlit.components.v1 import html
from data_loader import (
    load_json,
    load_json_from_bytes,
    validate_json_schema,
    normalize_questions
)
from detail_view import render_detail_view
from config import *


# Page configuration
st.set_page_config(
    page_title="Exam Solution Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def main():
    """Main application entry point."""

    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'uploaded_files_data' not in st.session_state:
        st.session_state.uploaded_files_data = {}
    if 'current_file' not in st.session_state:
        st.session_state.current_file = None
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'current_question_idx' not in st.session_state:
        st.session_state.current_question_idx = 0

    # Password protection
    if not st.session_state.authenticated:
        st.title("🔒 Exam Solution Dashboard")
        st.markdown("### Please enter the password to continue")

        # Use a form to capture Enter key properly
        with st.form(key="login_form"):
            password = st.text_input("Password", type="password", key="password_input")
            login_clicked = st.form_submit_button("Login", type="primary")

        # Check password only on form submit (button click or Enter key)
        if login_clicked:
            if password == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password")

        return

    # File upload section (minimal UI in collapsed sidebar)
    with st.sidebar:
        st.title("📁 Data Source")

        # Load default files from ./data directory on first run
        if not st.session_state.uploaded_files_data:
            default_files = sorted(glob.glob(os.path.join(DATA_DIR, "*.json")))
            if default_files:
                for file_path in default_files:
                    file_name = os.path.basename(file_path)
                    try:
                        data = load_json(file_path)
                        missing_fields = validate_json_schema(data)
                        if not missing_fields:
                            st.session_state.uploaded_files_data[file_name] = {
                                'data': data,
                                'df': normalize_questions(data)
                            }
                    except Exception as e:
                        pass  # Silently skip files that fail to load

        uploaded_files = st.file_uploader(
            "Upload JSON file(s)",
            type=['json'],
            help="Upload your exam solutions JSON file(s)",
            accept_multiple_files=True
        )

        # Process uploaded files (add to existing files)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                if file_name not in st.session_state.uploaded_files_data:
                    try:
                        file_bytes = uploaded_file.read()
                        data = load_json_from_bytes(file_bytes)

                        # Validate schema
                        missing_fields = validate_json_schema(data)
                        if not missing_fields:
                            st.session_state.uploaded_files_data[file_name] = {
                                'data': data,
                                'df': normalize_questions(data)
                            }
                    except Exception as e:
                        st.error(f"❌ Error loading {file_name}: {str(e)}")

        # File selection dropdown
        if st.session_state.uploaded_files_data:
            file_names = sorted(st.session_state.uploaded_files_data.keys())

            # Set default current file if not set
            if st.session_state.current_file is None or st.session_state.current_file not in file_names:
                st.session_state.current_file = file_names[0]

            selected_file = st.selectbox(
                "Select file to view",
                options=file_names,
                index=file_names.index(st.session_state.current_file) if st.session_state.current_file in file_names else 0,
                help="Choose which file to view"
            )

            # Update current file and data if selection changed
            if selected_file != st.session_state.current_file:
                st.session_state.current_file = selected_file
                st.session_state.current_question_idx = 0
                st.rerun()

            # Load the selected file's data
            st.session_state.df = st.session_state.uploaded_files_data[selected_file]['df']

            st.sidebar.success(f"✅ {len(file_names)} file(s) loaded")

    # Check if data is loaded
    if st.session_state.df is None or len(st.session_state.df) == 0:
        st.info("👈 No JSON files found in ./data directory. Please add JSON files to ./data or upload files using the sidebar.")
        return

    df = st.session_state.df
    total_questions = len(df)

    # Keyboard navigation with JavaScript - inject into main document
    keyboard_js = """
    <script>
    // Wait for parent document to be ready
    setTimeout(function() {
        const parentDoc = window.parent.document;

        // Remove old listener if exists
        if (window.parent._examKeyListener) {
            parentDoc.removeEventListener('keydown', window.parent._examKeyListener, true);
        }

        window.parent._examKeyListener = function(event) {
            // Don't trigger in input fields
            const activeTag = parentDoc.activeElement?.tagName?.toLowerCase();
            if (activeTag === 'input' || activeTag === 'textarea' || activeTag === 'select') {
                return;
            }

            let targetButton = null;

            // Map arrow keys to actions
            if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
                // Find Previous button
                const allButtons = parentDoc.querySelectorAll('button');
                for (let i = 0; i < allButtons.length; i++) {
                    const btn = allButtons[i];
                    if (btn.textContent && btn.textContent.indexOf('Previous') !== -1) {
                        targetButton = btn;
                        break;
                    }
                }
            } else if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
                // Find Next button
                const allButtons = parentDoc.querySelectorAll('button');
                for (let i = 0; i < allButtons.length; i++) {
                    const btn = allButtons[i];
                    if (btn.textContent && btn.textContent.indexOf('Next') !== -1) {
                        targetButton = btn;
                        break;
                    }
                }
            }

            // Click the button if found and enabled
            if (targetButton && !targetButton.disabled) {
                event.preventDefault();
                event.stopPropagation();
                targetButton.click();
            }
        };

        // Add listener with capture phase
        parentDoc.addEventListener('keydown', window.parent._examKeyListener, true);
    }, 100);
    </script>
    """

    html(keyboard_js, height=0)

    # Show current file name
    if st.session_state.current_file:
        st.markdown(f"**📄 File:** {st.session_state.current_file}")

    # Navigation controls at top
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])

    with col1:
        if st.button("← Previous", disabled=st.session_state.current_question_idx == 0, use_container_width=True):
            st.session_state.current_question_idx = max(0, st.session_state.current_question_idx - 1)
            st.rerun()

    with col2:
        st.markdown(f"<h3 style='text-align: center; margin: 0;'>Question {st.session_state.current_question_idx + 1} of {total_questions}</h3>", unsafe_allow_html=True)

    with col3:
        go_to_question = st.number_input("Go to Q#", min_value=1, max_value=total_questions, value=st.session_state.current_question_idx + 1, step=1, label_visibility="collapsed")
        if go_to_question != st.session_state.current_question_idx + 1:
            st.session_state.current_question_idx = go_to_question - 1
            st.rerun()

    with col4:
        if st.button("Next →", disabled=st.session_state.current_question_idx >= total_questions - 1, use_container_width=True):
            st.session_state.current_question_idx = min(total_questions - 1, st.session_state.current_question_idx + 1)
            st.rerun()

    st.markdown("---")

    # Display current question detail view
    current_row = df.iloc[st.session_state.current_question_idx]
    render_detail_view(current_row, show_korean=False, show_raw_json=False)


if __name__ == "__main__":
    main()
