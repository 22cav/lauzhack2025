import os
import sys

# Configuration
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
TRACKING_FILE = os.path.join(BASE_PATH, "last_created.txt")

def get_last_id():
    if os.path.exists(TRACKING_FILE):
        try:
            with open(TRACKING_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return int(content)
        except ValueError:
            pass
    return None

def update_last_id(new_id):
    with open(TRACKING_FILE, "w") as f:
        f.write(str(new_id))

def revert_last_action():
    last_id = get_last_id()
    
    if last_id is None or last_id < 1:
        print("No actions to revert or invalid tracking file.")
        return

    print(f"Reverting action ID: {last_id}")

    # Files to delete
    files_to_delete = [
        os.path.join(BASE_PATH, f"script_{last_id}.py"),
        os.path.join(BASE_PATH, f"script_{last_id}.json"),
        os.path.join(BASE_PATH, f"icon_{last_id}.png")
    ]

    deleted_any = False
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {os.path.basename(file_path)}")
                deleted_any = True
            except Exception as e:
                print(f"Error deleting {os.path.basename(file_path)}: {e}")
        else:
            print(f"File not found (skipping): {os.path.basename(file_path)}")

    # Decrement ID regardless of whether files were found, 
    # to ensure we don't get stuck on a "ghost" ID.
    # But only if we are sure we want to go back. 
    # If nothing was deleted, maybe we shouldn't? 
    # The user asked to "cancel" them. If they are already gone, we should probably just decrement.
    
    new_id = last_id - 1
    update_last_id(new_id)
    print(f"Tracking file updated to ID: {new_id}")
    
    # Execute build and kill command
    print("Rebuilding and restarting Loupedeck...")
    os.system("cd /Users/matti/Documents/hackaton/lauzhack2025/ExamplePlugin && dotnet build && pkill -f Loupedeck")

if __name__ == "__main__":
    revert_last_action()
