# Exam Solution Audit Dashboard

A streamlined Streamlit application for reviewing AI-generated exam solutions in JSON format.

## Features

- **📁 Data Source Selection**: Choose from predefined data files or upload custom JSON files
- **🔎 Question Navigator**: Browse questions with Previous/Next buttons, arrow key navigation, and direct question number input
- **📋 Detail View**: Comprehensive question display with answer, reasoning (Why), findings, and distractors
- **⚠️ Mismatch Detection**: Automatically displays first guess and rethink notes when decisions changed
- **🎯 Compact Display**: Optimized layout with reduced spacing for efficient review

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your data files**:
   - Place JSON files in the `./data` directory
   - Default files: `2022_1.json`, `2022_2.json`, `2023_1.json`, `2023_2.json`

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Access the dashboard**:
   - The app will automatically open in your browser
   - Default URL: `http://localhost:8501`

## Usage

### Loading Data

The app provides three ways to load data:

**Option 1: Select from dropdown (Default)**
1. Open the sidebar
2. Choose a file from the "Select data file" dropdown
3. The first file loads automatically on startup

**Option 2: Upload a file**
1. Click "Or upload JSON file" in the sidebar
2. Select your JSON file
3. Click "🔄 Load Data"

**Option 3: Enter file path**
1. Enter the file path in "Or enter file path"
2. Or set the `EXAM_JSON_PATH` environment variable
3. Click "🔄 Load Data"

### Navigation

**Previous/Next Buttons**:
- Click "← Previous" or "Next →" to move between questions

**Keyboard Shortcuts**:
- Arrow Left/Up: Previous question
- Arrow Right/Down: Next question

**Jump to Question**:
- Use the number input field in the navigation bar
- Type a question number to jump directly to it

### Understanding the Display

Each question shows:

1. **Header**: Question number, decision icon, final decision, and confidence percentage
   - 🟢 Agree with key (no mismatch)
   - 🟠 Agree with key (after mismatch/rethink)
   - 🔴 Override key
   - ⚪ No decision

2. **Answer Section**: Selected answer with label and text
   - Key: Shows provided answer key if available
   - Runner-up: Shows second-best option if present

3. **💡 Why**: Reasoning for the selected answer (concatenated)

4. **🔍 Findings**: Additional observations or notes (if available)

5. **❌ Distractors**: Other answer options with rejection reasons

6. **⚠️ Mismatch** (bottom): Shows first guess and rethink note when the decision changed

### JSON Schema

The application expects JSON files with the following structure:

```json
{
  "doc": {
    "source": "exam_name.pdf",
    "pages_parsed": 10,
    "has_global_answer_key": true
  },
  "defaults": {
    "depth": "shallow"
  },
  "questions": [
    {
      "question_no": "1",
      "depth": "deep",
      "answer": {
        "label": "3",
        "text": "Answer text"
      },
      "why": ["Reason 1", "Reason 2"],
      "others": [
        {
          "label": "1",
          "text": "Option text",
          "reason": "Rejection reason"
        }
      ],
      "findings": ["Finding 1", "Finding 2"],
      "runner_up": "2",
      "flags": {
        "illegible": false,
        "mixed_lang": false
      },
      "confidence": 0.95,
      "rethink": {
        "mismatch": false,
        "first_guess": "3",
        "provided_key": {"label": "3"},
        "final_decision": "agree_with_key",
        "override_key": false,
        "note": "Rethink explanation text"
      },
      "metadata": {
        "input_metadata": {"has_images": true},
        "version": "1.0"
      }
    }
  ]
}
```

## Project Structure

```
.
├── app.py              # Main Streamlit application with navigation
├── data/               # Directory for JSON data files
│   ├── 2022_1.json
│   ├── 2022_2.json
│   ├── 2023_1.json
│   └── 2023_2.json
├── data_loader.py      # JSON loading and normalization
├── detail_view.py      # Question detail view rendering
├── sidebar.py          # Sidebar filters and controls (if present)
├── kpis.py            # KPI summary rendering (if present)
├── table_view.py      # Table view utilities
├── analytics.py       # Analytics charts (if present)
├── exporters.py       # Export functionality (if present)
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Configuration

### Environment Variables

- `EXAM_JSON_PATH`: Default path to JSON file (optional)

### Display Customization

The detail view automatically:
- Concatenates "Why" reasons into a single paragraph
- Uses compact spacing for findings (reduced vertical spacing)
- Shows mismatch information only when relevant
- Formats confidence as whole percentages

## Troubleshooting

### Schema Validation Errors

If you see "Invalid JSON schema" errors:
1. Ensure your JSON has a `questions` array
2. Each question must have `question_no` and `answer` fields
3. Check the example schema above

### No Files Found

If the dropdown shows "No files found":
1. Create a `./data` directory in the project root
2. Add JSON files to the directory
3. Restart the application

### Navigation Issues

If keyboard navigation doesn't work:
1. Make sure you're not typing in an input field
2. Click outside input fields to deactivate them
3. Try refreshing the browser

## License

This project is provided as-is for educational and commercial use.
