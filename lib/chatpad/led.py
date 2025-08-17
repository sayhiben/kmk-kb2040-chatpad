"""NeoPixel status LED helper."""
from config import NEOPIXEL_PIN, NEOPIXEL_BRIGHTNESS, Colors
try:
    import neopixel
    LED_OK = NEOPIXEL_PIN is not None
except Exception:
    LED_OK = False

class StatusLED:
    def __init__(self):
        self.enabled = LED_OK
        self.color = Colors.OFF
        if self.enabled:
            self.px = neopixel.NeoPixel(NEOPIXEL_PIN, 1, brightness=NEOPIXEL_BRIGHTNESS, auto_write=True)
            self.px[0] = Colors.BASE

    def set(self, rgb):
        if not self.enabled:
            return
        self.color = rgb
        self.px[0] = rgb

    def update_for(self, modifiers):
        if not self.enabled:
            return
        if modifiers.people_toggle:
            self.set(Colors.PEOPLE)
        elif modifiers.green_active:
            self.set(Colors.GREEN)
        elif modifiers.orange_active:
            self.set(Colors.ORANGE)
        elif modifiers.shift_active:
            self.set(Colors.SHIFT)
        else:
            self.set(Colors.BASE)

    def heartbeat(self):
        # very fast blink without delay by immediate restore
        if not self.enabled:
            return
        saved = self.color
        self.px[0] = Colors.HEARTBEAT
        self.px[0] = saved

    def error(self):
        self.set(Colors.ERROR)