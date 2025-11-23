import subprocess
import platform
import os
import logging
import time
import shutil
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_default_blender_path() -> Optional[str]:
    """
    Get default Blender path. 
    Prioritizes 'Blender' (Capital B) in PATH, then 'blender', then hardcoded paths.
    """
    
    # 1. Check if "Blender" (Capital B) is in PATH (User specified requirement)
    if shutil.which("Blender"):
        return "Blender"
    
    # 2. Check if "blender" (lowercase) is in PATH (Standard convention)
    if shutil.which("blender"):
        return "blender"

    # 3. Fallback to hardcoded paths if not found in PATH
    system = platform.system()
    
    if system == "Darwin":  # macOS
        paths = [
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "/Applications/Blender 4.3.app/Contents/MacOS/Blender",
            "/Applications/Blender 4.2.app/Contents/MacOS/Blender",
            "/Applications/Blender 4.1.app/Contents/MacOS/Blender",
            "/Applications/Blender 4.0.app/Contents/MacOS/Blender",
            "/Applications/Blender 3.6.app/Contents/MacOS/Blender"
        ]
        for path in paths:
            if os.path.exists(path):
                return path
                
    elif system == "Windows":
        paths = [
            r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
        ]
        for path in paths:
            if os.path.exists(path):
                return path

    return None

def launch_blender(config: Dict[str, Any]) -> Optional[subprocess.Popen]:
    """
    Launch Blender application with error capturing.
    """
    blender_command = config.get('blender_path')
    
    if not blender_command:
        blender_command = get_default_blender_path()

    # --- VALIDATION FIX ---
    # We use shutil.which() to validate. 
    # This works for both absolute paths ("/bin/blender") AND commands ("Blender")
    executable_path = shutil.which(blender_command) if blender_command else None

    if not executable_path:
        logger.error(f"❌ Blender executable not found. Searched for: '{blender_command}'")
        return None
        
    # We log the resolved path so you know exactly which file is running
    logger.info(f"🚀 Launching Blender command: '{blender_command}'")
    logger.info(f"   (Resolved executable: {executable_path})")
    
    try:
        process = subprocess.Popen(
            [blender_command], # We use the original command string
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment to ensure it doesn't crash immediately
        time.sleep(2) 
        
        return_code = process.poll()
        
        if return_code is not None:
            logger.error(f"❌ Blender crashed immediately with return code: {return_code}")
            stdout_out, stderr_out = process.communicate()
            if stdout_out: logger.error(f"--- STDOUT ---\n{stdout_out}")
            if stderr_out: logger.error(f"--- STDERR ---\n{stderr_out}")
            return None
        
        logger.info("✓ Blender launched successfully and is running.")
        return process
        
    except PermissionError:
        logger.error(f"❌ Permission denied when trying to execute: {blender_command}")
    except OSError as e:
        logger.error(f"❌ OS Error occurred: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        
    return None

if __name__ == "__main__":
    # If you leave this as None, it will auto-detect "Blender" from PATH
    config = {"blender_path": None} 
    
    proc = launch_blender(config)
    
    if proc:
        logger.info(f"Process PID: {proc.pid}")
        try:
            # Keep main thread alive to let Blender run
            proc.wait()
        except KeyboardInterrupt:
            logger.info("Stopping Blender...")
            proc.terminate()