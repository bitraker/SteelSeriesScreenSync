import json
import sys
import requests
import os

from win32api import GetSystemMetrics

from PIL.Image import Image
from PIL import ImageGrab
import win32api
from tools import BitmapFader, Mapping, trypass
from time import sleep
import numpy as np

win32api.EnumDisplaySettings()

class ScreenSync:

    def __init__(self, logger, speed: int = None, brightness: int = None, low_light: bool = None, tolerance: int = None, fade: bool = None, keyboard: dict = None, enhanced: bool = None, sample: dict = None):
        self.logger = logger
        self.coreprops_path = ""
        self.load_config()
        self.coreprops = self.read_coreprops(self.coreprops_path)

        self.sample = sample or {
            'x': 0,
            'y': 0,
            'width': GetSystemMetrics(0),
            'height': GetSystemMetrics(1)
        }

        self.brightness = brightness or 100
        self.speed = speed or 100
        self.low_light = low_light or False
        self.tolerance = tolerance or 50
        self.fade = fade or False
        self.enhanced = enhanced or False
        self.presets = {"smooth":{"speed":8,"fade":True,"brightness":100},
                        "responsive":{"speed":24,"fade":True,"brightness":100},
                        "fast":{"speed":100,"fade":False,"brightness":100}}
        self.keyboard = keyboard or {'width': 22, 'height': 6}

        self.mapping = Mapping(self.sample, grid=self.keyboard)
        self.bf = BitmapFader()

        self.dark_mode = True
        self.start_in_tray = False
        self.running = False

        self.keyboard_bound = False
        self.mouse_bound = False
        self.pad_top_bound = False
        self.pad_bot_bound = False
        self.failed_bind_attempts = 0

    def update_sample_area(self, x, y, width, height):
        self.sample = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }

        self.mapping.update_sample_area(x, y, width, height)

    def update_keyboard(self, width, height):
        self.keyboard = {
            'width': width,
            'height': height
        }

        self.mapping.update_grid(width, height)

    def save(self):
        try:
            with open("settings.json", "w") as s:
                s.write(json.dumps({
                    "options": {
                        "speed": self.speed,
                        "fade": self.fade,
                        "enhanced": self.enhanced,
                        "brightness": self.brightness,
                        "low_light": self.low_light,
                        "tolerance": self.tolerance,
                        "enhanced": self.enhanced,
                        "sample": self.sample,
                        "keyboard": self.keyboard
                    },
                    "dark_mode": self.dark_mode,
                    "start_in_tray": self.start_in_tray
                }))
        except Exception as e:
            self.logger.error(f"Error when saving setting: {e}")

    def configure(self, speed: int = None, brightness: int = None, low_light: bool = None, tolerance: int = None, fade: bool = None, keyboard: dict = None, enhanced: bool = None, sample: dict = None, **kwargs):
        if low_light is not None and low_light != self.low_light:
            self.low_light = low_light

        self.low_light = low_light if low_light is not None else self.low_light
        self.enhanced = enhanced if enhanced is not None else self.enhanced
        self.fade = fade if fade is not None else self.fade
        self.tolerance = tolerance or self.tolerance

        if keyboard is not None and keyboard != self.keyboard:
            self.update_keyboard(**keyboard)

        if sample is not None and sample != self.sample:
            self.update_sample_area(**sample)

        if brightness is not None and brightness != self.brightness:
            self.bf.brightness = brightness
            self.brightness = brightness

        if speed is not None and speed != self.speed:
            self.bf.inc = speed
            self.speed = speed

        if kwargs: self.logger.warn("Unknown config settings: " + str(kwargs))

    def load(self):
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as s:
                    settings = json.loads(s.read())
                    if 'options' in settings: self.configure(**settings['options'])

                    if 'dark_mode' in settings:
                        self.dark_mode = settings['dark_mode'] or False

                    if 'start_in_tray' in settings:
                        self.start_in_tray = settings['start_in_tray'] or False

            except Exception as e:
                self.logger.error(f"Error when loading setting: {e}")

    def load_preset(self, preset):
        try:
            self.configure(**self.presets[preset])
        except Exception as e:
            self.logger.error(f"Error when loading preset: {e}")

    def load_config(self):
        try:
            with open("config.json", "r") as c:
                config = json.loads(c.read())
                self.coreprops_path = config["coreprops_path"]
        except Exception as e:
            self.logger.error(f"Error when loading config: {e}")

    def read_coreprops(self, path):
        try:
            with open(path, "r") as c:
                d = json.loads(c.read())
            return d
        except Exception as e:
            self.logger.error(f"Error when loading coreprops: {e}")
            self.running = False

    def register_game(self):
        try:
            """Registers this application to Engine."""
            endpoint = f'http://{self.coreprops["address"]}/game_metadata'
            payload = {
                "game" : "SCREEN_COLOR_SYNC",
                "game_display_name" : "Screen Color Sync",
                "developer" : "Peter Glad (Bitraker)"
            }
            requests.post(endpoint, json=payload)
        except Exception as e:
            self.logger.error(f"Error when registering game with SteelSeries API: {e}")
            self.running = False

    def remove_game(self):
        try:
            """Removes this application to Engine."""
            endpoint = f'http://{self.coreprops["address"]}/remove_game'
            payload = {
                "game" : "SCREEN_COLOR_SYNC"
            }
            requests.post(endpoint, json=payload)
        except Exception as e:
            self.logger.error(f"Error when removing game from SteelSeries API: {e}")

    def bind_keyboard(self):
        """Binds a lighting event to Engine."""
        try:
            endpoint = f'http://{self.coreprops["address"]}/bind_game_event'
            payload = {
                "game" : "SCREEN_COLOR_SYNC",
                "event": 'BITMAP_EVENT',
                "value_optional": r'"true"',
                "handlers": [
                    {
                        "device-type": "rgb-per-key-zones",
                        "zone": "all",
                        "mode": "bitmap"
                    }
                ]
            }
            r = requests.post(endpoint, json=payload)
            if not r.status_code == 200:
                self.logger.warning(f"bind_keyboard got status code {r.status_code} and {r.text}")
                return False
            else:
                self.logger.info(f"bind_keyboard succeeded")
                return True
        except Exception as e:
            self.logger.error(f"Error when binding keyboard: {e}")
            self.remove_keyboard()
            return False

    @trypass
    def remove_keyboard(self):
        self.logger.info("removing keyboard binding")
        endpoint = f'http://{self.coreprops["address"]}/remove_game_event'
        payload = {
            "game" : "SCREEN_COLOR_SYNC",
            "event": 'BITMAP_EVENT'
        }
        r = requests.post(endpoint, json=payload)
        if r.status_code == 200:
            self.keyboard_bound = False
        else:
            self.logger.warning(f"remove_keyboard got status code {r.status_code} and {r.text}")


    def bind_mouse(self):
        """Binds a lighting event to Engine."""
        try:
            endpoint = f'http://{self.coreprops["address"]}/bind_game_event'
            payload = {
                "game" : "SCREEN_COLOR_SYNC",
                "event": 'MOUSE_COLOR',
                "value_optional": r'"true"',
                "handlers": [
                    {
                        "device-type": "mouse",
                        "zone": "all",
                        "color": {"red": 0, "green": 0, "blue": 0},
                        "mode": "context-color",
                        "context-frame-key": "color"
                    }
                ]
            }
            r = requests.post(endpoint, json=payload)
            if not r.status_code == 200:
                self.logger.warning(f"bind_mouse got status code {r.status_code} and {r.text}")
                return False
            else:
                self.logger.info(f"bind_mouse succeeded")
                return True
        except Exception as e:
            self.logger.error(f"Error when binding mouse: {e}")
            self.remove_mouse()
            return False

    @trypass
    def remove_mouse(self):
        self.logger.info("removing mouse binding")
        endpoint = f'http://{self.coreprops["address"]}/remove_game_event'
        payload = {
            "game" : "SCREEN_COLOR_SYNC",
            "event": 'MOUSE_COLOR'
        }
        r = requests.post(endpoint, json=payload)
        if r.status_code == 200:
            self.mouse_bound = False
        else:
            self.logger.warning(f"remove_mouse got status code {r.status_code} and {r.text}")

    def bind_pad_bot(self):
        """Binds a lighting event to Engine."""
        try:
            endpoint = f'http://{self.coreprops["address"]}/bind_game_event'
            payload = {
                "game" : "SCREEN_COLOR_SYNC",
                "event": 'PAD_COLOR_BOT',
                "value_optional": r'"true"',
                "handlers": [
                    {
                        "device-type": "rgb-2-zone",
                        "zone": "one",
                        "color": {"red": 0, "green": 0, "blue": 0},
                        "mode": "context-color",
                        "context-frame-key": "color"
                    }
                ]
            }
            r = requests.post(endpoint, json=payload)
            if not r.status_code == 200:
                self.logger.warning(f"bind_pad_bot got status code {r.status_code} and {r.text}")
                return False
            else:
                self.logger.info(f"bind_pad_bot succeeded")
                return True
        except Exception as e:
            self.logger.error(f"Error when binding pad bot: {e}")
            self.remove_pad_bot()
            return False

    @trypass
    def remove_pad_bot(self):
        self.logger.info("removing pad bot binding")
        endpoint = f'http://{self.coreprops["address"]}/remove_game_event'
        payload = {
            "game" : "SCREEN_COLOR_SYNC",
            "event": 'PAD_COLOR_BOT'
        }
        r = requests.post(endpoint, json=payload)
        if r.status_code == 200:
            self.pad_bot_bound = False
        else:
            self.logger.warning(f"remove_pad_bot got status code {r.status_code} and {r.text}")

    def bind_pad_top(self):
        """Binds a lighting event to Engine."""
        try:
            endpoint = f'http://{self.coreprops["address"]}/bind_game_event'
            payload = {
                "game" : "SCREEN_COLOR_SYNC",
                "event": 'PAD_COLOR_TOP',
                "value_optional": r'"true"',
                "handlers": [
                    {
                        "device-type": "rgb-2-zone",
                        "zone": "two",
                        "color": {"red": 0, "green": 0, "blue": 0},
                        "mode": "context-color",
                        "context-frame-key": "color"
                    }
                ]
            }
            r = requests.post(endpoint, json=payload)
            if not r.status_code == 200:
                self.logger.warning(f"bind_pad_top got status code {r.status_code} and {r.text}")
                return False
            else:
                self.logger.info(f"bind_pad_top succeeded")
                return True
        except Exception as e:
            self.logger.error(f"Error when binding pad top: {e}")
            self.remove_pad_top()
            return False

    @trypass
    def remove_pad_top(self):
        self.logger.info("removing pad top binding")
        endpoint = f'http://{self.coreprops["address"]}/remove_game_event'
        payload = {
            "game" : "SCREEN_COLOR_SYNC",
            "event": 'PAD_COLOR_TOP'
        }
        r = requests.post(endpoint, json=payload)
        if r.status_code == 200:
            self.pad_top_bound = False
        else:
            self.logger.warning(f"remove_pad_top got status code {r.status_code} and {r.text}")

    @trypass
    def send_keyboard_event(self, frame):
        endpoint = f'http://{self.coreprops["address"]}/game_event'
        payload = {
                    "game": "SCREEN_COLOR_SYNC",
                    "event": 'BITMAP_EVENT',
                    "data" : {
                        "value" : 100,
                        "frame" : {
                            "bitmap" : frame
                        }
                    }
                }
        r = requests.post(endpoint, json=payload)
        if not r.status_code == 200:
            self.logger.warning(f"send_keyboard_event got status code {r.status_code} and {r.text}")

    @trypass
    def send_pad_event_bot(self, color):
        endpoint = f'http://{self.coreprops["address"]}/game_event'
        payload = {
                    "game": "SCREEN_COLOR_SYNC",
                    "event": 'PAD_COLOR_BOT',
                    "data" : {
                        "frame": {
                            "color": color
                            }}}
        r = requests.post(endpoint, json=payload)
        if not r.status_code == 200:
            self.logger.warning(f"send_pad_event_bot got status code {r.status_code} and {r.text}")

    @trypass
    def send_pad_event_top(self, color):
        endpoint = f'http://{self.coreprops["address"]}/game_event'
        payload = {
                    "game": "SCREEN_COLOR_SYNC",
                    "event": 'PAD_COLOR_TOP',
                    "data" : {
                        "frame": {
                            "color": color
                            }}}
        r = requests.post(endpoint, json=payload)
        if not r.status_code == 200:
            self.logger.warning(f"send_pad_event_top got status code {r.status_code} and {r.text}")

    @trypass
    def send_mouse_event(self, color):
        endpoint = f'http://{self.coreprops["address"]}/game_event'
        payload = {
                    "game": "SCREEN_COLOR_SYNC",
                    "event": 'MOUSE_COLOR',
                    "data" : {
                        "frame": {
                            "color": color
                            }}}
        r = requests.post(endpoint, json=payload)
        if not r.status_code == 200:
            self.logger.warning(f"send_mouse_event got status code {r.status_code} and {r.text}")

    def bind_all(self):
        self.logger.info(f"attempting to bind all devices")
        self.keyboard_bound = self.bind_keyboard()
        self.mouse_bound = self.bind_mouse()
        self.pad_top_bound = self.bind_pad_top()
        self.pad_bot_bound = self.bind_pad_bot()

    def apply_mapping(self, image: Image):
        return [np.mean(np.asarray(image.crop(region[2:])), axis=(0, 1)).astype(int).tolist() for region in self.mapping.sample_grid] if self.enhanced else [image.getpixel(region[:2]) for region in self.mapping.sample_grid]

    def apply_low_light(self, colors):
        tolerance = 128 * (self.tolerance / 100.)
        for i, color in enumerate(colors):
            if sum(color) == 0:
                colors[i] = [tolerance for _ in range(3)]
            elif sum(color) // 3 < tolerance:
                upscale = tolerance / (sum(color) / 3.)
                colors[i] = list(map(lambda c: min(int(c * upscale), 255), iter(color)))
        return colors

    def run(self):
        if self.failed_bind_attempts > 0:
            self.logger.info(f"relaxing SteelSeries API by waiting for {self.failed_bind_attempts * 5} seconds")
            sleep(self.failed_bind_attempts * 5)
            if self.failed_bind_attempts > 5:
                self.failed_bind_attempts = 0
        self.register_game()
        self.bind_all()
        self.running = True

        while self.running:
            try:

                if not True in [self.keyboard_bound, self.mouse_bound, self.pad_top_bound, self.pad_bot_bound]:
                    self.logger.warning("no devices are bound, attempting to remove app from SteelSeries and re-register")
                    self.failed_bind_attempts += 1
                    self.remove_game()
                    self.logger.info("restarting ..")
                    self.run()

                # GET SCREEN IMAGE
                try:
                    image = ImageGrab.grab(self.mapping.get_bbox())
                except:
                    continue

                # USE SAMPLE_POINTS X,Y TO SELECT COLORS FROM SCREEN IMAGE
                sampled_colors = []
                try:
                        sampled_colors = self.apply_mapping(image)

                        # ENFORCING BASE_COLOR, SETS A MINIMUM COLOR OF BUTTONS
                        # THIS IS GOOD IF YOU ALWAYS WANT SOME LIGHT IN YOUR KEYS
                        if self.low_light:
                            sampled_colors = self.apply_low_light(sampled_colors)

                        self.bf.update(sampled_colors)
                except Exception as e:
                    self.logger.error(f"Error working with sample points: {e}")
                    continue

                if self.keyboard_bound:
                    if self.fade:
                        self.send_keyboard_event(self.bf.current_colors)
                        last = self.bf.current_colors[len(self.bf.current_colors)-1]
                        mid_bot = self.bf.current_colors[len(sampled_colors) - (self.keyboard['width'] // 2) - (22 % self.keyboard['width'])]
                        mid_top = self.bf.current_colors[self.keyboard['width'] // 2]
                    else:
                        self.send_keyboard_event(sampled_colors)
                        last = sampled_colors[len(sampled_colors)-1]
                        mid_bot = sampled_colors[len(sampled_colors) - (self.keyboard['width'] // 2) - (22 % self.keyboard['width'])]
                        mid_top = sampled_colors[self.keyboard['width'] // 2]

                if self.mouse_bound:
                    self.send_mouse_event({"red":last[0], "green":last[1], "blue":last[2]})

                if self.pad_top_bound and self.pad_bot_bound:
                    self.send_pad_event_top({"red":mid_top[0], "green":mid_top[1], "blue":mid_top[2]})
                    self.send_pad_event_bot({"red":mid_bot[0], "green":mid_bot[1], "blue":mid_bot[2]})

                sleep(0.005)

            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.remove_game()
                sleep(10)
                self.run()

        self.remove_game()
        sys.exit()