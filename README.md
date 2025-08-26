# Dynamic Streamlit UI with Gemini (main.py)

This project demonstrates a dynamic Streamlit app that adapts its UI in real time based on natural language feedback, using Google Gemini for structured interpretation.

## Features
- Change button color, label, and visibility
- Change title text and color
- Change background color
- Show/hide and update a text area
- Show/hide and set value of a slider
- Supports multiple UI changes in a single feedback (e.g., "make the button red and change the title to Hello")

## Setup Instructions

### 1. Clone the repository (if needed)
```
git clone <your-repo-url>
cd <your-project-folder>
```

### 2. Create and activate a virtual environment
**Windows (PowerShell):**
```
python -m venv VLM
.\VLM\Scripts\Activate.ps1
```
**Windows (cmd):**
```
python -m venv VLM
VLM\Scripts\activate.bat
```
**Linux/macOS:**
```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install requirements
```
pip install -r requirements.txt
```

### 4. Set up your Gemini API key
You can either:
- Set the environment variable `GEMINI_API_KEY` before running the app, or
- Enter your API key in the Streamlit sidebar when prompted.

### 5. Run the Streamlit app
```
streamlit run main.py
```

## Usage
- Enter your Gemini API key in the sidebar (if not set as an environment variable).
- Type natural language UI commands in the main text area (e.g., "change button color to green and set title to Welcome!").
- Click **Apply Feedback**.
- The UI will update according to your instructions, and the Gemini JSON output will be shown for transparency.

## Example Feedback
- `change the button color to red and hide the text area`
- `set the slider to 80 and change the title label to Dashboard`
- `make the background color black and show the button`

## Function Descriptions

### get_gemini_ui_response(user_feedback: str, api_key: str)
Sends the user's natural language feedback to the Gemini API and requests a structured JSON list of UI instructions.
- Defines a Pydantic model for the expected instruction format.
- Calls Gemini with the user feedback and a prompt to return a list of objects, each with `component`, `property`, and `value`.
- Parses and returns the list of instructions, or the raw response if parsing fails.

### normalize_component(comp: str) -> str
Normalizes the component name from the Gemini output to a canonical form, making the app robust to synonyms, plurals, and typos.
- Converts the input to lowercase.
- Uses regex to match common variants (e.g., "button", "btn", "buttons" → "button").
- Returns the canonical component name (e.g., "button", "title", "background", "text_area", "slider").

### normalize_property(prop: str) -> str
Normalizes the property name from the Gemini output to a canonical form, handling synonyms and typos.
- Converts the input to lowercase.
- Uses regex to match common variants (e.g., "color", "colour", "background color" → "color").
- Returns the canonical property name (e.g., "text", "color", "content", "visibility", "value").

### apply_ui_instruction(instruction: dict, rerun: bool = False)
Applies a single UI instruction to the Streamlit session state, updating the UI accordingly.
- Normalizes the `component` and `property` fields using the above functions.
- Maps the instruction to a session state key (e.g., "button_color", "title_text").
- Updates the value in `st.session_state`.
- If `rerun=True` (used for the last instruction in a batch), sets a flag and calls `st.rerun()` to update the UI.

### main()
The main entry point for the Streamlit app. Handles UI rendering, user input, and feedback processing.
- Sets up the Streamlit page and initializes all session state variables with defaults if not already set.
- Renders the UI (title, button, text area, slider) based on the current session state.
- Provides a sidebar for entering the Gemini API key and a text area for user feedback.
- When the user clicks **Apply Feedback**:
  - Calls `get_gemini_ui_response` to get a list of instructions from Gemini.
  - Displays the raw Gemini JSON output.
  - Applies each instruction using `apply_ui_instruction`, only rerunning after the last instruction so all changes appear at once.
- Shows a success message if the UI was updated.

## Visual Workflow

```mermaid
flowchart TD
    A[User Input (feedback)] --> B[get_gemini_ui_response (Gemini API call)]
    B --> C[Gemini JSON Output (list of instructions)]
    C --> D{For each instruction}
    D --> E[normalize_component and normalize_property]
    E --> F[Update session state]
    F --> G{Last instruction?}
    G -- No --> D
    G -- Yes --> H[st.rerun()]
    H --> I[UI re-renders from session state]
```

---
Built with ❤️ using Streamlit and Google Gemini
