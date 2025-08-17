"""Boot configuration for Chatpad KMK."""
import storage
import supervisor
import usb_cdc

# Enable serial console for debugging
usb_cdc.enable(console=True, data=False)

# Increase stack for deeper call stacks
supervisor.set_next_stack_limit(4096)

# Keep storage writable during development
storage.remount("/", readonly=False)