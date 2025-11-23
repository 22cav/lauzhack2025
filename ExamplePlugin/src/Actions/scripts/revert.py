import os
import sys
import glob

# Configuration
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(BASE_PATH, "last_created.txt")

def revert_last_action():
    print("Cancelling all generated script, JSON, and icon files...")

    # Patterns for files to delete
    file_patterns = [
        os.path.join(BASE_PATH, "script_*.py"),
        os.path.join(BASE_PATH, "script_*.json"),
        os.path.join(BASE_PATH, "icon_*.png")
    ]

    deleted_any = False
    for pattern in file_patterns:
        for file_path in glob.glob(pattern):
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted: {os.path.basename(file_path)}")
                    deleted_any = True
                except Exception as e:
                    print(f"Error deleting {os.path.basename(file_path)}: {e}")
            else:
                print(f"File not found (skipping): {os.path.basename(file_path)}")

    if not deleted_any:
        print("No generated files found to cancel.")
    
    # Remove the tracking file as all actions are cancelled
    if os.path.exists(TRACKING_FILE):
        try:
            with open(TRACKING_FILE, "w") as f:
                f.write("0")
            print(f"Tracking file reset to 0: {os.path.basename(TRACKING_FILE)}")
        except Exception as e:
            print(f"Error deleting tracking file: {e}")

    # Execute build and kill command
    print("Rebuilding and restarting Loupedeck...")
    os.system("cd /Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin && dotnet build && pkill -f Loupedeck")

if __name__ == "__main__":
    revert_last_action()
