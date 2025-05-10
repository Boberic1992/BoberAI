import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from ctypes import windll

def create_conversation_text(root):
    conversation_text = ScrolledText(
        root,
        state='disabled',
        width=100,
        height=20,
        wrap="word",
        bg='#262626',
        fg='white',
        font=("Segoe UI", 12)
    )
    conversation_text.pack(padx=10, pady=10)
    
    # Configure tags
    conversation_text.tag_configure("AI_Tag", foreground="#00FF00")
    conversation_text.tag_configure("Me_Tag", foreground="#00BFFF")
    conversation_text.tag_configure("Client_Tag", foreground="#FFA500")
    conversation_text.tag_configure("code", 
        background="#1E1E1E",
        foreground="#D4D4D4",
        font=("Consolas", 12),
        relief="solid",
        borderwidth=1,
        spacing1=10,
        spacing3=10,
        rmargin=10
    )
    
    return conversation_text

def create_info_label(root):
    info_label = tk.Label(
        root,
        text="",
        bg='#262626',
        fg="white",
        font=("Segoe UI", 12)
    )
    info_label.pack(side='top', pady=5)
    return info_label

button_style = {
    'bg': '#262626',
    'fg': 'white',
    'relief': 'flat',
    'padx': 10,
    'pady': 5
}

def create_settings_panel(root, on_language_change=None, on_framework_change=None):
    settings_panel = tk.Frame(
        root,
        bg='#1E1E1E',
        height=100
    )
    
    toggle_button = tk.Label(
        root,
        text="▼",
        bg='#262626',
        fg='white',
        cursor='hand2'
    )
    toggle_button.pack(side='bottom', pady=0)
    
    # Language selection frame on the left
    lang_frame = tk.Frame(settings_panel, bg='#1E1E1E')
    lang_frame.pack(side='left', padx=20, pady=10)
    
    # Language label
    tk.Label(
        lang_frame,
        text="Language:",
        bg='#1E1E1E',
        fg='white',
        font=("Segoe UI", 12) 
    ).pack(anchor='w')
    
    # Create language variable
    selected_lang = tk.StringVar(value="en")
    
    def on_lang_select():
        if on_language_change:
            on_language_change(selected_lang.get())
    
    # English checkbox
    en_check = tk.Radiobutton(
        lang_frame,
        text="English",
        variable=selected_lang,
        value="en",
        command=on_lang_select,
        bg='#1E1E1E',
        fg='white',
        selectcolor='#262626',
        activebackground='#1E1E1E',
        font=("Segoe UI", 12) 
    )
    en_check.pack(anchor='w')
    
    # Serbian checkbox
    sr_check = tk.Radiobutton(
        lang_frame,
        text="Serbian",
        variable=selected_lang,
        value="sr",
        command=on_lang_select,
        bg='#1E1E1E',
        fg='white',
        selectcolor='#262626',
        activebackground='#1E1E1E',
        font=("Segoe UI", 12) 
    )
    sr_check.pack(anchor='w')

    # Framework selection frame on the right
    framework_frame = tk.Frame(settings_panel, bg='#1E1E1E')
    framework_frame.pack(side='left', padx=20, pady=10)
    
    # Framework label
    tk.Label(
        framework_frame,
        text="Framework:",
        bg='#1E1E1E',
        fg='white',
        font=("Segoe UI", 12) 
    ).pack(anchor='w')
    
    # Create framework variable
    selected_framework = tk.StringVar(value="Python")
    
    def on_framework_select():
        if on_framework_change:
            on_framework_change(selected_framework.get())
    
    # Python checkbox
    python_check = tk.Radiobutton(
        framework_frame,
        text="Python",
        variable=selected_framework,
        value="Python",
        command=on_framework_select,
        bg='#1E1E1E',
        fg='white',
        selectcolor='#262626',
        activebackground='#1E1E1E',
        font=("Segoe UI", 12) 
    )
    python_check.pack(anchor='w')
    
    # SQL checkbox
    sql_check = tk.Radiobutton(
        framework_frame,
        text="SQL",
        variable=selected_framework,
        value="SQL",
        command=on_framework_select,
        bg='#1E1E1E',
        fg='white',
        selectcolor='#262626',
        activebackground='#1E1E1E',
        font=("Segoe UI", 12) 
    )
    sql_check.pack(anchor='w')
    
    # Animation state and toggle function (keep existing code)
    settings_panel.is_visible = False
    
    def toggle_panel(event):
        if not settings_panel.is_visible:
            settings_panel.pack(side='bottom', fill='x', before=toggle_button)
            toggle_button.configure(text="▲")
        else:
            settings_panel.pack_forget()
            toggle_button.configure(text="▼")
        settings_panel.is_visible = not settings_panel.is_visible
    
    toggle_button.bind('<Button-1>', toggle_panel)
    
    return settings_panel, selected_lang, selected_framework
