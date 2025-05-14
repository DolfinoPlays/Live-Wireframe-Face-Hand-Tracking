import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog
import json
import os
from collections import deque
from datetime import datetime
import threading
import time
from threading import Lock
import pyaudio
import audioop

class ModernSettingsUI:
    def __init__(self, tracker):
        self.tracker = tracker
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.saves_dir = os.path.join(self.script_dir, "saves")
        self.color_presets_dir = os.path.join(self.script_dir, "color_presets")
        self.autosave_dir = os.path.join(self.script_dir, "autosave")
        for directory in [self.saves_dir, self.color_presets_dir, self.autosave_dir]:
            os.makedirs(directory, exist_ok=True)
        self.thread = threading.Thread(target=self.run_ui, daemon=True)
        self.thread.start()
        
    def run_ui(self):
        self.root = tk.Tk()
        self.root.title("Face Tracker Settings")
        self.root.geometry("450x700")
        self.root.configure(bg='#2b2b2b')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        self.notebook = ttk.Notebook(self.root, style='Dark.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        self.create_appearance_tab()
        self.create_color_presets_tab()
        self.create_saves_tab()
        self.create_experiments_tab()
        self.create_performance_tab()
        self.status_bar = tk.Label(self.root, text="Ready", bg='#1e1e1e', fg='white', relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(100, self.load_autosave)
        self.root.mainloop()
        
    def configure_styles(self):
        self.style.configure('Dark.TNotebook', background='#2b2b2b', borderwidth=0)
        self.style.configure('Dark.TNotebook.Tab', background='#3c3c3c', foreground='white', padding=[20, 10])
        self.style.map('Dark.TNotebook.Tab', background=[('selected', '#555555')])
        self.style.configure('Dark.TFrame', background='#2b2b2b')
        self.style.configure('Dark.TLabel', background='#2b2b2b', foreground='white')
        self.style.configure('Dark.TButton', background='#3c3c3c', foreground='white', borderwidth=0, focuscolor='none')
        self.style.map('Dark.TButton', background=[('active', '#555555')])
        self.style.configure('Dark.TCheckbutton', background='#2b2b2b', foreground='white', focuscolor='none')
        self.style.configure('Dark.TRadiobutton', background='#2b2b2b', foreground='white', focuscolor='none')
        self.style.configure('Dark.Horizontal.TScale', background='#2b2b2b', troughcolor='#3c3c3c', borderwidth=0)
        
    def create_appearance_tab(self):
        tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(tab, text='Appearance')
        mode_frame = ttk.Frame(tab, style='Dark.TFrame')
        mode_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(mode_frame, text="Mode:", style='Dark.TLabel').pack(side='left', padx=(0, 10))
        self.mode_var = tk.StringVar(value=self.tracker.modes[self.tracker.mode])
        self.mode_menu = ttk.Combobox(mode_frame, textvariable=self.mode_var, values=self.tracker.modes, state='readonly', width=15)
        self.mode_menu.pack(side='left')
        self.mode_menu.bind('<<ComboboxSelected>>', self.on_mode_change)
        conn_frame = ttk.Frame(tab, style='Dark.TFrame')
        conn_frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(conn_frame, text="Connection:", style='Dark.TLabel').pack(side='left', padx=(0, 10))
        self.conn_var = tk.StringVar(value=self.tracker.current_connection)
        self.conn_menu = ttk.Combobox(conn_frame, textvariable=self.conn_var, values=list(self.tracker.connection_types.keys()), state='readonly', width=15)
        self.conn_menu.pack(side='left')
        self.conn_menu.bind('<<ComboboxSelected>>', self.on_connection_change)
        toggles_frame = ttk.Frame(tab, style='Dark.TFrame')
        toggles_frame.pack(fill='x', padx=20, pady=10)
        self.show_camera_var = tk.BooleanVar(value=self.tracker.show_camera)
        camera_check = ttk.Checkbutton(toggles_frame, text="Show Camera Feed", variable=self.show_camera_var,
                                      command=self.on_camera_toggle, style='Dark.TCheckbutton')
        camera_check.pack(anchor='w', pady=2)
        self.show_hands_var = tk.BooleanVar(value=self.tracker.show_hands)
        hands_check = ttk.Checkbutton(toggles_frame, text="Show Hands", variable=self.show_hands_var,
                                     command=self.on_hands_toggle, style='Dark.TCheckbutton')
        hands_check.pack(anchor='w', pady=2)
        ttk.Label(toggles_frame, text="Camera Opacity:", style='Dark.TLabel').pack(anchor='w', pady=(10, 0))
        self.camera_opacity_var = tk.DoubleVar(value=self.tracker.camera_opacity)
        opacity_scale = ttk.Scale(toggles_frame, from_=0.1, to=1.0, orient='horizontal',
                                 variable=self.camera_opacity_var, command=self.on_camera_opacity_change,
                                 style='Dark.Horizontal.TScale')
        opacity_scale.pack(fill='x', pady=5)
        ttk.Label(tab, text="Colors:", style='Dark.TLabel').pack(anchor='w', padx=20, pady=(10, 5))
        self.create_color_control(tab, "Dot Color", self.tracker.dot_color, self.on_dot_color_change)
        self.create_color_control(tab, "Line Color", self.tracker.line_color, self.on_line_color_change)
        self.create_color_control(tab, "Background", self.tracker.bg_color, self.on_bg_color_change)
        size_frame = ttk.Frame(tab, style='Dark.TFrame')
        size_frame.pack(fill='x', padx=20, pady=20)
        ttk.Label(size_frame, text="Dot Size:", style='Dark.TLabel').pack()
        self.dot_size_var = tk.IntVar(value=self.tracker.dot_size)
        dot_scale = ttk.Scale(size_frame, from_=1, to=10, orient='horizontal', variable=self.dot_size_var, 
                             command=self.on_dot_size_change, style='Dark.Horizontal.TScale')
        dot_scale.pack(fill='x', pady=5)
        ttk.Label(size_frame, text="Line Width:", style='Dark.TLabel').pack()
        self.line_width_var = tk.IntVar(value=self.tracker.line_thickness)
        line_scale = ttk.Scale(size_frame, from_=1, to=5, orient='horizontal', variable=self.line_width_var,
                              command=self.on_line_width_change, style='Dark.Horizontal.TScale')
        line_scale.pack(fill='x', pady=5)
        
    def create_color_presets_tab(self):
        tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(tab, text='Color Presets')
        self.default_presets = {
            "Neon": {"dot_color": [255, 0, 255], "line_color": [0, 255, 255], "bg_color": [0, 0, 0]},
            "Matrix": {"dot_color": [0, 255, 0], "line_color": [0, 200, 0], "bg_color": [0, 0, 0]},
            "Cyberpunk": {"dot_color": [255, 0, 128], "line_color": [0, 255, 255], "bg_color": [16, 0, 32]},
            "Wireframe": {"dot_color": [255, 255, 255], "line_color": [128, 128, 128], "bg_color": [0, 0, 0]},
            "Ocean": {"dot_color": [255, 200, 0], "line_color": [255, 100, 0], "bg_color": [40, 20, 0]},
            "Sunset": {"dot_color": [0, 200, 255], "line_color": [0, 100, 200], "bg_color": [0, 20, 40]}
        }
        preset_frame = ttk.Frame(tab, style='Dark.TFrame')
        preset_frame.pack(fill='both', expand=True, padx=20, pady=10)
        ttk.Label(preset_frame, text="Available Color Presets:", style='Dark.TLabel').pack()
        self.preset_listbox = tk.Listbox(preset_frame, bg='#3c3c3c', fg='white', selectbackground='#555555')
        self.preset_listbox.pack(fill='both', expand=True, pady=10)
        button_frame = ttk.Frame(preset_frame, style='Dark.TFrame')
        button_frame.pack(fill='x')
        ttk.Button(button_frame, text="Load", command=self.load_color_preset, style='Dark.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Save Current", command=self.save_color_preset, style='Dark.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_color_preset, style='Dark.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_color_preset_list, style='Dark.TButton').pack(side='left', padx=5)
        self.refresh_color_preset_list()
    
    def create_saves_tab(self):
        tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(tab, text='Saves')
        save_frame = ttk.Frame(tab, style='Dark.TFrame')
        save_frame.pack(fill='both', expand=True, padx=20, pady=10)
        ttk.Label(save_frame, text="Saved Configurations:", style='Dark.TLabel').pack()
        self.save_listbox = tk.Listbox(save_frame, bg='#3c3c3c', fg='white', selectbackground='#555555')
        self.save_listbox.pack(fill='both', expand=True, pady=10)
        button_frame = ttk.Frame(save_frame, style='Dark.TFrame')
        button_frame.pack(fill='x')
        ttk.Button(button_frame, text="Load", command=self.load_save, style='Dark.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Save Current", command=self.save_current, style='Dark.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_save, style='Dark.TButton').pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.refresh_save_list, style='Dark.TButton').pack(side='left', padx=5)
        self.start_save_monitor()
        self.refresh_save_list()
        
    def create_experiments_tab(self):
        tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(tab, text='Experiments')
        info_label = ttk.Label(tab, text="Enable experimental features (may affect performance)", 
                              style='Dark.TLabel', font=('Arial', 10, 'bold'))
        info_label.pack(padx=20, pady=10)
        self.exp_expression_triggers = tk.BooleanVar(value=self.tracker.experiments.get('expression_triggers', False))
        exp1_check = ttk.Checkbutton(tab, text="Expression Triggers (Emotion-based colors)", 
                                    variable=self.exp_expression_triggers,
                                    command=self.on_exp_expression_toggle, style='Dark.TCheckbutton')
        exp1_check.pack(anchor='w', padx=20, pady=5)
        self.expression_frame = ttk.LabelFrame(tab, text="Expression Settings", style='Dark.TFrame')
        self.expression_frame.pack(fill='x', padx=40, pady=5)
        self.emotion_colors = {
            'happy': tk.StringVar(value=str(self.tracker.emotion_colors.get('happy', [0, 255, 0]))),
            'sad': tk.StringVar(value=str(self.tracker.emotion_colors.get('sad', [255, 0, 0]))),
            'angry': tk.StringVar(value=str(self.tracker.emotion_colors.get('angry', [0, 0, 255]))),
            'neutral': tk.StringVar(value=str(self.tracker.emotion_colors.get('neutral', [128, 128, 128])))
        }
        for emotion, color_var in self.emotion_colors.items():
            self.create_emotion_color_control(self.expression_frame, emotion.capitalize(), emotion)
        self.toggle_expression_settings()
        self.exp_additional_modes = tk.BooleanVar(value=self.tracker.experiments.get('additional_modes', False))
        exp2_check = ttk.Checkbutton(tab, text="Additional Visualization Modes", 
                                    variable=self.exp_additional_modes,
                                    command=self.on_exp_modes_toggle, style='Dark.TCheckbutton')
        exp2_check.pack(anchor='w', padx=20, pady=5)
        modes_info = ttk.Label(tab, text="    Adds: Skeleton, Wireframe Triangle, Wireframe Hexagon", 
                              style='Dark.TLabel', font=('Arial', 9))
        modes_info.pack(anchor='w', padx=40, pady=2)
        self.exp_audio_visualizer = tk.BooleanVar(value=self.tracker.experiments.get('audio_visualizer', False))
        exp3_check = ttk.Checkbutton(tab, text="Audio Visualizer (Mic controls thickness)", 
                                    variable=self.exp_audio_visualizer,
                                    command=self.on_exp_audio_toggle, style='Dark.TCheckbutton')
        exp3_check.pack(anchor='w', padx=20, pady=5)
        self.audio_frame = ttk.LabelFrame(tab, text="Audio Settings", style='Dark.TFrame')
        self.audio_frame.pack(fill='x', padx=40, pady=5)
        self.audio_sensitivity = tk.DoubleVar(value=self.tracker.audio_sensitivity)
        ttk.Label(self.audio_frame, text="Sensitivity:", style='Dark.TLabel').pack(anchor='w', padx=10)
        sensitivity_scale = ttk.Scale(self.audio_frame, from_=0.1, to=5.0, orient='horizontal',
                                     variable=self.audio_sensitivity, command=self.on_audio_sensitivity_change,
                                     style='Dark.Horizontal.TScale')
        sensitivity_scale.pack(fill='x', padx=10, pady=5)
        self.toggle_audio_settings()
    
    def create_performance_tab(self):
        tab = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(tab, text='Performance')
        self.performance_mode = tk.BooleanVar(value=self.tracker.performance_mode)
        perf_check = ttk.Checkbutton(tab, text="Performance Mode (Higher FPS)", variable=self.performance_mode,
                                    command=self.on_performance_toggle, style='Dark.TCheckbutton')
        perf_check.pack(padx=20, pady=10)
        self.show_fps = tk.BooleanVar(value=self.tracker.show_fps)
        fps_check = ttk.Checkbutton(tab, text="Show FPS", variable=self.show_fps,
                                   command=self.on_fps_toggle, style='Dark.TCheckbutton')
        fps_check.pack(padx=20, pady=10)
        self.auto_save = tk.BooleanVar(value=True)
        auto_save_check = ttk.Checkbutton(tab, text="Auto-save settings", variable=self.auto_save,
                                         style='Dark.TCheckbutton')
        auto_save_check.pack(padx=20, pady=10)
        info_frame = ttk.LabelFrame(tab, text="Performance Mode Info", style='Dark.TFrame')
        info_frame.pack(fill='x', padx=20, pady=10)
        info_text = """Performance mode optimizes tracking by:
• Reducing face mesh resolution
• Lowering detection confidence
• Decreasing tracking smoothness
• Simplifying hand tracking
        
This can improve FPS from 10-15 to 30-60."""
        info_label = ttk.Label(info_frame, text=info_text, style='Dark.TLabel', justify='left')
        info_label.pack(padx=10, pady=10)
    
    def create_emotion_color_control(self, parent, label, emotion):
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(frame, text=f"{label}:", style='Dark.TLabel').pack(side='left', padx=(0, 10))
        current_color = eval(self.emotion_colors[emotion].get())
        color_frame = tk.Frame(frame, width=50, height=25, bg=self.rgb_to_hex(current_color), relief=tk.RAISED, bd=2)
        color_frame.pack(side='left', padx=(0, 10))
        if not hasattr(self, 'emotion_color_frames'):
            self.emotion_color_frames = {}
        self.emotion_color_frames[emotion] = color_frame
        ttk.Button(frame, text="Choose", 
                  command=lambda: self.choose_emotion_color(emotion, color_frame),
                  style='Dark.TButton').pack(side='left')
    
    def choose_emotion_color(self, emotion, color_frame):
        current_color = eval(self.emotion_colors[emotion].get())
        color = colorchooser.askcolor(initialcolor=self.rgb_to_hex(current_color))
        if color[0]:
            new_color = [int(color[0][2]), int(color[0][1]), int(color[0][0])]
            self.emotion_colors[emotion].set(str(new_color))
            self.tracker.emotion_colors[emotion] = new_color
            color_frame.configure(bg=color[1])
            self.schedule_autosave()
    
    def toggle_expression_settings(self):
        if self.exp_expression_triggers.get():
            self.expression_frame.pack(fill='x', padx=40, pady=5)
        else:
            self.expression_frame.pack_forget()
    
    def toggle_audio_settings(self):
        if self.exp_audio_visualizer.get():
            self.audio_frame.pack(fill='x', padx=40, pady=5)
        else:
            self.audio_frame.pack_forget()
    
    def on_exp_expression_toggle(self):
        self.tracker.experiments['expression_triggers'] = self.exp_expression_triggers.get()
        self.toggle_expression_settings()
        self.schedule_autosave()
    
    def on_exp_modes_toggle(self):
        self.tracker.experiments['additional_modes'] = self.exp_additional_modes.get()
        self.tracker.update_modes()
        self.mode_var.set(self.tracker.modes[self.tracker.mode])
        self.mode_menu['values'] = self.tracker.modes
        self.schedule_autosave()
    
    def on_exp_audio_toggle(self):
        self.tracker.experiments['audio_visualizer'] = self.exp_audio_visualizer.get()
        if self.exp_audio_visualizer.get():
            self.tracker.start_audio_stream()
        else:
            self.tracker.stop_audio_stream()
        self.toggle_audio_settings()
        self.schedule_autosave()
    
    def on_audio_sensitivity_change(self, value):
        self.tracker.audio_sensitivity = float(value)
        self.schedule_autosave()
    
    def create_color_control(self, parent, label, color, callback):
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.pack(fill='x', padx=20, pady=10)
        ttk.Label(frame, text=f"{label}:", style='Dark.TLabel').pack(side='left', padx=(0, 10))
        color_frame = tk.Frame(frame, width=50, height=25, bg=self.rgb_to_hex(color), relief=tk.RAISED, bd=2)
        color_frame.pack(side='left', padx=(0, 10))
        if not hasattr(self, 'color_frames'):
            self.color_frames = []
        attr_map = {
            "Dot Color": "dot_color",
            "Line Color": "line_color",
            "Background": "bg_color"
        }
        self.color_frames.append((color_frame, color, attr_map.get(label)))
        ttk.Button(frame, text="Choose", command=lambda: self.choose_color(color, callback, color_frame),
                  style='Dark.TButton').pack(side='left')
    
    def rgb_to_hex(self, rgb):
        return '#{:02x}{:02x}{:02x}'.format(rgb[2], rgb[1], rgb[0])
    
    def choose_color(self, current_color, callback, color_frame):
        rgb_color = (current_color[2], current_color[1], current_color[0])
        color = colorchooser.askcolor(initialcolor=self.rgb_to_hex(current_color))
        if color[0]:
            new_color = [int(color[0][2]), int(color[0][1]), int(color[0][0])]
            callback(new_color)
            color_frame.configure(bg=color[1])
    
    def on_mode_change(self, event=None):
        self.tracker.mode = self.tracker.modes.index(self.mode_var.get())
        self.schedule_autosave()
        
    def on_connection_change(self, event=None):
        self.tracker.current_connection = self.conn_var.get()
        self.schedule_autosave()
        
    def on_dot_color_change(self, color):
        self.tracker.dot_color = color
        self.schedule_autosave()
        
    def on_line_color_change(self, color):
        self.tracker.line_color = color
        self.schedule_autosave()
        
    def on_bg_color_change(self, color):
        self.tracker.bg_color = color
        self.schedule_autosave()
        
    def on_dot_size_change(self, value):
        self.tracker.dot_size = int(float(value))
        self.schedule_autosave()
        
    def on_line_width_change(self, value):
        self.tracker.line_thickness = int(float(value))
        self.schedule_autosave()
    
    def on_fps_toggle(self):
        self.tracker.show_fps = self.show_fps.get()
        self.schedule_autosave()
    
    def on_camera_toggle(self):
        self.tracker.show_camera = self.show_camera_var.get()
        self.schedule_autosave()
    
    def on_camera_opacity_change(self, value):
        self.tracker.camera_opacity = float(value)
        self.schedule_autosave()
    
    def on_hands_toggle(self):
        self.tracker.show_hands = self.show_hands_var.get()
        self.schedule_autosave()
    
    def on_performance_toggle(self):
        self.tracker.performance_mode = self.performance_mode.get()
        self.tracker.update_performance_settings()
        self.schedule_autosave()
    
    def schedule_autosave(self):
        if hasattr(self, 'autosave_timer') and self.autosave_timer:
            self.root.after_cancel(self.autosave_timer)
        self.autosave_timer = self.root.after(1000, self.autosave_settings)
    
    def autosave_settings(self):
        if self.auto_save.get():
            autosave_path = os.path.join(self.autosave_dir, "autosave.json")
            self.save_all_settings(autosave_path)
    
    def save_all_settings(self, filepath):
        settings = {
            "mode": self.tracker.mode,
            "connection": self.tracker.current_connection,
            "dot_color": self.tracker.dot_color,
            "line_color": self.tracker.line_color,
            "bg_color": self.tracker.bg_color,
            "dot_size": self.tracker.dot_size,
            "line_thickness": self.tracker.line_thickness,
            "show_fps": self.tracker.show_fps,
            "show_camera": self.tracker.show_camera,
            "camera_opacity": self.tracker.camera_opacity,
            "show_hands": self.tracker.show_hands,
            "performance_mode": self.tracker.performance_mode,
            "experiments": self.tracker.experiments,
            "emotion_colors": self.tracker.emotion_colors,
            "audio_sensitivity": self.tracker.audio_sensitivity
        }
        try:
            with open(filepath, "w") as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_all_settings(self, filepath):
        try:
            with open(filepath, "r") as f:
                settings = json.load(f)
            self.tracker.mode = settings.get("mode", 0)
            self.tracker.current_connection = settings.get("connection", "TESSELATION")
            self.tracker.dot_color = settings.get("dot_color", [255, 255, 0])
            self.tracker.line_color = settings.get("line_color", [0, 255, 0])
            self.tracker.bg_color = settings.get("bg_color", [0, 0, 0])
            self.tracker.dot_size = settings.get("dot_size", 2)
            self.tracker.line_thickness = settings.get("line_thickness", 1)
            self.tracker.show_fps = settings.get("show_fps", True)
            self.tracker.show_camera = settings.get("show_camera", False)
            self.tracker.camera_opacity = settings.get("camera_opacity", 0.5)
            self.tracker.show_hands = settings.get("show_hands", True)
            self.tracker.performance_mode = settings.get("performance_mode", False)
            self.tracker.experiments = settings.get("experiments", {
                'expression_triggers': False,
                'additional_modes': False,
                'audio_visualizer': False
            })
            self.tracker.emotion_colors = settings.get("emotion_colors", {
                'happy': [0, 255, 0],
                'sad': [255, 0, 0],
                'angry': [0, 0, 255],
                'neutral': [128, 128, 128]
            })
            self.tracker.audio_sensitivity = settings.get("audio_sensitivity", 1.0)
            self.tracker.update_modes()
            self.update_ui_from_settings()
            return True
            
        except json.JSONDecodeError:
            os.remove(filepath)
            return False
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
    
    def update_ui_from_settings(self):
        self.mode_var.set(self.tracker.modes[self.tracker.mode])
        self.mode_menu['values'] = self.tracker.modes
        self.conn_var.set(self.tracker.current_connection)
        self.dot_size_var.set(self.tracker.dot_size)
        self.line_width_var.set(self.tracker.line_thickness)
        self.show_camera_var.set(self.tracker.show_camera)
        self.camera_opacity_var.set(self.tracker.camera_opacity)
        self.show_hands_var.set(self.tracker.show_hands)
        self.show_fps.set(self.tracker.show_fps)
        self.performance_mode.set(self.tracker.performance_mode)
        if hasattr(self, 'exp_expression_triggers'):
            self.exp_expression_triggers.set(self.tracker.experiments.get('expression_triggers', False))
            self.exp_additional_modes.set(self.tracker.experiments.get('additional_modes', False))
            self.exp_audio_visualizer.set(self.tracker.experiments.get('audio_visualizer', False))
            self.audio_sensitivity.set(self.tracker.audio_sensitivity)
        if hasattr(self, 'emotion_colors'):
            for emotion, color in self.tracker.emotion_colors.items():
                self.emotion_colors[emotion].set(str(color))
        for frame, color, attr in self.color_frames:
            current_color = getattr(self.tracker, attr)
            frame.configure(bg=self.rgb_to_hex(current_color))
    
    def load_autosave(self):
        autosave_path = os.path.join(self.autosave_dir, "autosave.json")
        if os.path.exists(autosave_path):
            if not self.load_all_settings(autosave_path):
                self.status_bar.config(text="Autosave corrupted, using defaults")
            else:
                self.status_bar.config(text="Loaded autosaved settings")
    
    def refresh_save_list(self):
        self.save_listbox.delete(0, tk.END)
        if os.path.exists(self.saves_dir):
            for filename in os.listdir(self.saves_dir):
                if filename.endswith('.json'):
                    name = filename[:-5]
                    self.save_listbox.insert(tk.END, name)
    
    def save_current(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Configuration")
        dialog.geometry("300x100")
        dialog.configure(bg='#2b2b2b')
        tk.Label(dialog, text="Save Name:", bg='#2b2b2b', fg='white').pack(pady=10)
        name_entry = tk.Entry(dialog, bg='#3c3c3c', fg='white')
        name_entry.pack(pady=5)
        
        def save():
            name = name_entry.get()
            if name:
                save_path = os.path.join(self.saves_dir, f"{name}.json")
                if self.save_all_settings(save_path):
                    self.refresh_save_list()
                    dialog.destroy()
                    self.status_bar.config(text=f"Saved configuration: {name}")
                else:
                    messagebox.showerror("Error", "Failed to save configuration")
        ttk.Button(dialog, text="Save", command=save).pack(pady=10)
    
    def load_save(self):
        selection = self.save_listbox.curselection()
        if selection:
            save_name = self.save_listbox.get(selection[0])
            save_path = os.path.join(self.saves_dir, f"{save_name}.json")
            if self.load_all_settings(save_path):
                self.status_bar.config(text=f"Loaded configuration: {save_name}")
            else:
                messagebox.showwarning("Corrupted File", 
                    f"The save file '{save_name}' was corrupted and has been deleted.")
                self.refresh_save_list()
    
    def delete_save(self):
        selection = self.save_listbox.curselection()
        if selection:
            save_name = self.save_listbox.get(selection[0])
            if messagebox.askyesno("Delete Save", f"Delete configuration '{save_name}'?"):
                save_path = os.path.join(self.saves_dir, f"{save_name}.json")
                os.remove(save_path)
                self.refresh_save_list()
                self.status_bar.config(text=f"Deleted configuration: {save_name}")
    
    def start_save_monitor(self):
        def check_saves():
            self.refresh_save_list()
            self.root.after(2000, check_saves)
        self.root.after(2000, check_saves)

    def refresh_color_preset_list(self):
        self.preset_listbox.delete(0, tk.END)
        for name in self.default_presets:
            self.preset_listbox.insert(tk.END, f"[Default] {name}")
        if os.path.exists(self.color_presets_dir):
            for filename in os.listdir(self.color_presets_dir):
                if filename.endswith('.json'):
                    name = filename[:-5]
                    self.preset_listbox.insert(tk.END, name)
    
    def save_color_preset(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Color Preset")
        dialog.geometry("300x100")
        dialog.configure(bg='#2b2b2b')
        tk.Label(dialog, text="Preset Name:", bg='#2b2b2b', fg='white').pack(pady=10)
        name_entry = tk.Entry(dialog, bg='#3c3c3c', fg='white')
        name_entry.pack(pady=5)
        
        def save():
            name = name_entry.get()
            if name:
                preset = {
                    "dot_color": self.tracker.dot_color,
                    "line_color": self.tracker.line_color,
                    "bg_color": self.tracker.bg_color
                }
                preset_path = os.path.join(self.color_presets_dir, f"{name}.json")
                try:
                    with open(preset_path, "w") as f:
                        json.dump(preset, f, indent=2)
                    self.refresh_color_preset_list()
                    dialog.destroy()
                    self.status_bar.config(text=f"Saved color preset: {name}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save preset: {e}")
        ttk.Button(dialog, text="Save", command=save).pack(pady=10)
    
    def load_color_preset(self):
        selection = self.preset_listbox.curselection()
        if selection:
            preset_name = self.preset_listbox.get(selection[0])
            if preset_name.startswith("[Default]"):
                preset_name = preset_name.replace("[Default] ", "")
                preset = self.default_presets[preset_name]
            else:
                preset_path = os.path.join(self.color_presets_dir, f"{preset_name}.json")
                try:
                    with open(preset_path, "r") as f:
                        preset = json.load(f)
                except json.JSONDecodeError:
                    messagebox.showwarning("Corrupted File", 
                        f"The preset file '{preset_name}' was corrupted and has been deleted.")
                    os.remove(preset_path)
                    self.refresh_color_preset_list()
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load preset: {e}")
                    return
            self.tracker.dot_color = preset["dot_color"]
            self.tracker.line_color = preset["line_color"]
            self.tracker.bg_color = preset["bg_color"]
            self.update_ui_from_settings()
            self.status_bar.config(text=f"Loaded color preset: {preset_name}")
            self.schedule_autosave()
    
    def delete_color_preset(self):
        selection = self.preset_listbox.curselection()
        if selection:
            preset_name = self.preset_listbox.get(selection[0])
            if preset_name.startswith("[Default]"):
                messagebox.showwarning("Cannot Delete", "Cannot delete default presets")
                return
            if messagebox.askyesno("Delete Preset", f"Delete color preset '{preset_name}'?"):
                preset_path = os.path.join(self.color_presets_dir, f"{preset_name}.json")
                os.remove(preset_path)
                self.refresh_color_preset_list()
                self.status_bar.config(text=f"Deleted color preset: {preset_name}")
    
    def on_closing(self):
        if hasattr(self, 'auto_save') and self.auto_save.get():
            self.autosave_settings()
        self.root.quit()
    
    def update(self):
        pass
        
    def close(self):
        pass

class FaceTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        cv2.namedWindow('Face Tracking', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Face Tracking', 1280, 720)
        self.mode = 0
        self.modes = ['Mesh', 'Dots']
        self.dot_color = [255, 255, 0]
        self.line_color = [0, 255, 0]
        self.bg_color = [0, 0, 0]
        self.dot_size = 2
        self.line_thickness = 1
        self.connection_types = {
            'TESSELATION': self.mp_face_mesh.FACEMESH_TESSELATION,
            'CONTOURS': self.mp_face_mesh.FACEMESH_CONTOURS,
            'FACE_OVAL': self.mp_face_mesh.FACEMESH_FACE_OVAL,
            'LIPS': self.mp_face_mesh.FACEMESH_LIPS,
            'LEFT_EYE': self.mp_face_mesh.FACEMESH_LEFT_EYE,
            'RIGHT_EYE': self.mp_face_mesh.FACEMESH_RIGHT_EYE
        }
        self.current_connection = 'TESSELATION'
        self.hand_tessellation = self.create_hand_tessellation()
        self.show_camera = False
        self.camera_opacity = 0.5
        self.show_hands = True
        self.performance_mode = False
        self.experiments = {
            'expression_triggers': False,
            'additional_modes': False,
            'audio_visualizer': False
        }
        self.emotion_colors = {
            'happy': [0, 255, 0],
            'sad': [255, 0, 0],
            'angry': [0, 0, 255],
            'neutral': [128, 128, 128]
        }
        self.current_emotion = 'neutral'
        self.audio_sensitivity = 1.0
        self.audio_stream = None
        self.audio_level = 0
        self.mouth_landmarks = [61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318]
        self.eye_landmarks = [33, 133, 157, 158, 159, 160, 161, 246, 263, 362, 387, 388, 389, 390, 391, 467]
        self.eyebrow_landmarks = [46, 52, 53, 63, 68, 70, 71, 55, 285, 295, 300, 293, 334, 296, 276, 283]
        self.show_fps = True
        self.fps_start_time = cv2.getTickCount()
        self.fps_counter = 0
        self.current_fps = 0
        self.settings_ui = ModernSettingsUI(self)
        time.sleep(0.5)
    
    def create_hand_tessellation(self):
        tessellation = []
        tessellation.extend([
            (0, 1), (0, 5), (0, 9), (0, 13), (0, 17),
            (1, 2), (2, 5), (5, 9), (9, 13), (13, 17),
            (1, 5), (5, 9), (9, 13), (13, 17),
            (0, 2), (0, 6), (0, 10), (0, 14), (0, 18),
        ])
        tessellation.extend([
            (1, 2), (2, 3), (3, 4),
            (1, 3), (2, 4),
        ])
        tessellation.extend([
            (5, 6), (6, 7), (7, 8),
            (5, 7), (6, 8),
        ])
        tessellation.extend([
            (9, 10), (10, 11), (11, 12),
            (9, 11), (10, 12),
        ])
        tessellation.extend([
            (13, 14), (14, 15), (15, 16),
            (13, 15), (14, 16),
        ])
        tessellation.extend([
            (17, 18), (18, 19), (19, 20),
            (17, 19), (18, 20),
        ])
        tessellation.extend([
            (2, 5),
            (5, 9), (9, 13), (13, 17),
            (1, 9), (5, 13), (9, 17),
            (2, 9), (5, 17),
        ])
        return list(set(tessellation))
    
    def draw_mesh(self, output_frame, face_landmarks, frame_shape, hand_results=None):
        for idx, landmark in enumerate(face_landmarks.landmark):
            x = int(landmark.x * frame_shape[1])
            y = int(landmark.y * frame_shape[0])
            cv2.circle(output_frame, (x, y), self.dot_size, tuple(self.dot_color), -1)
        connections = self.connection_types[self.current_connection]
        for connection in connections:
            start_idx = connection[0]
            end_idx = connection[1]
            start_point = face_landmarks.landmark[start_idx]
            end_point = face_landmarks.landmark[end_idx]
            start_x = int(start_point.x * frame_shape[1])
            start_y = int(start_point.y * frame_shape[0])
            end_x = int(end_point.x * frame_shape[1])
            end_y = int(end_point.y * frame_shape[0])
            cv2.line(output_frame, (start_x, start_y), (end_x, end_y), 
                    tuple(self.line_color), self.line_thickness)
        if hand_results and hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    x = int(landmark.x * frame_shape[1])
                    y = int(landmark.y * frame_shape[0])
                    cv2.circle(output_frame, (x, y), self.dot_size, tuple(self.dot_color), -1)
                hand_connections = self.hand_tessellation if self.current_connection == 'TESSELATION' else self.mp_hands.HAND_CONNECTIONS
                for connection in hand_connections:
                    start_idx = connection[0]
                    end_idx = connection[1]
                    if start_idx < len(hand_landmarks.landmark) and end_idx < len(hand_landmarks.landmark):
                        start_point = hand_landmarks.landmark[start_idx]
                        end_point = hand_landmarks.landmark[end_idx]
                        start_x = int(start_point.x * frame_shape[1])
                        start_y = int(start_point.y * frame_shape[0])
                        end_x = int(end_point.x * frame_shape[1])
                        end_y = int(end_point.y * frame_shape[0])
                        cv2.line(output_frame, (start_x, start_y), (end_x, end_y), 
                                tuple(self.line_color), self.line_thickness)
    
    def draw_dots_only(self, output_frame, face_landmarks, frame_shape, hand_results=None):
        for idx, landmark in enumerate(face_landmarks.landmark):
            x = int(landmark.x * frame_shape[1])
            y = int(landmark.y * frame_shape[0])
            cv2.circle(output_frame, (x, y), self.dot_size * 2, tuple(self.dot_color), -1)
        if hand_results and hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    x = int(landmark.x * frame_shape[1])
                    y = int(landmark.y * frame_shape[0])
                    cv2.circle(output_frame, (x, y), self.dot_size * 2, tuple(self.dot_color), -1)
    
    def calculate_fps(self):
        self.fps_counter += 1
        current_time = cv2.getTickCount()
        time_diff = (current_time - self.fps_start_time) / cv2.getTickFrequency()
        if time_diff >= 1.0:
            self.current_fps = self.fps_counter / time_diff
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def draw_fps(self, frame):
        if self.show_fps:
            cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    def update_modes(self):
        base_modes = ['Mesh', 'Dots']
        if self.experiments.get('additional_modes', False):
            base_modes.extend(['Skeleton', 'Wireframe Triangle', 'Wireframe Hexagon'])
        self.modes = base_modes
        if self.mode >= len(self.modes):
            self.mode = 0
    
    def start_audio_stream(self):
        if not self.audio_stream:
            try:
                p = pyaudio.PyAudio()
                self.audio_stream = p.open(format=pyaudio.paInt16,
                                         channels=1,
                                         rate=44100,
                                         input=True,
                                         frames_per_buffer=1024,
                                         stream_callback=self.audio_callback)
                self.audio_stream.start_stream()
            except Exception as e:
                print(f"Error starting audio stream: {e}")
    
    def stop_audio_stream(self):
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio_stream = None
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        try:
            rms = audioop.rms(in_data, 2)
            self.audio_level = min(rms / 10000.0, 1.0) * self.audio_sensitivity
        except:
            self.audio_level = 0
        return (in_data, pyaudio.paContinue)
    
    def detect_emotion(self, face_landmarks):
        if not self.experiments.get('expression_triggers', False):
            return 'neutral'
        mouth_points = []
        for idx in self.mouth_landmarks:
            mouth_points.append([
                face_landmarks.landmark[idx].x,
                face_landmarks.landmark[idx].y
            ])
        mouth_left = np.array(mouth_points[0])
        mouth_right = np.array(mouth_points[6])
        mouth_top = np.array(mouth_points[3])
        mouth_bottom = np.array(mouth_points[9])
        mouth_width = np.linalg.norm(mouth_left - mouth_right)
        mouth_height = np.linalg.norm(mouth_top - mouth_bottom)
        mouth_ratio = mouth_height / (mouth_width + 0.001)
        left_eye_top = face_landmarks.landmark[159].y
        left_eye_bottom = face_landmarks.landmark[145].y
        right_eye_top = face_landmarks.landmark[386].y
        right_eye_bottom = face_landmarks.landmark[374].y
        eye_height = ((left_eye_bottom - left_eye_top) + (right_eye_bottom - right_eye_top)) / 2
        left_eyebrow = face_landmarks.landmark[70].y
        right_eyebrow = face_landmarks.landmark[300].y
        eyebrow_height = (left_eyebrow + right_eyebrow) / 2
        forehead_point = face_landmarks.landmark[10].y
        eyebrow_relative = eyebrow_height - forehead_point
        left_corner = face_landmarks.landmark[61].y
        right_corner = face_landmarks.landmark[291].y
        mouth_center = face_landmarks.landmark[13].y
        mouth_curve = ((left_corner + right_corner) / 2) - mouth_center
        if mouth_ratio > 0.3 and mouth_curve < -0.01:
            return 'happy'
        elif eye_height < 0.02 and eyebrow_relative > 0.08:
            return 'sad'
        elif eyebrow_relative < 0.06 and mouth_ratio < 0.2:
            return 'angry'
        else:
            return 'neutral'
    
    def draw_skeleton(self, output_frame, face_landmarks, frame_shape, hand_results=None):
        key_face_points = [
            1,
            33,
            263,
            61,
            291,
            10,
            152,
            234,
            454,
        ]
        for idx in key_face_points:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * frame_shape[1])
            y = int(landmark.y * frame_shape[0])
            cv2.circle(output_frame, (x, y), self.dot_size * 2, tuple(self.dot_color), -1)
        skeleton_connections = [
            (1, 10),
            (1, 152),
            (33, 263),
            (61, 291),
            (234, 33),
            (454, 263),
        ]
        for start_idx, end_idx in skeleton_connections:
            start_point = face_landmarks.landmark[start_idx]
            end_point = face_landmarks.landmark[end_idx]
            start_x = int(start_point.x * frame_shape[1])
            start_y = int(start_point.y * frame_shape[0])
            end_x = int(end_point.x * frame_shape[1])
            end_y = int(end_point.y * frame_shape[0])
            cv2.line(output_frame, (start_x, start_y), (end_x, end_y), 
                    tuple(self.line_color), self.line_thickness)
        if hand_results and hand_results.multi_hand_landmarks and self.show_hands:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                key_hand_points = [0, 4, 8, 12, 16, 20]
                for idx in key_hand_points:
                    landmark = hand_landmarks.landmark[idx]
                    x = int(landmark.x * frame_shape[1])
                    y = int(landmark.y * frame_shape[0])
                    cv2.circle(output_frame, (x, y), self.dot_size * 2, tuple(self.dot_color), -1)
                for idx in [4, 8, 12, 16, 20]:
                    start_point = hand_landmarks.landmark[0]
                    end_point = hand_landmarks.landmark[idx]
                    start_x = int(start_point.x * frame_shape[1])
                    start_y = int(start_point.y * frame_shape[0])
                    end_x = int(end_point.x * frame_shape[1])
                    end_y = int(end_point.y * frame_shape[0])
                    cv2.line(output_frame, (start_x, start_y), (end_x, end_y), 
                            tuple(self.line_color), self.line_thickness)
    
    def draw_wireframe_triangle(self, output_frame, face_landmarks, frame_shape, hand_results=None):
        triangle_indices = [
            (10, 67, 109), (109, 9, 10), (9, 109, 107),
            (33, 133, 157), (263, 362, 387),
            (1, 4, 6), (6, 197, 1), 
            (61, 84, 17), (17, 314, 291),
            (35, 31, 228), (264, 261, 448)
        ]
        for triangle in triangle_indices:
            points = []
            for idx in triangle:
                if idx < len(face_landmarks.landmark):
                    landmark = face_landmarks.landmark[idx]
                    x = int(landmark.x * frame_shape[1])
                    y = int(landmark.y * frame_shape[0])
                    points.append((x, y))
            if len(points) == 3:
                cv2.line(output_frame, points[0], points[1], tuple(self.line_color), self.line_thickness)
                cv2.line(output_frame, points[1], points[2], tuple(self.line_color), self.line_thickness)
                cv2.line(output_frame, points[2], points[0], tuple(self.line_color), self.line_thickness)
                for point in points:
                    cv2.circle(output_frame, point, self.dot_size, tuple(self.dot_color), -1)
        if hand_results and hand_results.multi_hand_landmarks and self.show_hands:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                hand_triangles = [
                    (0, 1, 5), (0, 5, 9), (0, 9, 13), (0, 13, 17),
                    (1, 2, 3), (5, 6, 7), (9, 10, 11), (13, 14, 15), (17, 18, 19)
                ]
                for triangle in hand_triangles:
                    points = []
                    for idx in triangle:
                        landmark = hand_landmarks.landmark[idx]
                        x = int(landmark.x * frame_shape[1])
                        y = int(landmark.y * frame_shape[0])
                        points.append((x, y))
                    cv2.line(output_frame, points[0], points[1], tuple(self.line_color), self.line_thickness)
                    cv2.line(output_frame, points[1], points[2], tuple(self.line_color), self.line_thickness)
                    cv2.line(output_frame, points[2], points[0], tuple(self.line_color), self.line_thickness)
                    for point in points:
                        cv2.circle(output_frame, point, self.dot_size, tuple(self.dot_color), -1)
    
    def draw_wireframe_hexagon(self, output_frame, face_landmarks, frame_shape, hand_results=None):
        hex_centers = [10, 1, 152, 33, 263, 61, 291]
        for center_idx in hex_centers:
            center = face_landmarks.landmark[center_idx]
            center_x = int(center.x * frame_shape[1])
            center_y = int(center.y * frame_shape[0])
            radius = 30
            angles = [i * 60 for i in range(6)]
            hex_points = []
            for angle in angles:
                x = int(center_x + radius * np.cos(np.radians(angle)))
                y = int(center_y + radius * np.sin(np.radians(angle)))
                hex_points.append((x, y))
            for i in range(6):
                cv2.line(output_frame, hex_points[i], hex_points[(i + 1) % 6], 
                        tuple(self.line_color), self.line_thickness)
            cv2.circle(output_frame, (center_x, center_y), self.dot_size * 2, tuple(self.dot_color), -1)
        if hand_results and hand_results.multi_hand_landmarks and self.show_hands:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                hand_hex_centers = [0, 4, 8, 12, 16, 20]
                for center_idx in hand_hex_centers:
                    center = hand_landmarks.landmark[center_idx]
                    center_x = int(center.x * frame_shape[1])
                    center_y = int(center.y * frame_shape[0])
                    radius = 20
                    angles = [i * 60 for i in range(6)]
                    hex_points = []
                    for angle in angles:
                        x = int(center_x + radius * np.cos(np.radians(angle)))
                        y = int(center_y + radius * np.sin(np.radians(angle)))
                        hex_points.append((x, y))
                    for i in range(6):
                        cv2.line(output_frame, hex_points[i], hex_points[(i + 1) % 6], 
                                tuple(self.line_color), self.line_thickness)
                    cv2.circle(output_frame, (center_x, center_y), self.dot_size * 2, tuple(self.dot_color), -1)
    
    def update_performance_settings(self):
        if self.performance_mode:
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=False,
                min_detection_confidence=0.3,
                min_tracking_confidence=0.3
            )
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.3,
                min_tracking_confidence=0.3,
                model_complexity=0
            )
        else:
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
    
    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            hand_results = None
            if self.show_hands and self.mode in [0, 1, 2, 3, 4]:
                hand_results = self.hands.process(rgb_frame)
            if results.multi_face_landmarks and self.experiments.get('expression_triggers', False):
                self.current_emotion = self.detect_emotion(results.multi_face_landmarks[0])
                emotion_color = self.emotion_colors[self.current_emotion]
                self.dot_color = emotion_color
                self.line_color = emotion_color
            original_dot_size = self.dot_size
            original_line_thickness = self.line_thickness
            
            if self.experiments.get('audio_visualizer', False):
                base_size = 1
                audio_multiplier = 1 + (self.audio_level * 9)
                self.dot_size = int(base_size * audio_multiplier)
                self.line_thickness = int(base_size * audio_multiplier)
            if self.show_camera:
                output_frame = cv2.addWeighted(frame, self.camera_opacity, 
                                             np.full_like(frame, self.bg_color), 
                                             1 - self.camera_opacity, 0)
            else:
                output_frame = np.full_like(frame, self.bg_color)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    if self.mode == 0:
                        self.draw_mesh(output_frame, face_landmarks, frame.shape, hand_results)
                    elif self.mode == 1:
                        self.draw_dots_only(output_frame, face_landmarks, frame.shape, hand_results)
                    elif self.mode == 2:
                        self.draw_skeleton(output_frame, face_landmarks, frame.shape, hand_results)
                    elif self.mode == 3:
                        self.draw_wireframe_triangle(output_frame, face_landmarks, frame.shape, hand_results)
                    elif self.mode == 4:
                        self.draw_wireframe_hexagon(output_frame, face_landmarks, frame.shape, hand_results)
            if self.experiments.get('audio_visualizer', False):
                self.dot_size = original_dot_size
                self.line_thickness = original_line_thickness
            self.calculate_fps()
            self.draw_fps(output_frame)
            if self.experiments.get('expression_triggers', False):
                cv2.putText(output_frame, f"Emotion: {self.current_emotion}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, self.emotion_colors[self.current_emotion], 2)
            cv2.imshow('Face Tracking', output_frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                self.mode = (self.mode + 1) % len(self.modes)
                if hasattr(self.settings_ui, 'mode_var') and hasattr(self.settings_ui, 'mode_menu'):
                    try:
                        self.settings_ui.root.after(0, lambda: (
                            self.settings_ui.mode_var.set(self.modes[self.mode]),
                            setattr(self.settings_ui.mode_menu, 'values', self.modes)
                        ))
                    except:
                        pass
        self.cleanup()
    
    def cleanup(self):
        self.stop_audio_stream()
        self.settings_ui.close()
        self.cap.release()
        cv2.destroyAllWindows()
        self.face_mesh.close()
        self.hands.close()

if __name__ == "__main__":
    tracker = FaceTracker()
    tracker.run()
