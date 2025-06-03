from waveshare_epd import epd1in54_V2
from PIL import Image, ImageDraw, ImageFont
import time

epd = epd1in54_V2.EPD()
epd.init()
epd.Clear(0xFF)

font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 24)
image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)

draw.text((10, 40), "Hello ePaper!", font=font, fill=0)
epd.display(epd.getbuffer(image))

time.sleep(5)
epd.Clear(0xFF)