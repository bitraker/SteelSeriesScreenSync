import tkinter
import tkinter.messagebox
import customtkinter

from functools import partial

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")


class ScreenSyncApp(customtkinter.CTk):

    def __init__(self, screensync, logger):
        super().__init__()
        self.WIDTH = 600
        self.HEIGHT = 250
        self.screensync = screensync
        self.logger = logger
        self.dark_mode = True

        # SETUP
        self.title("Bitraker - SteelSeries Screen Sync")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # FRAME
        self.frame = customtkinter.CTkFrame(master=self,corner_radius=5)
        self.frame.grid(row=0, column=0, sticky="nswe")
        self.frame.grid_rowconfigure(0, minsize=10)

        # SWITCHES
        self.sw_dark_mode = customtkinter.CTkSwitch(master=self.frame,
                                                text="Dark Mode",
                                                command=self.change_mode)
        self.sw_dark_mode.grid(row=10, column=0, pady=10, padx=20, sticky="w")
        self.sw_dark_mode.select()

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

        self.slider_speed.set(10)
        self.slider_brightness.set(100)

        # CHECK BOXES
        self.chk_low_light = customtkinter.CTkCheckBox(master=self.frame,
                                                      text="Low Light", command=self.toggle_low_light)
        self.chk_low_light.grid(row=6, column=0, pady=10, padx=20, sticky="w")

        self.chk_fade_effect = customtkinter.CTkCheckBox(master=self.frame,
                                                     text="Fade Effect", command=self.toggle_fading)
        self.chk_fade_effect.grid(row=6, column=1, pady=10, padx=20, sticky="w")
        self.chk_fade_effect.select()

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

        self.btn_preset_responsive = customtkinter.CTkButton(master=self.frame,
                                                       height=25,
                                                       text="Fast",
                                                       command=partial(self.change_preset, "fast"))
        self.btn_preset_responsive.grid(row=2, column=3, columnspan=1, pady=10, padx=20, sticky="we")


    def toggle_fading(self):
        if self.chk_fade_effect.check_state:
            self.screensync.fading = True
        else:
            self.screensync.fading = False
        
    def toggle_low_light(self):
        if self.chk_low_light.check_state:
            self.screensync.base_color_enforce = True
        else:
            self.screensync.base_color_enforce = False

    def set_fading_speed(self, speed):
        self.lbl_speed.set_text(f"Speed {int(speed)}")
        self.screensync.bf.inc = int(speed)

    def set_brightness(self, brightness):
        self.lbl_brightness.set_text(f"Brightness {int(brightness)}")
        self.screensync.bf.brightness = int(brightness)

    def set_low_light(self, value):
        self.lbl_low_light.set_text(f"Low Light {int(value)}")
        self.screensync.base_color = [int(value),int(value),int(value)]
        self.screensync.base_color_tolerance = int(value)
        
    def change_mode(self):
        if self.sw_dark_mode.get() == 1:
            customtkinter.set_appearance_mode("dark")
            self.screensync.dark_mode = True
        else:
            customtkinter.set_appearance_mode("light")
            self.screensync.dark_mode = False

    def change_preset(self, preset):
        self.screensync.load_preset(preset)
        self.update_gui()

    def on_closing(self, event=0):
        self.screensync.save()
        self.screensync.running = False
        self.destroy()

    def update_gui(self):
        self.lbl_low_light.set_text(f"Low Light {self.screensync.base_color_tolerance}")
        self.slider_low_light.set(self.screensync.base_color_tolerance)
        self.lbl_brightness.set_text(f"Brightness {self.screensync.bf.brightness}")
        self.slider_brightness.set(self.screensync.bf.brightness)
        self.lbl_speed.set_text(f"Speed {self.screensync.bf.inc}")
        self.slider_speed.set(self.screensync.bf.inc)
        if self.screensync.fading:
            self.chk_fade_effect.select()
        else:
            self.chk_fade_effect.deselect()
        if self.screensync.base_color_enforce:
            self.chk_low_light.select()
        else:
            self.chk_low_light.deselect()
        if self.screensync.dark_mode:
            self.sw_dark_mode.select()
        else:
            self.sw_dark_mode.deselect()
        self.change_mode()

    def start(self):
        self.screensync.load()
        self.update_gui()
        self.mainloop()