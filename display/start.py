import time
import st7789
from PIL import Image, ImageDraw, ImageFont

# Initialize the st7789 display
display = st7789.ST7789(
    height=240,
    width=280,
    rotation=0,
    port=0,
    cs=st7789.BG_SPI_CS_FRONT,
    dc=9,
    backlight=19,
    spi_speed_hz=80 * 1000 * 1000,
    offset_left=0,
    offset_top=0,
)

display.begin()

# Get display size
WIDTH = display.width
HEIGHT = display.height

# write text
WIDTH = display.width
HEIGHT = display.height

image = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

draw.text((10, 10), "Hello st7789!", font=font, fill=(255, 255, 0))

display.display(image)

print("Display initialized")

# Keep the display on
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass