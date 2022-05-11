from win32api import GetSystemMetrics

class BitmapFader:

    """ The BitmapFader's job is to relax color shifting and provide smooth transitions. 

        By providing a desired color (actual colors on screen), the Fader will update
        the current_colors variable in a speed, defined by the inc variable.

        The GUI controls the speed by changing the inc value.
    """

    def __init__(self):
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
        self.inc = 10
        self.brightness = 100
        

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

class Screen:

    """ Contains all screen related functionality.

    Sample points are created on the bottom half of the screen,
    they are used to detect the colors, that will be mapped to the steelseries devices.
    the points are created in a 6x22 matrix, and are singletons, or single pixels measurements,
    this makes the code run fast, instead of having complex calculations. """

    def __init__(self):
        self.width = GetSystemMetrics(0)
        self.height = GetSystemMetrics(1)
        self.sample_points = self._create_sample_points()

    def _create_sample_points(self):
        sample_points = []
        current_x = 0
        current_y = self.height // 2
        v_inc_size = self.height // 12
        h_inc_size = self.width // 22
        for r in range(1,7):
            row = []
            for p in range(0,22):
                row.append([current_x,current_y])
                current_x += h_inc_size
            sample_points.append(row)
            current_y += v_inc_size
            current_x = 0
        return sample_points


def trypass(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            pass
    return wrapper