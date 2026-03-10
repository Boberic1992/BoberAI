import base64
import threading
import time
from io import BytesIO

from PIL import ImageGrab


def setup_window_controls(root):
    def toggle_visibility(event=None):
        current_alpha = root.attributes('-alpha')
        root.attributes('-alpha', 0.0 if current_alpha > 0 else 0.7)

    root.bind('<Control-Shift-KeyPress-H>', toggle_visibility)


def _capture_screenshot(root):
    """Hide window, grab screen, restore window, return base64 PNG."""
    current_alpha = root.attributes('-alpha')
    try:
        root.attributes('-alpha', 0.0)
        root.update()
        time.sleep(0.1)

        screenshot = ImageGrab.grab()
    finally:
        root.attributes('-alpha', current_alpha)

    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def setup_screenshot_controls(root, speech):
    def on_explain_screenshot(event=None):
        try:
            img_str = _capture_screenshot(root)
            speech.process_screenshot(img_str)
        except Exception as e:
            speech.update_text(f"[INFO]Screenshot error: {e}")

    def on_debug_screenshot(event=None):
        try:
            img_str = _capture_screenshot(root)
            speech.debug_screenshot(img_str)
        except Exception as e:
            speech.update_text(f"[INFO]Screenshot error: {e}")

    root.bind('<Control-Shift-KeyPress-S>', on_explain_screenshot)
    root.bind('<Control-Shift-KeyPress-D>', on_debug_screenshot)


def setup_recording_controls(root, speech, update_info_label):
    def toggle_audio_recording(event):
        if speech.is_audio_recording:
            speech.is_audio_recording = False
            speech.update_text("[INFO] Recording stopped")
        else:
            speech.is_audio_recording = True
            threading.Thread(target=speech.continuous_audio_recording).start()
            speech.update_text("[REC] Continuous recording started - Press 'A' to stop")

    root.bind('a', toggle_audio_recording)
