"""Data loading and normalization for exam solutions JSON."""

import json
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st


def safe_get(obj: Any, path: str, default: Any = None) -> Any:
    """Safely get nested dictionary values using dot notation.

    Args:
        obj: Dictionary or object to traverse
        path: Dot-separated path (e.g., 'rethink.mismatch')
        default: Default value if path not found

    Returns:
        Value at path or default
    """
    keys = path.split('.')
    current = obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
        if current is None:
            return default
    return current


def validate_json_schema(data: Dict[str, Any]) -> List[str]:
    """Validate that JSON has required fields.

    Args:
        data: Parsed JSON data

    Returns:
        List of missing required fields (empty if valid)
    """
    missing = []

    if 'questions' not in data:
        missing.append('questions')
        return missing

    if not isinstance(data['questions'], list):
        missing.append('questions (must be a list)')
        return missing

    if len(data['questions']) == 0:
        missing.append('questions (list is empty)')
        return missing

    # Check first question for critical fields
    sample_q = data['questions'][0]
    critical_fields = ['question_no', 'answer']

    for field in critical_fields:
        if field not in sample_q:
            missing.append(f'questions[0].{field}')

    return missing


@st.cache_data
def load_json(file_path: str) -> Dict[str, Any]:
    """Load and cache JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        Exception: If file cannot be loaded or parsed
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@st.cache_data
def load_json_from_bytes(file_bytes: bytes) -> Dict[str, Any]:
    """Load JSON from uploaded file bytes.

    Args:
        file_bytes: File bytes from uploaded file

    Returns:
        Parsed JSON data
    """
    return json.loads(file_bytes.decode('utf-8'))


def normalize_questions(data: Dict[str, Any]) -> pd.DataFrame:
    """Normalize questions list into a flat DataFrame.

    Args:
        data: Parsed JSON data

    Returns:
        DataFrame with normalized question data
    """
    questions = data.get('questions', [])

    rows = []
    for q in questions:
        row = {
            # Basic fields
            'question_no': q.get('question_no', ''),
            'depth': q.get('depth', safe_get(data, 'defaults.depth', '')),

            # Answer fields
            'answer_label': safe_get(q, 'answer.label', ''),
            'answer_text': safe_get(q, 'answer.text', ''),

            # Rethink fields
            'provided_key_label': safe_get(q, 'rethink.provided_key.label', ''),
            'first_guess': safe_get(q, 'rethink.first_guess', ''),
            'final_decision': safe_get(q, 'rethink.final_decision', ''),
            'override_key': safe_get(q, 'rethink.override_key', False),
            'mismatch': safe_get(q, 'rethink.mismatch', False),

            # Flags
            'illegible': safe_get(q, 'flags.illegible', False),
            'mixed_lang': safe_get(q, 'flags.mixed_lang', False),

            # Other fields
            'confidence': q.get('confidence', 0.0),
            'runner_up': q.get('runner_up', ''),

            # Metadata
            'has_images': safe_get(q, 'metadata.input_metadata.has_images', False),
            'version': safe_get(q, 'metadata.version', ''),

            # Lists (keep as lists for filtering)
            'why': q.get('why', []),
            'findings': q.get('findings', []),
            'others': q.get('others', []),

            # Store raw question for detail view
            '_raw': q
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # Ensure numeric types
    if 'confidence' in df.columns:
        df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce').fillna(0.0)

    return df


def get_document_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract document-level metadata.

    Args:
        data: Parsed JSON data

    Returns:
        Dictionary with document metadata
    """
    return {
        'source': safe_get(data, 'doc.source', 'Unknown'),
        'pages_parsed': safe_get(data, 'doc.pages_parsed', 0),
        'has_global_answer_key': safe_get(data, 'doc.has_global_answer_key', False),
        'default_depth': safe_get(data, 'defaults.depth', '')
    }


def search_text_fields(row: pd.Series, search_term: str) -> bool:
    """Search across text fields in a question row.

    Args:
        row: DataFrame row
        search_term: Search term (case-insensitive)

    Returns:
        True if search term found in any field
    """
    search_term = search_term.lower()

    # Search in answer text
    if search_term in str(row.get('answer_text', '')).lower():
        return True

    # Search in why list
    why_list = row.get('why', [])
    if isinstance(why_list, list):
        for item in why_list:
            if search_term in str(item).lower():
                return True

    # Search in findings
    findings_list = row.get('findings', [])
    if isinstance(findings_list, list):
        for item in findings_list:
            if search_term in str(item).lower():
                return True

    # Search in others
    others_list = row.get('others', [])
    if isinstance(others_list, list):
        for other in others_list:
            if isinstance(other, dict):
                text = str(other.get('text', ''))
                reason = str(other.get('reason', ''))
                if search_term in text.lower() or search_term in reason.lower():
                    return True

    return False
