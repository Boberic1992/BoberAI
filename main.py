import tkinter as tk
import os
import sys
import ctypes
import speech

from window_setup import setup_window
from gui_elements import create_conversation_text, create_info_label, button_style, create_settings_panel
from event_handlers import setup_window_controls, setup_recording_controls, setup_screenshot_controls
from config import set_language, set_prog_language

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except:
    pass

user_scrolled_up = False

def on_user_scroll(event=None):
    global user_scrolled_up
    # if bottom of scroll region is visible, user is not scrolled up
    user_scrolled_up = conversation_text.yview()[1] < 1.0

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def update_info_label(message, clear_after=None):
    """Update the info label with a message and optionally clear it after a delay."""
    info_label.config(text=message)
    if clear_after:
        root.after(clear_after, lambda: info_label.config(text=""))

def update_text(message):
    if "[INFO]" in message or "[REC]" in message:
        display_message = message.replace("[INFO]", "").replace("[REC]", "").strip()
        update_info_label(display_message, clear_after=None if "[REC]" in message else 1000)
    else:
        conversation_text.configure(state='normal')
        tag = None
        prefix = ""
        
        # Determine the message type
        if message.startswith("BoberAI:"):
            tag = "AI_Tag"
            prefix = "BoberAI:"
            message = message.replace("BoberAI:", "").strip()
        elif message.startswith("Me:"):
            tag = "Me_Tag"
            prefix = "Me:"
            message = message.replace("Me:", "").strip()
        elif message.startswith("Client:"):
            tag = "Client_Tag"
            prefix = "Client:"
            message = message.replace("Client:", "").strip()

        conversation_text.insert(tk.END, prefix + " ", tag)
        
        parts = message.split("```")
        for i, part in enumerate(parts):
            if i % 2 == 0:
                conversation_text.insert(tk.END, part)
            else:
                conversation_text.insert(tk.END, "\n")
                conversation_text.insert(tk.END, part, "code")
                conversation_text.insert(tk.END, "\n")
        
        conversation_text.insert(tk.END, "\n")
        conversation_text.insert(tk.END, "-"*50 + "\n\n", tag)
        conversation_text.configure(state='disabled')
        if not user_scrolled_up:
            conversation_text.see(tk.END)

def on_language_change(new_lang):
    set_language(new_lang)

def on_framework_change(new_lang):
    set_prog_language(new_lang)



def main():
    global root, conversation_text, info_label

    # Initialize main window
    root = tk.Tk()
    root = setup_window(root, resource_path)

    # Create GUI elements
    conversation_text = create_conversation_text(root)
    conversation_text.bind("<MouseWheel>", on_user_scroll) 
    info_label = create_info_label(root)
    
    create_settings_panel(root, on_language_change, on_framework_change)

    # Set up controls
    setup_window_controls(root)
    setup_screenshot_controls(root, speech)
    setup_recording_controls(root, speech, update_info_label)

    # Set up speech callback
    speech.set_update_callback(update_text)

    # Start GUI loop
    root.mainloop()


if __name__ == "__main__":
    main()