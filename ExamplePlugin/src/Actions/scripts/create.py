import os
import speech_recognition as sr
import requests
import json
import random
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw

# --- CONFIGURATION ---
load_dotenv()

# API Configuration
API_ENDPOINT = os.environ.get("API_ENDPOINT")
API_KEY = os.environ.get("LLM_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME")


BASE_PATH = "/Users/matti/Documents/hackaton/ExamplePlugin/src/Actions/scripts"
TRACKING_FILE = os.path.join(BASE_PATH, "last_created.txt")

# Ensure directory exists
if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

def listen_to_microphone():
    """
    Listens to the microphone and returns the recognized text.
    Stops only after 2 seconds of silence.
    """
    r = sr.Recognizer()
    r.pause_threshold = 2.0 
    r.non_speaking_duration = 0.5 

    try:
        with sr.Microphone() as source:
            print("Calibrating for ambient noise... please wait.")
            r.adjust_for_ambient_noise(source, duration=1)
            print(f"Listening... (Will stop after {r.pause_threshold}s of silence)")
            
            try:
                audio = r.listen(source, timeout=10)
            except sr.WaitTimeoutError:
                print("Timeout: No speech detected.")
                return None
    except OSError as e:
        print(f"Error accessing microphone: {e}")
        return None

    try:
        print("Recognizing...")
        text = r.recognize_google(audio, language="en-US") 
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        return None

def from_transcription_to_data(transcription):
    """
    Sends the transcription to the LLM and returns:
    - Command Name
    - Python Code
    """
    system_prompt = (
        "You are a Python Script Generator for Blender. "
        "The user wants a script that performs an action IMMEDIATELY when executed. "
        "Do NOT create an Add-on. Do NOT create a Tool.\n\n"
        
        "STRICT RULES:\n"
        "1. NO CLASSES: Do not define 'class Operator(bpy.types.Operator)'.\n"
        "2. NO REGISTRATION: Do not use 'bpy.utils.register_class' or 'register()'.\n"
        "3. NO KEYMAPS: Do not try to assign hotkeys using 'wm.keyconfigs'.\n"
        "4. IMMEDIATE EXECUTION: Write procedural code that runs top-to-bottom (e.g., 'bpy.ops.mesh.primitive_cube_add()', 'print(\"Hello\")').\n"
        "5. FLEXIBILITY: Use 'bpy' only if interacting with Blender internals. Use standard Python libraries (os, sys, math, etc.) if the task is generic.\n"
        "6. OUTPUT FORMAT: Return ONLY the JSON object described below.\n\n"
        
        "JSON Structure:\n"
        "{\n"
        '  "command_name": "One Word Action Name",\n'
        '  "python_code": "The raw procedural python code...",\n'
        "}"
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcription}
        ],
        "temperature": 0.2
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    try:
        print(f"Sending request to {MODEL_NAME}...")
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        
        result_json = response.json()
        content = result_json['choices'][0]['message']['content']

        # Clean up markdown
        clean_content = content.replace("```json", "").replace("```", "").strip()
        
        data = json.loads(clean_content)
        cmd_name = data.get("command_name", "unnamed_action")
        code = data.get("python_code", "")

        return cmd_name, code

    except Exception as e:
        print(f"LLM Interaction Error: {e}")
        return None, None

def get_next_sequence_id():
    """
    Reads the last created ID from text file, increments it, 
    saves the new ID, and returns it.
    """
    current_id = 0
    
    # Read last ID
    if os.path.exists(TRACKING_FILE):
        try:
            with open(TRACKING_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    current_id = int(content)
        except ValueError:
            print("Warning: Could not parse tracking file. Resetting to 0.")
    
    next_id = current_id + 1
    
    with open(TRACKING_FILE, "w") as f:
        f.write(str(next_id))
        
    return next_id

def generate_random_icon(icon_path):
    """
    Generates a random color 80x80 icon and saves it.
    """
    r = random.randint(20, 255)
    g = random.randint(20, 255)
    b = random.randint(20, 255)
    
    # Create image
    img = Image.new('RGB', (80, 80), color=(r, g, b))
    d = ImageDraw.Draw(img)

    # Add visual detail (white circle)
    d.ellipse([(20, 20), (60, 60)], outline="white", width=3)

    img.save(icon_path)
    return f"#{r:02x}{g:02x}{b:02x}"

def save_action_files(cmd_name, code):
    """
    Orchestrates the saving of the Python script, the Icon, and the JSON metadata
    using the incremental ID logic.
    """
    # 1. Get unique ID
    seq_id = get_next_sequence_id()
    
    # 2. Define Filenames
    script_filename = f"script_{seq_id}.py"
    json_filename = f"script_{seq_id}.json"
    icon_filename = f"icon_{seq_id}.png" # Unique icon per script
    
    script_path = os.path.join(BASE_PATH, script_filename)
    json_path = os.path.join(BASE_PATH, json_filename)
    icon_path = os.path.join(BASE_PATH, icon_filename)

    print(f"\nProcessing ID: {seq_id}...")

    # 3. Generate and Save Icon
    color_hex = generate_random_icon(icon_path)
    print(f"🎨 Icon generated: {color_hex} -> {icon_filename}")

    # 4. Save Python Script
    full_code_content = (
        f"# Action Name: {cmd_name}\n"
        f"# Generated via Voice Command\n"
        f"# ---------------------------\n"
        f"{code}\n"
    )
    
    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(full_code_content)
        print(f"📜 Script saved: {script_filename}")
    except Exception as e:
        print(f"Error saving script: {e}")
        return

    # 5. Save JSON Metadata
    # The C# plugin likely watches this file to trigger the update
    metadata = {
        "Title": cmd_name,
        "IconPath": icon_path
    }

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        print(f"✅ Metadata saved: {json_filename}")
    except Exception as e:
        print(f"Error saving metadata: {e}")

def main():
    print("--- Voice to C# Plugin Action Generator ---")
    
    text = listen_to_microphone()
    if not text:
        return

    print("\nGenerating immediate execution script...")
    cmd_name, code = from_transcription_to_data(text)
    
    if cmd_name and code:
        save_action_files(cmd_name, code)
    else:
        print("Failed to generate valid code or name from LLM.")

if __name__ == "__main__":
    main()