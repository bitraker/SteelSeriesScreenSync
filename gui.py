from typing import Dict
import tkinter
import tkinter.messagebox
import customtkinter

import sys

import pystray # tray
from pystray import MenuItem as item # tray
from PIL import Image # tray

from functools import partial

from steelseries import ScreenSync

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")

class ScreenSamplingArea(customtkinter.CTk):
    def __init__(self, screensync: ScreenSync, logger, x = None, y = None, width = None, height = None):
        super().__init__()

        self.screensync = screensync
        self.logger = logger
        self.x0 = 0 if x is None else x
        self.y0 = 0 if y is None else y
        self.x1 = self.winfo_screenwidth() if width is None else self.x0 + width
        self.y1 = self.winfo_screenheight() if height is None else self.y0 + height
        self.drag = None
        self.end = None

        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.overrideredirect(True)
        self.attributes("-alpha", 0.05)

        self.canvas = tkinter.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight())
        self.canvas.pack()

        self.rect = self.canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, fill = "green")

        self.select_listener = self.bind('<Button-1>', self.start_drag)
        self.move_listener = self.bind('<Button-3>', self.start_move)
        self.snap_listener = self.bind('<Button-2>', self.keyboard_resize)
        self.horizontal_listener = self.bind('<Control-Button-1>', self.center_horizontal)
        self.vertical_listener = self.bind('<Control-Button-3>', self.center_vertical)

    def set_rect(self, x0, y0, x1, y1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.update_rect()

    def update_rect(self):
        self.canvas.coords(self.rect, self.x0, self.y0, self.x1, self.y1)

    def center_horizontal(self, _):
        w = self.x1 - self.x0
        self.x0 = self.winfo_screenwidth() // 2 - w // 2
        self.x1 = self.x0 + w
        self.update_rect()

    def center_vertical(self, _):
        h = self.y1 - self.y0
        self.y0 = self.winfo_screenheight() // 2 - h // 2
        self.y1 = self.y0 + h
        self.update_rect()

    def start_drag(self, event):
        self.unbind('<Button-3>', self.move_listener)
        self.unbind('<Button-2>', self.snap_listener)
        self.x0 = event.x
        self.y0 = event.y
        self.drag = self.bind('<B1-Motion>', self.update_drag)
        self.end = self.bind('<ButtonRelease-1>', self.end_drag)

    def start_drag(self, event):
        self.unbind('<Button-3>', self.move_listener)
        self.unbind('<Button-2>', self.snap_listener)
        self.x0 = event.x
        self.y0 = event.y
        self.drag = self.bind('<B1-Motion>', self.update_drag)
        self.end = self.bind('<ButtonRelease-1>', self.end_drag)

    def update_drag(self, event):
        self.x1 = event.x
        self.y1 = event.y
        self.update_rect()

    def end_drag(self, _):
        self.unbind('<B1-Motion>', self.drag)
        self.unbind('<ButtonRelease-1>', self.end)
        self.move_listener = self.bind('<Button-3>', self.start_move)
        self.snap_listener = self.bind('<Button-2>', self.keyboard_resize)

    def start_move(self, _):
        self.unbind('<Button-1>', self.select_listener)
        self.unbind('<Button-2>', self.snap_listener)
        self.drag = self.bind('<B3-Motion>', self.update_move)
        self.end = self.bind('<ButtonRelease-3>', self.end_move)

    def update_move(self, event):
        self.x1 = event.x + self.x1 - self.x0
        self.y1 = event.y + self.y1 - self.y0
        self.x0 = event.x
        self.y0 = event.y
        self.update_rect()

    def end_move(self, _):
        self.unbind('<B3-Motion>', self.drag)
        self.unbind('<ButtonRelease-3>', self.end)
        self.select_listener = self.bind('<Button-1>', self.start_drag)
        self.snap_listener = self.bind('<Button-2>', self.keyboard_resize)

    def keyboard_resize(self, *_):
        self.y1 = self.y0 + int((self.x1 - self.x0) * (self.screensync.keyboard['height'] / float(self.screensync.keyboard['width'])))
        self.update_rect()

    def start(self):
        try:
            self.mainloop()
        except:
            sys.exit()

class ScreenSyncApp(customtkinter.CTk):

    def __init__(self, screensync: ScreenSync, logger):
        super().__init__()
        self.screensync = screensync
        self.logger = logger
        self.dark_mode = True
        self.screen_sampling_area = None

        # SETUP
        self.title("Bitraker - SteelSeries Screen Sync")
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # TRAY
        self.tray_image=Image.open("logo.ico")
        self.menu=(item("Quit", self.quit), item("Show", self.show_window))

        # FRAME
        self.frame = customtkinter.CTkFrame(master=self,corner_radius=5)
        self.frame.grid(row=0, column=0, sticky="nswe")
        self.frame.grid_rowconfigure(0, minsize=10)

        # SWITCHES
        self.sw_dark_mode = customtkinter.CTkSwitch(master=self.frame,
                                                text="Dark Mode",
                                                command=self.change_mode)
        self.sw_dark_mode.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        self.sw_start_in_tray = customtkinter.CTkSwitch(master=self.frame,
                                                text="Start in Tray",
                                                command=self.set_traying)
        self.sw_start_in_tray.grid(row=10, column=1, pady=10, padx=20, sticky="w")

        # LABELS
        self.lbl_speed = customtkinter.CTkLabel(master=self.frame,
                                                   text="Speed 10",
                                                   height=25,
                                                   fg_color=("white", "black"),
                                                   justify=tkinter.LEFT)
        self.lbl_speed.grid(column=2, row=0, sticky="nwe", padx=15, pady=15)

        self.lbl_brightness = customtkinter.CTkLabel(master=self.frame,
                                                   text="Bightness 100" ,
                                                   height=25,
                                                   fg_color=("white", "black"),
                                                   justify=tkinter.LEFT)
        self.lbl_brightness.grid(column=2, row=1, sticky="nwe", padx=15, pady=15)

        self.lbl_low_light = customtkinter.CTkLabel(master=self.frame,
                                                   text="Low Light 50" ,
                                                   height=25,
                                                   fg_color=("white", "black"),
                                                   justify=tkinter.LEFT)
        self.lbl_low_light.grid(column=2, row=2, sticky="nwe", padx=15, pady=15)

        # SLIDERS
        self.slider_speed = customtkinter.CTkSlider(master=self.frame,
                                                from_=1,
                                                to=100,
                                                number_of_steps=99,
                                                command=self.set_fading_speed)
        self.slider_speed.grid(row=0, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        self.slider_brightness = customtkinter.CTkSlider(master=self.frame,
                                                from_=1,
                                                to=100,
                                                number_of_steps=99,
                                                command=self.set_brightness)
        self.slider_brightness.grid(row=1, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        self.slider_low_light = customtkinter.CTkSlider(master=self.frame,
                                                from_=1,
                                                to=100,
                                                number_of_steps=99,
                                                command=self.set_low_light)
        self.slider_low_light.grid(row=2, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        # CHECK BOXES
        self.chk_low_light = customtkinter.CTkCheckBox(master=self.frame,
                                                      text="Low Light", command=self.toggle_low_light)
        self.chk_low_light.grid(row=6, column=0, pady=10, padx=20, sticky="w")

        self.chk_fade_effect = customtkinter.CTkCheckBox(master=self.frame,
                                                     text="Fade Effect", command=self.toggle_fading)
        self.chk_fade_effect.grid(row=6, column=1, pady=10, padx=20, sticky="w")

        self.chk_enhanced_rendering = customtkinter.CTkCheckBox(master=self.frame,
                                                     text="Enhanced Rendering", command=self.toggle_enhanced)
        self.chk_enhanced_rendering.grid(row=6, column=2, pady=10, padx=20, sticky="w")

        # BUTTONS
        self.btn_preset_smooth = customtkinter.CTkButton(master=self.frame,
                                                       height=25,
                                                       text="Smooth",
                                                       command=partial(self.change_preset, "smooth"))
        self.btn_preset_smooth.grid(row=0, column=3, columnspan=1, pady=10, padx=20, sticky="we")

        self.btn_preset_responsive = customtkinter.CTkButton(master=self.frame,
                                                       height=25,
                                                       text="Responsive",
                                                       command=partial(self.change_preset, "responsive"))
        self.btn_preset_responsive.grid(row=1, column=3, columnspan=1, pady=10, padx=20, sticky="we")

        self.btn_preset_fast = customtkinter.CTkButton(master=self.frame,
                                                       height=25,
                                                       text="Fast",
                                                       command=partial(self.change_preset, "fast"))
        self.btn_preset_fast.grid(row=2, column=3, columnspan=1, pady=10, padx=20, sticky="we")

        self.lbl_kb_width = customtkinter.CTkLabel(master=self.frame,
                                                   text="Keyboard Width 22" ,
                                                   height=25,
                                                   fg_color=("white", "black"),
                                                   justify=tkinter.LEFT)
        self.lbl_kb_width.grid(row=11, column=0, sticky="nwe", padx=15, pady=15)

        self.lbl_kb_height = customtkinter.CTkLabel(master=self.frame,
                                                   text="Keyboard Height 6" ,
                                                   height=25,
                                                   fg_color=("white", "black"),
                                                   justify=tkinter.LEFT)
        self.lbl_kb_height.grid(row=12, column=0, sticky="nwe", padx=15, pady=15)

        self.slider_kb_width = customtkinter.CTkSlider(master=self.frame,
                                                from_=15,
                                                to=22,
                                                number_of_steps=7,
                                                command=self.set_kb_width)
        self.slider_kb_width.grid(row=11, column=2, columnspan=2, pady=10, padx=20, sticky="we")

        self.slider_kb_height = customtkinter.CTkSlider(master=self.frame,
                                                from_=5,
                                                to=6,
                                                number_of_steps=1,
                                                command=self.set_kb_height)
        self.slider_kb_height.grid(row=12, column=2, columnspan=2, pady=10, padx=20, sticky="we")

        self.btn_select_sampling_area = customtkinter.CTkButton(master=self.frame,
                                                       height=25,
                                                       text="Select Sampling Area",
                                                       command=self.select_sampling_area)
        self.btn_select_sampling_area.grid(row=13, column=0, columnspan=2, pady=10, padx=20, sticky="we")

        self.btn_keyboard_resize = customtkinter.CTkButton(master=self.frame,
                                                       height=25,
                                                       text="Resize to Keyboard",
                                                       command=self.keyboard_resize)
        self.btn_keyboard_resize.grid(row=13, column=2, columnspan=2, pady=10, padx=20, sticky="we")

        self.frame.update()

        self.geometry(f"{self.frame.winfo_reqwidth()}x{self.frame.winfo_reqheight()}")

    def select_sampling_area(self):
        if self.screen_sampling_area is None:
            self.btn_select_sampling_area.set_text("Accept Sampling Area")
            self.btn_select_sampling_area.draw()
            self.screen_sampling_area = ScreenSamplingArea(self.screensync, self.logger, **self.screensync.sample if self.screensync.sample else None)
            self.screen_sampling_area.start()
        else:
            self.screensync.update_sample_area(self.screen_sampling_area.x0, self.screen_sampling_area.y0, self.screen_sampling_area.x1 - self.screen_sampling_area.x0, self.screen_sampling_area.y1 - self.screen_sampling_area.y0)
            self.screen_sampling_area.destroy()
            self.btn_select_sampling_area.set_text("Select Sampling Area")
            self.btn_select_sampling_area.draw()
            self.screen_sampling_area = None

    def keyboard_resize(self):
        if self.screen_sampling_area is not None:
            self.screen_sampling_area.keyboard_resize()

    def toggle_fading(self):
        self.screensync.configure(fade=(self.chk_fade_effect.check_state or False))

    def toggle_enhanced(self):
        self.screensync.configure(enhanced=(self.chk_enhanced_rendering.check_state or False))

    def toggle_low_light(self):
        self.screensync.configure(low_light=(self.chk_low_light.check_state or False))

    def set_fading_speed(self, speed):
        self.lbl_speed.set_text(f"Speed {int(speed)}")
        self.screensync.configure(speed=int(speed))

    def set_kb_width(self, width):
        self.lbl_kb_width.set_text(f"Keyboard Width {int(width)}")
        self.screensync.update_keyboard(int(width), self.screensync.keyboard['height'])

    def set_kb_height(self, height):
        self.lbl_kb_height.set_text(f"Keyboard Height {int(height)}")
        self.screensync.update_keyboard(self.screensync.keyboard['width'], int(height))

    def set_brightness(self, brightness):
        self.lbl_brightness.set_text(f"Brightness {int(brightness)}")
        self.screensync.configure(brightness=int(brightness))

    def set_low_light(self, tolerance):
        self.lbl_low_light.set_text(f"Low Light {int(tolerance)}")
        self.screensync.configure(tolerance=int(tolerance))

    def change_mode(self):
        self.screensync.dark_mode = (self.sw_dark_mode.get() or False)
        customtkinter.set_appearance_mode("dark" if self.screensync.dark_mode else "light")

    def set_traying(self):
        self.screensync.start_in_tray = (self.sw_start_in_tray.get() or False)

    def change_preset(self, preset):
        self.screensync.load_preset(preset)
        self.update_gui()

    def minimize_to_tray(self):
        self.icon=pystray.Icon("SS-ScreenSync", self.tray_image, "SteelSeries ScreenSync", self.menu)
        self.withdraw()
        self.tray_image=Image.open("logo.ico")
        self.icon.run()

    def show_window(self):
        self.icon.stop()
        self.deiconify()

    def quit(self):
        self.on_closing()

    def on_closing(self):
        self.screensync.save()
        self.screensync.running = False
        self.icon.stop()
        self.destroy()

    def update_gui(self):
        self.lbl_low_light.set_text(f"Low Light {self.screensync.tolerance}")
        self.slider_low_light.set(self.screensync.tolerance)
        self.lbl_brightness.set_text(f"Brightness {self.screensync.brightness}")
        self.slider_brightness.set(self.screensync.brightness)
        self.lbl_speed.set_text(f"Speed {self.screensync.speed}")
        self.slider_speed.set(self.screensync.speed)
        self.lbl_kb_width.set_text(f"Keyboard Width {self.screensync.keyboard['width']}")
        self.slider_kb_width.set(self.screensync.keyboard['width'])
        self.lbl_kb_height.set_text(f"Keyboard Height {self.screensync.keyboard['height']}")
        self.slider_kb_height.set(self.screensync.keyboard['height'])
        if self.screensync.fade:
            self.chk_fade_effect.select()
        else:
            self.chk_fade_effect.deselect()
        if self.screensync.low_light:
            self.chk_low_light.select()
        else:
            self.chk_low_light.deselect()
        if self.screensync.dark_mode:
            self.sw_dark_mode.select()
        else:
            self.sw_dark_mode.deselect()
        if self.screensync.start_in_tray:
            self.sw_start_in_tray.select()
        else:
            self.sw_start_in_tray.deselect()
        if self.screensync.enhanced:
            self.chk_enhanced_rendering.select()
        else:
            self.chk_enhanced_rendering.deselect()
        self.change_mode()

    def start(self):
        self.screensync.load()
        self.update_gui()
        if self.screensync.start_in_tray:
            self.minimize_to_tray()
        try:
            self.mainloop()
        except:
            sys.exit()