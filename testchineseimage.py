from PIL import Image, ImageDraw, ImageFont

# Create a blank image
image = Image.new('RGB', (200, 60), color=(255, 255, 255))
draw = ImageDraw.Draw(image)

# Use the downloaded Noto Sans CJK SC font
font = ImageFont.truetype('NotoSans-Thin.ttf', 30)  # Update path and filename as necessary

# Draw text
draw.text((10, 10), '测试中文', fill=(0, 0, 0), font=font)

# Save and view
image.save('test_chinese.jpg')
image.show()
