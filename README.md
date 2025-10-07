# Exam Solution Audit Dashboard

A streamlined Streamlit application for reviewing AI-generated exam solutions in JSON format.

## Features

- **📁 Auto-load Data**: Automatically loads JSON files from `./data` directory on startup
- **📤 Multiple File Upload**: Upload additional JSON files and switch between them easily
- **🔎 Question Navigator**: Browse questions with Previous/Next buttons, arrow key navigation, and direct question number input
- **📋 Detail View**: Comprehensive question display with answer, reasoning (Why), findings, and distractors
- **⚠️ Mismatch Detection**: Automatically displays first guess and rethink notes when decisions changed
- **🎯 Streamlined Interface**: Clean, focused interface for efficient exam solution review

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

3. **Add your data files** (optional):
   - Place JSON files in the `./data` directory
   - Example files: `2022_1.json`, `2022_2.json`, `2023_1.json`, `2023_2.json`
   - Files are loaded automatically on startup

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Access the dashboard**:
   - The app will automatically open in your browser
   - Default URL: `http://localhost:8501`

## Usage

### Loading Data

**Default Files:**
- The app automatically loads all JSON files from the `./data` directory on startup
- Files appear in the "Select file to view" dropdown in alphabetical order
- No action needed if your data is in the `./data` directory

**Upload Additional Files:**
1. Open the sidebar (if collapsed)
2. Click "Browse files" under "Upload JSON file(s)"
3. Select one or more JSON files
4. Uploaded files are added to the selection dropdown

**Switch Between Files:**
1. Use the "Select file to view" dropdown in the sidebar
2. Files are listed in alphabetical order
3. Switching files resets navigation to question 1

**Remove Uploaded Files:**
- Click the "×" next to a file in the uploader to remove it
- Removed files disappear from the selection dropdown
- Default files from `./data` directory cannot be removed via uploader

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

**File Indicator:**
- The current file name is shown at the top of the page

**Each Question Shows:**

1. **Header**: Question number, decision icon, final decision, and confidence percentage
   - 🟢 Agree with key (no mismatch)
   - 🟠 Agree with key (after mismatch/rethink)
   - 🔴 Override key
   - ⚪ No decision

2. **Answer Section**: Selected answer with label and text
   - **Key**: Shows provided answer key if available
   - **Runner-up**: Shows second-best option if present

3. **💡 Why**: Reasoning for the selected answer

4. **🔍 Findings**: Additional observations or notes (appears between Why and Distractors)

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
├── data/               # Directory for default JSON data files
│   ├── 2022_1.json     # (Example - add your files here)
│   ├── 2022_2.json
│   ├── 2023_1.json
│   └── 2023_2.json
├── data_loader.py      # JSON loading and normalization
├── detail_view.py      # Question detail view rendering
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

## Key Features

### Streamlined Design

The application focuses on efficient exam solution review with:
- **Simple file management**: Upload multiple files and switch between them
- **Clean detail view**: No clutter, just the essential information
- **Smart layout**: Findings positioned between Why and Distractors for logical flow
- **Compact formatting**: Reduced vertical spacing for faster reading
- **Automatic mismatch detection**: Highlights when AI changed its decision

## Troubleshooting

### Schema Validation Errors

If you see "Invalid JSON schema" errors:
1. Ensure your JSON has a `questions` array
2. Each question must have `question_no` and `answer` fields
3. Check the example schema above

### No Files Loaded

If you see "Please upload JSON file(s) to get started":
1. Check if the `./data` directory exists and contains JSON files
2. If not, create the directory and add your JSON files
3. Or click "Browse files" in the sidebar to upload files manually
4. Restart the application if you added files to `./data`

### Navigation Issues

If keyboard navigation doesn't work:
1. Make sure you're not typing in an input field
2. Click outside input fields to deactivate them
3. Try refreshing the browser

## License

This project is provided as-is for educational and commercial use.
