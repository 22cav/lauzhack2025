import os
import speech_recognition as sr
import requests
import json
import random
import time
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw
import playsound
from gtts import gTTS

# --- CONFIGURATION ---
load_dotenv()

# API Configuration
API_ENDPOINT = os.environ.get("API_ENDPOINT")
API_KEY = os.environ.get("LLM_API_KEY")
MODEL_NAME = os.environ.get("MODEL_NAME")


BASE_PATH = "/Users/matti/Documents/hackaton/ExamplePlugin/src/Actions/scripts"
TRACKING_FILE = os.path.join(BASE_PATH, "last_created.txt")
AUDIO_BASE_PATH = "percorso/alla/tua/cartella/audio"

# Ensure directory exists
if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

def announce_feedback(text):
    tts = gTTS(text=text, lang='it')
    temp_file = "temp_feedback.mp3"

    try:
        tts.save(temp_file)
        playsound.playsound(temp_file)
    except Exception as e:
        print(f"Errore TTS/Riproduzione: {e}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def play_feedback(status):
    """It starts an audio file, based on status."""

    if status == "success":
        audio_file = os.path.join(AUDIO_BASE_PATH, "audio_registrato.wav")
    elif status == "no_microphone":
        audio_file = os.path.join(AUDIO_BASE_PATH, "errore_generico.wav")
    elif status == "start":
        audio_file = os.path.join(AUDIO_BASE_PATH, "errore_generico.wav")
    elif status == "stop_listening":
        audio_file = os.path.join(AUDIO_BASE_PATH, "errore_generico.wav")
    elif status == "no_talking":
        audio_file = os.path.join(AUDIO_BASE_PATH, "errore_generico.wav")
    elif status == "no_understand":
        audio_file = os.path.join(AUDIO_BASE_PATH, "errore_generico.wav")
    elif status == "unavailable":
        audio_file = os.path.join(AUDIO_BASE_PATH, "errore_generico.wav")
    else:
        return

    try:
        # playsound blocks execution until the audio finishes
        playsound.playsound(audio_file)
    except Exception as e:
        print(f"Errore riproduzione audio: {e}")

def button_color(color):
    """
    Updates the status icon file to communicate state.
    Colors: red, yellow, green
    """
    status_icon_path = os.path.join(BASE_PATH, "status_icon.png") # it has to be the same icon as the default one
    
    colors = {
        "red": (255, 0, 0),
        "yellow": (255, 255, 0),
        "green": (0, 255, 0),
        "reset": (0, 0, 0)
    }
    
    rgb = colors.get(color, (0, 0, 0))
    
    try:
        img = Image.new('RGB', (80, 80), color=rgb)
        img.save(status_icon_path)
    except Exception as e:
        print(f"Error updating status icon: {e}")
        
    if color in ["red", "green"]:
        time.sleep(2)
        button_color("reset")




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
            button_color("yellow")
            r.adjust_for_ambient_noise(source, duration=1)
            play_feedback("start")
            button_color("green")
            print(f"Listening... (Will stop after {r.pause_threshold}s of silence)")
            play_feedback("stop_listening")
            
            try:
                audio = r.listen(source, timeout=10)
            except sr.WaitTimeoutError:
                print("Timeout: No speech detected.")
                play_feedback("no_talking")
                return None
    except OSError as e:
        print(f"Error accessing microphone: {e}")
        play_feedback("no_microphone")
        return None

    try:
        button_color("yellow")
        print("Recognizing...")
        text = r.recognize_google(audio, language="en-US") 
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
        play_feedback("no_understand")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        play_feedback("unavailable")
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
        if cmd_name and code:
            audio_prompt = (
                "You are a concise assistant tasked with creating audio feedback for a user. "
                "You will receive a block of **Blender Python code** that was just generated and saved. "
                "Your goal is to summarize the action performed by the code into a short, positive, and confirming sentence. "
                "The output must be strictly a JSON object.\n\n"
                
                "STRICT RULES:\n"
                "1. MAX LENGTH: The feedback sentence must be **maximum 15 words** long.\n"
                "2. TONE: The sentence must be confirming and professional (e.g., 'The script will create a cube and scale it along the Z-axis.').\n"
                "3. CONTEXT: Base the feedback **EXCLUSIVELY** on the received Python code.\n"
                "4. OUTPUT FORMAT: Return ONLY the JSON object described below.\n\n"
                
                "JSON Structure:\n"
                "{\n"
                '  "feedback": "Your short confirming sentence describing the code.",\n'
                "}"
            )
            audio_payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": audio_prompt},
                    {"role": "user", "content": code}
                ],
                "temperature": 0.2
            }
            response = requests.post(API_ENDPOINT, headers=headers, json=audio_payload)
            response.raise_for_status()
            
            result_json = response.json()
            content = result_json['choices'][0]['message']['content']

            # Clean up markdown
            clean_content = content.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(clean_content)
            feedback = data.get("feedback", "Button created") 
            announce_feedback(feedback)

        return cmd_name, code

    except Exception as e:
        print(f"LLM Interaction Error: {e}")
        play_feedback("unavailable")
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
        play_feedback("unavailable")
        return False

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
        return False
    
    button_color("green")
    return True

def main():
    print("--- Voice to C# Plugin Action Generator ---")
    
    text = listen_to_microphone()
    if not text:
        button_color("red")
        return

    print("\nGenerating immediate execution script...")
    cmd_name, code = from_transcription_to_data(text)
    
    if cmd_name and code:
        if not save_action_files(cmd_name, code):
            button_color("red")
            print("Error during saving action files.")
            return
    else:
        button_color("red")
        print("Failed to generate valid code or name from LLM.")

if __name__ == "__main__":
    main()