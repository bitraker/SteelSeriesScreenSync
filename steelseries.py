import time
import json
import sys
import requests

from PIL import ImageGrab
from win32api import GetSystemMetrics
from tools import BitmapFader, Screen, trypass

class ScreenSync:

    def __init__(self, logger):
        self.logger = logger
        self.coreprops_path = ""
        self.load_config()
        self.coreprops = self.read_coreprops(self.coreprops_path)
        self.screen = Screen()
        self.base_color = [50,50,50]
        self.base_color_tolerance = 50
        self.base_color_enforce = False
        self.bf = BitmapFader()
        self.running = False
        self.fading = False
        self.dark_mode = True
        self.start_in_tray = False
        self.presets = {"smooth":{"speed":8,"fade":True,"brightness":100},
                        "responsive":{"speed":24,"fade":True,"brightness":100},
                        "fast":{"speed":100,"fade":False,"brightness":100}}
        self.keyboard_bound = False
        self.mouse_bound = False
        self.pad_top_bound = False
        self.pad_bot_bound = False
        self.failed_bind_attempts = 0

    def save(self):
        try:
            with open("settings.json", "w") as s:
                s.write(json.dumps({"speed":self.bf.inc,
                                    "fade":self.fading,
                                    "brightness":self.bf.brightness,
                                    "low_light":self.base_color_tolerance,
                                    "low_light_enabled":self.base_color_enforce,
                                    "dark_mode":self.dark_mode,
                                    "start_in_tray":self.start_in_tray}))
        except:
            self.logger.exception()

    def load(self):
        try:
            with open("settings.json", "r") as s:
                settings = json.loads(s.read())
                self.bf.inc = settings["speed"]
                self.bf.brightness = settings["brightness"]
                self.fading = settings["fade"]
                self.base_color_tolerance = settings["low_light"]
                self.base_color = [self.base_color_tolerance,self.base_color_tolerance,self.base_color_tolerance]
                self.base_color_enforce = settings["low_light_enabled"]
                self.dark_mode = settings["dark_mode"]
                self.start_in_tray = settings["start_in_tray"]
        except:
            self.logger.exception()

    def load_preset(self, preset):
        try:
            self.bf.inc = self.presets[preset]["speed"]
            self.fading = self.presets[preset]["fade"]
            self.bf.brightness = self.presets[preset]["brightness"]
        except:
            self.logger.exception()

    def load_config(self):
        try:
            with open("config.json", "r") as c:
                config = json.loads(c.read())
                self.coreprops_path = config["coreprops_path"]
        except:
            self.logger.exception()

    def read_coreprops(self, path):
        try:
            with open(path, "r") as c:
                d = json.loads(c.read())
            return d
        except:
            self.logger.error("unable to read coreprops file")
            self.logger.exception()
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
        except:
            self.logger.error("failed registering game")
            self.logger.exception()
            self.running = False

    def remove_game(self):
        try:
            """Removes this application to Engine."""
            endpoint = f'http://{self.coreprops["address"]}/remove_game'
            payload = {
                "game" : "SCREEN_COLOR_SYNC"
            }
            requests.post(endpoint, json=payload)
        except:
            self.logger.error("failed removing game")
            self.logger.exception()

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
        except:
            self.logger.exception()
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
        except:
            self.logger.exception()
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
        except:
            self.logger.exception()
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
        except:
            self.logger.exception()
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

    def run(self):
        if self.failed_bind_attempts > 0:
            self.logger.info(f"relaxing SteelSeries API by waiting for {self.failed_bind_attempts * 5} seconds")
            time.sleep(self.failed_bind_attempts * 5)
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
                image = ImageGrab.grab()

                # USE SAMPLE_POINTS X,Y TO SELECT COLORS FROM SCREEN IMAGE
                sampled_colors = []
                for row in self.screen.sample_points:
                    try:
                        for sp in row:
                            clr = image.getpixel((sp[0],sp[1]))

                            # ENFORCING BASE_COLOR, SETS A MINIMUM COLOR OF BUTTONS
                            # THIS IS GOOD IF YOU ALWAYS WANT SOME LIGHT IN YOUR KEYS
                            if self.base_color_enforce:
                                if clr[0] < self.base_color_tolerance and \
                                clr[1] < self.base_color_tolerance and \
                                clr[2] < self.base_color_tolerance:
                                    sampled_colors.append(self.base_color)
                                else:
                                    sampled_colors.append([clr[0],clr[1],clr[2]])
                            else:
                                sampled_colors.append([clr[0],clr[1],clr[2]])
                    except:
                        self.logger.exception()
                self.bf.update(sampled_colors)

                if self.keyboard_bound:
                    if self.fading:
                        self.send_keyboard_event(self.bf.current_colors)
                        last = self.bf.current_colors[len(self.bf.current_colors)-1]
                        mid_bot = self.bf.current_colors[len(self.bf.current_colors)-11]
                        mid_top = self.bf.current_colors[11]
                    else:
                        self.send_keyboard_event(sampled_colors)
                        last = sampled_colors[len(sampled_colors)-1]
                        mid_bot = sampled_colors[len(sampled_colors)-11]
                        mid_top = sampled_colors[11]

                if self.mouse_bound:
                    self.send_mouse_event({"red":last[0], "green":last[1], "blue":last[2]})

                if self.pad_top_bound and self.pad_bot_bound:
                    self.send_pad_event_top({"red":mid_top[0], "green":mid_top[1], "blue":mid_top[2]})
                    self.send_pad_event_bot({"red":mid_bot[0], "green":mid_bot[1], "blue":mid_bot[2]})

                time.sleep(0.005)

            except:
                self.logger.exception()
                self.remove_game()
                sys.exit()

        self.remove_game()
        sys.exit()