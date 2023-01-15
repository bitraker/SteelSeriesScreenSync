class BitmapFader:

    """ The BitmapFader's job is to relax color shifting and provide smooth transitions.

        By providing a desired color (actual colors on screen), the Fader will update
        the current_colors variable in a speed, defined by the inc variable.

        The GUI controls the speed by changing the inc value.
    """

    def __init__(self, speed: int = 10, brightness: int = 100):
        self.current_colors = [
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
            [0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],
        ]
        self.inc = speed
        self.brightness = brightness

    def update(self, desired_colors):

        brightness = self.brightness / 100
        count = 0
        for c in self.current_colors:
            dc = desired_colors[count]
            if c != dc:

                # RED
                if c[0] < dc[0]:
                    c[0] += self.inc
                    if c[0] > dc[0]:
                        c[0] = dc[0]
                elif c[0] > dc[0]:
                    c[0] -= self.inc
                    if c[0] < dc[0]:
                        c[0] = dc[0]

                c[0] = round(c[0] * brightness)

                # GREEN
                if c[1] < dc[1]:
                    c[1] += self.inc
                    if c[1] > dc[1]:
                        c[1] = dc[1]
                elif c[1] > dc[1]:
                    c[1] -= self.inc
                    if c[1] < dc[1]:
                        c[1] = dc[1]

                c[1] = round(c[1] * brightness)

                # BLUE
                if c[2] < dc[2]:
                    c[2] += self.inc
                    if c[2] > dc[2]:
                        c[2] = dc[2]
                elif c[2] > dc[2]:
                    c[2] -= self.inc
                    if c[2] < dc[2]:
                        c[2] = dc[2]

                c[2] = round(c[2] * brightness)

                self.current_colors[count] = c

            count += 1

class Mapping:

    """ Contains all screen related functionality.

    Sample points are created on the bottom half of the screen,
    they are used to detect the colors, that will be mapped to the steelseries devices.
    the points are created in a 6x22 matrix, and are singletons, or single pixels measurements,
    this makes the code run fast, instead of having complex calculations. """

    def __init__(self, sample, grid={'width': 22, 'height':6}):
        self.sample = sample

        self.grid = {
            "width": self.sample["width"] // grid["width"],
            "height": self.sample["height"] // grid["height"]
        }

        self.sample_grid = []
        self._sample_grid()

    def get_bbox(self):
        return tuple((self.sample['x'], self.sample['y'], self.sample['x'] + self.sample['width'], self.sample['y'] + self.sample['height']))

    def update_grid(self, width, height):
        self.grid = {
            "width": width,
            "height": height
        }

        self._sample_grid()

    def update_sample_area(self, x, y, width, height):
        self.sample = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }

        self._sample_grid()

    def update_grid(self, width, height):
        self.grid = {
            'width': self.sample["width"] // width,
            'height': self.sample["height"] // height
        }

        self._sample_grid()

    def _sample_grid(self):
        self.sample_grid = []
        current_x = 0
        current_y = 0
        for r in range(6):
            for p in range(22):
                self.sample_grid.append((current_x + self.grid["width"] // 2, current_y + self.grid["height"] // 2, current_x, current_y, current_x + self.grid["width"], current_y + self.grid["height"]))
                if current_x + self.grid["width"] <= self.sample["width"] - self.grid["width"]:
                    current_x += self.grid["width"]
            if current_y + self.grid["height"] <= self.sample["height"] - self.grid["height"]:
                current_y += self.grid["height"]
            current_x = 0

def trypass(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            pass
    return wrapper