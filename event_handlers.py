import threading
from PIL import ImageGrab
import base64
from io import BytesIO
import time

def setup_window_controls(root):

    def toggle_visibility(event=None):
        current_alpha = root.attributes('-alpha')
        if current_alpha > 0:
            root.attributes('-alpha', 0.0)
        else:
            root.attributes('-alpha', 0.7)

    # Bind events
    root.bind('<Control-Shift-KeyPress-H>', toggle_visibility)

def setup_screenshot_controls(root, speech):
    def capture_and_process_screenshot(event=None):
        try:
            # Temporarily make window transparent during screenshot
            current_alpha = root.attributes('-alpha')
            root.attributes('-alpha', 0.0)
            root.update()
            
            # Small delay to ensure window transparency
            time.sleep(0.1)
            
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Restore window visibility
            root.attributes('-alpha', current_alpha)
            
            # Save screenshot
            # filename = f"screenshot_{int(time.time())}.png"
            # screenshot.save(filename)
            
            # Convert to base64
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Process screenshot asynchronously
            speech.process_screenshot(img_str)
            
        except Exception as e:
            speech.update_text(f"[INFO]Screenshot error: {str(e)}")
            root.attributes('-alpha', current_alpha)
    
    # Bind screenshot to Ctrl+Shift+S
    root.bind('<Control-Shift-KeyPress-S>', capture_and_process_screenshot)
    
    def debug_screenshot(event=None):
        try:
            # Temporarily make window transparent during screenshot
            current_alpha = root.attributes('-alpha')
            root.attributes('-alpha', 0.0)
            root.update()
            
            # Small delay to ensure window transparency
            time.sleep(0.1)
            
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Restore window visibility
            root.attributes('-alpha', current_alpha)
            
            # Save screenshot
            # filename = f"screenshot_{int(time.time())}.png"
            # screenshot.save(filename)
            
            # Convert to base64
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Process screenshot asynchronously
            speech.debug_screenshot(img_str)
            
        except Exception as e:
            speech.update_text(f"[INFO]Screenshot error: {str(e)}")
            root.attributes('-alpha', current_alpha)
    
    # Bind screenshot to Ctrl+Shift+D
    root.bind('<Control-Shift-KeyPress-D>', debug_screenshot)

def setup_recording_controls(root, speech, update_info_label):

    def toggle_audio_recording(event):
        if speech.is_audio_recording:
            speech.is_audio_recording = False
            # Add this line to ensure clean stop
            speech.stop_recording.set()
            speech.update_text("[INFO] Recording stopped")
        else:
            speech.stop_recording.clear()  # Reset the stop flag
            speech.is_audio_recording = True
            threading.Thread(target=speech.continuous_audio_recording).start()
            speech.update_text("[REC] Continuous recording started - Press 'A' to stop")

    # Bind recording controls
    root.bind('a', toggle_audio_recording)