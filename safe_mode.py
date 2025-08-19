"""Safe mode test - minimal code to verify CircuitPython is working."""
import time
import board

print("=" * 40)
print("SAFE MODE - CircuitPython is working")
print("=" * 40)
print(f"Board: {board.board_id}")

# Try to blink the LED to show we're alive
try:
    import digitalio
    led = digitalio.DigitalInOut(board.LED)
    led.direction = digitalio.Direction.OUTPUT
    
    print("Blinking LED...")
    for i in range(10):
        led.value = not led.value
        time.sleep(0.5)
        print(f"Blink {i+1}/10")
except:
    print("No LED found, but CircuitPython is running")

print("\nCircuitPython is working correctly!")
print("You can now copy the main code files.")
print("\nTo exit safe mode, rename this file and")
print("copy the real code.py to the device.")