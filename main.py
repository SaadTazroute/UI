import streamlit as st
import os
from google import genai
from pydantic import BaseModel
import re

def get_gemini_ui_response(user_feedback: str, api_key: str):
    class UIInstruction(BaseModel):
        component: str
        property: str
        value: object = None
    class UIInstructions(BaseModel):
        instructions: list[UIInstruction]
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Interpret this user feedback for a Streamlit UI: '{user_feedback}'. Respond as a JSON list of objects, each with fields: component, property, value. Example: [{{'component': 'button', 'property': 'color', 'value': 'red'}}, ...]",
        config={
            "response_mime_type": "application/json",
            "response_schema": list[UIInstruction],
        },
    )
    # Always return a list of instructions
    if hasattr(response, 'parsed'):
        if isinstance(response.parsed, list):
            return [i.dict() for i in response.parsed]
        elif hasattr(response.parsed, 'instructions'):
            return [i.dict() for i in response.parsed.instructions]
    # fallback: try to parse as list
    try:
        parsed = response.text
        if isinstance(parsed, str):
            import json
            parsed = json.loads(parsed)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    return [response.text]

def normalize_component(comp):
    comp = comp.lower()
    if re.search(r"button|btn", comp):
        return "button"
    if re.search(r"title|header", comp):
        return "title"
    if re.search(r"background|app", comp):
        return "background"
    if re.search(r"text[_ ]?area|textarea", comp):
        return "text_area"
    if re.search(r"slider", comp):
        return "slider"

    return comp

def normalize_property(prop):
    prop = prop.lower()
    if re.search(r"label|text|name", prop):
        return "text"
    if re.search(r"color|colour|background[_ ]?color", prop):
        return "color"
    if re.search(r"content", prop):
        return "content"
    if re.search(r"visible|visibility|show|hide", prop):
        return "visibility"
    if re.search(r"value", prop):
        return "value"
    return prop

def apply_ui_instruction(instruction, rerun=False):
    print("Applying instruction:", instruction)
    print("Normalized component:", normalize_component(str(instruction.get("component", ""))))
    print("Normalized property:", normalize_property(str(instruction.get("property", ""))))
    print("Value:", instruction.get("value"))
    
    comp = normalize_component(str(instruction.get("component", "")))
    prop = normalize_property(str(instruction.get("property", "")))
    value = instruction.get("value")
    updated = False
    print(f"Component: {comp}, Property: {prop}, Value: {value}")
    key = None
    if comp == "button" and prop == "color":
        key = "button_color"
    elif comp == "button" and prop == "text":
        key = "button_label"
    elif comp == "button" and prop == "visibility":
        key = "button_visible"
        value = bool(value)
    elif comp == "title" and prop == "text":
        key = "title_text"
    elif comp == "title" and prop == "color":
        key = "title_color"
    elif comp == "background" and prop == "color":
        key = "background_color"
    elif comp == "text_area" and prop == "content":
        key = "text_area_content"
    elif comp == "text_area" and prop == "visibility":
        key = "text_area_visible"
        value = bool(value)
    elif comp == "slider" and prop == "value":
        key = "slider_value"
        value = int(value)
    elif comp == "slider" and prop == "visibility":
        key = "slider_visible"
        value = bool(value)
    # Add more as needed
    if key:
        st.session_state[key] = value
        updated = True
    if updated and rerun:
        st.session_state["_show_success"] = True
        st.rerun()

def main():
    st.set_page_config(layout="centered", page_title="Gemini UI Demo")
    # Defaults
    if "button_color" not in st.session_state:
        st.session_state["button_color"] = "blue"
    if "button_label" not in st.session_state:
        st.session_state["button_label"] = "Click Me!"
    if "button_visible" not in st.session_state:
        st.session_state["button_visible"] = True
    if "title_text" not in st.session_state:
        st.session_state["title_text"] = "Dynamic UI with Gemini 🤖"
    if "title_color" not in st.session_state:
        st.session_state["title_color"] = "#262730"
    if "background_color" not in st.session_state:
        st.session_state["background_color"] = "#f0f2f6"
    if "text_area_content" not in st.session_state:
        st.session_state["text_area_content"] = "This is a dynamic text area."
    if "text_area_visible" not in st.session_state:
        st.session_state["text_area_visible"] = True
    if "slider_value" not in st.session_state:
        st.session_state["slider_value"] = 50
    if "slider_visible" not in st.session_state:
        st.session_state["slider_visible"] = True
    if "_show_success" in st.session_state and st.session_state["_show_success"]:
        st.success("UI updated!")
        st.session_state["_show_success"] = False

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state['background_color']}; }}
        </style>
    """, unsafe_allow_html=True)
    st.markdown(f"<h1 style='color: {st.session_state['title_color']};'>{st.session_state['title_text']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<style>.stButton > button {{background-color: {st.session_state['button_color']}; color: white;}}</style>", unsafe_allow_html=True)
    if st.session_state["button_visible"]:
        st.button(st.session_state["button_label"])
    if st.session_state["text_area_visible"]:
        st.text_area("Dynamic Text Area", value=st.session_state["text_area_content"], key="main_text_area", height=100)
    if st.session_state["slider_visible"]:
        st.slider("Adjust Value", min_value=0, max_value=100, value=st.session_state["slider_value"], key="main_slider")

    st.divider()
    api_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    user_feedback = st.text_area("Enter UI command:")
    if st.button("Apply Feedback"):
        if not api_key:
            st.warning("Please enter your Gemini API key.")
        elif user_feedback:
            instructions = get_gemini_ui_response(user_feedback, api_key)
            st.subheader("Gemini JSON Output:")
            st.json(instructions)
            updated = False
            if isinstance(instructions, list):
                for idx, instruction in enumerate(instructions):
                    if isinstance(instruction, dict):
                        # Only rerun after the last instruction
                        apply_ui_instruction(instruction, rerun=(idx == len(instructions)-1))

if __name__ == "__main__":
    main()
