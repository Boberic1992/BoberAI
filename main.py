import ctypes
import os
import sys
import tkinter as tk

import speech
from config import set_interview_mode, set_language, set_prog_language
from event_handlers import setup_recording_controls, setup_screenshot_controls, setup_window_controls
from gui_elements import create_conversation_text, create_info_label, create_settings_panel
from window_setup import setup_window

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
except Exception:
    pass

user_scrolled_up = False


def on_user_scroll(event=None):
    global user_scrolled_up
    # If bottom of scroll region is visible, user is not scrolled up
    user_scrolled_up = conversation_text.yview()[1] < 1.0


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def update_info_label(message, clear_after=None):
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
        for label, tag_name in [("BoberAI:", "AI_Tag"), ("Me:", "Me_Tag"), ("Client:", "Client_Tag")]:
            if message.startswith(label):
                tag = tag_name
                prefix = label
                message = message[len(label):].strip()
                break

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
        conversation_text.insert(tk.END, "-" * 50 + "\n\n", tag)
        conversation_text.configure(state='disabled')

        if not user_scrolled_up:
            conversation_text.see(tk.END)


def main():
    global root, conversation_text, info_label

    root = tk.Tk()
    root = setup_window(root, resource_path)

    conversation_text = create_conversation_text(root)
    conversation_text.bind("<MouseWheel>", on_user_scroll)
    info_label = create_info_label(root)

    create_settings_panel(root, set_language, set_prog_language, set_interview_mode)

    setup_window_controls(root)
    setup_screenshot_controls(root, speech)
    setup_recording_controls(root, speech, update_info_label)

    speech.set_update_callback(update_text)

    root.mainloop()


if __name__ == "__main__":
    main()
