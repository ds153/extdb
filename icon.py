import Image
import operator
import os

def iconcolorchange(iconpath, color):

	icon = Image.open(iconpath)

	color_origin = sorted(icon.getcolors(), key = lambda t: t[0])[-1][-1]

	color += (255,)

	val_normal = (255, 255, 255, 255)
	val_normal2 = (67, 67, 67, 255)

	gap_1 = tuple(map(operator.truediv, map(operator.sub, val_normal, color), zeroExpect(map(operator.sub, val_normal, color_origin))))
	gap_2 = tuple(map(operator.truediv, map(operator.sub, val_normal2, color), zeroExpect(map(operator.sub, (67, 67, 67, 256), color_origin))))
	pix = icon.load()

	for width in xrange(icon.size[0]):
		for height in xrange(icon.size[1]):
			value = pix[width, height]
			if value[3] == 255 and value != val_normal2 and value != val_normal:
				if value == color_origin:
					icon.putpixel((width, height), color)
				elif width > 4 and width < 27 and height > 5 and height < 26:
					pix[width, height] = tuple(map(operator.sub, val_normal, map(int, map(operator.mul, zeroExpect(map(operator.sub, val_normal, value)), gap_1))))
					icon.putpixel((width, height), pix[width, height])
				else:
					pix[width, height] = tuple(map(operator.sub, val_normal2, map(int, map(operator.mul, zeroExpect(map(operator.sub, val_normal2, value)), gap_2))))
					icon.putpixel((width, height), pix[width, height])

	return icon

def zeroExpect(values):

	for index, value in enumerate(values):
		if value == 0:
			values[index] = 1

	return values

def hex_to_rgb(value):

	value = value.lstrip("#")
	lv = len(value)
	return tuple(int(value[i:i+lv/3], 16) for i in xrange(0, lv, lv/3))


hex_color = "#74c476"
rgb_color = hex_to_rgb(hex_color)

if not os.path.exists("/home/xinbo/sandbox/extremes/static/" + hex_color.lstrip("#")):
	os.mkdir("/home/xinbo/sandbox/extremes/static/" + hex_color.lstrip("#"))

for roots, dirs, names in os.walk("/home/xinbo/sandbox/extremes/static/mapicons"):
	for name in names:
		filepath = os.path.join(roots, name)
		im = iconcolorchange(filepath, rgb_color)
		im.save("/home/xinbo/sandbox/extremes/static/" + hex_color.lstrip("#") + "/" + name)


# im = iconcolorchange("/home/xinbo/number_2.png", (135, 210, 187))
# im.save("/home/xinbo/test_5.png")

