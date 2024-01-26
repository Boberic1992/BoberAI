import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import speech

# Initialize the main window
root = tk.Tk()
root.title("BoberAI")
root.configure(bg='#a1a1a1')
root.iconbitmap('BoberAI_logo.ico')
root.resizable(False,False)

# Create a ScrolledText widget for displaying conversation
conversation_text = ScrolledText(root, state='disabled', width=80, height=20)
conversation_text.pack(padx=10, pady=10)

# Define tags for different senders
conversation_text.tag_configure("AI_Tag", foreground="#008000")  # Green for AI prefix and line
conversation_text.tag_configure("Me_Tag", foreground="#0000FF")  # Blue for Me prefix and line
conversation_text.tag_configure("Client_Tag", foreground="#FFA500")  # Orange for Client prefix and line

# Label for [INFO] messages
info_label = tk.Label(root, text="", bg='#a1a1a1', fg="blue")
info_label.pack(side='top', pady=5)

def update_info_label(message, clear_after=None):
    """Update the info label with a message and optionally clear it after a delay."""
    info_label.config(text=message)
    if clear_after:
        root.after(clear_after, lambda: info_label.config(text=""))

# Update text function for GUI
def update_text(message):
    if "[INFO]" in message or "[REC]" in message:
        # Remove the [INFO] or [REC] prefix
        display_message = message.replace("[INFO]", "").replace("[REC]", "").strip()
        update_info_label(display_message, clear_after=None if "[REC]" in message else 1000)
    else:
        conversation_text.configure(state='normal')
        tag = None
        prefix = ""
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
        conversation_text.insert(tk.END, message + "\n")
        conversation_text.insert(tk.END, "-"*50 + "\n\n", tag)
        conversation_text.configure(state='disabled')
        conversation_text.see(tk.END)

# Set the GUI update callback
speech.set_update_callback(update_text)

# Key event handlers
def on_key_press(event):
    if event.char == 'r':
        start_recording()
    elif event.char == 'a':
        start_audio_recording()

def on_key_release(event):
    if event.char == 'r':
        stop_recording()
    elif event.char == 'a':
        stop_audio_recording()

def start_recording():
    speech.is_recording = True

def stop_recording():
    speech.is_recording = False
    update_info_label("")

def start_audio_recording():
    if not speech.is_audio_recording:
        speech.start_time = speech.time.time()
        threading.Thread(target=speech.record_audio).start()

def stop_audio_recording():
    speech.is_audio_recording = False

def set_language_to_english():
    speech.DEFAULT_LANGUAGE = "en-US"
    update_text("[INFO] Switched to English")

def set_language_to_serbian():
    speech.DEFAULT_LANGUAGE = "sr-RS"
    update_text("[INFO] Prebaceno na Srpski jezik")

# Bind key events
root.bind('<KeyPress>', on_key_press)
root.bind('<KeyRelease>', on_key_release)

# Buttons for language switching
english_button = tk.Button(root, text="Switch to English", command=set_language_to_english)
english_button.pack(side='left', padx=10, pady=10)

serbian_button = tk.Button(root, text="Switch to Serbian", command=set_language_to_serbian)
serbian_button.pack(side='right', padx=10, pady=10)

# Start the speech recording thread
speech_thread = threading.Thread(target=speech.record_mic)
speech_thread.start()

# Start the GUI loop
root.mainloop()

# Clean up when closing the GUI
speech.stop_recording.set()
speech_thread.join()
