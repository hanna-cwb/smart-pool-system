from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd1in54_V2

epd = epd1in54_V2.EPD()
epd.init(isPartial=False)
epd.Clear(0xFF)

image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)
font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 24)
draw.text((10, 40), "Direktanzeige", font=font, fill=0)

epd.display(epd.getbuffer(image))
