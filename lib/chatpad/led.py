"""NeoPixel status LED helper with pulsing layer indication."""
from config import NEOPIXEL_PIN, NEOPIXEL_BRIGHTNESS, Colors
from time import monotonic
import math

try:
    import neopixel
    LED_OK = NEOPIXEL_PIN is not None
except Exception:
    LED_OK = False

class StatusLED:
    def __init__(self):
        self.enabled = LED_OK
        self.base_color = Colors.BASE
        self.current_layer_color = Colors.BASE
        self.pulse_phase = 0
        self.last_update = monotonic()
        if self.enabled:
            self.px = neopixel.NeoPixel(NEOPIXEL_PIN, 1, brightness=NEOPIXEL_BRIGHTNESS, auto_write=False)
            self.px[0] = Colors.BASE
            self.px.show()

    def set(self, rgb):
        if not self.enabled:
            return
        self.base_color = rgb
        self.current_layer_color = rgb

    def update_for(self, modifiers):
        if not self.enabled:
            return
        
        # Determine base color from layer
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
        
        # Apply pulsing effect
        self.pulse()

    def pulse(self):
        """Create a pulsing effect for current layer color."""
        if not self.enabled:
            return
        
        now = monotonic()
        dt = now - self.last_update
        self.last_update = now
        
        # Update pulse phase (0 to 2*pi over 2 seconds)
        self.pulse_phase += dt * math.pi  # Full cycle in 2 seconds
        if self.pulse_phase > 2 * math.pi:
            self.pulse_phase -= 2 * math.pi
        
        # Calculate brightness multiplier (0.3 to 1.0)
        brightness = 0.65 + 0.35 * math.sin(self.pulse_phase)
        
        # Apply brightness to current color
        r, g, b = self.current_layer_color
        self.px[0] = (int(r * brightness), int(g * brightness), int(b * brightness))
        self.px.show()
    
    def heartbeat(self):
        # Keep for compatibility, but pulsing replaces this
        self.pulse()

    def error(self):
        if not self.enabled:
            return
        self.px[0] = Colors.ERROR
        self.px.show()