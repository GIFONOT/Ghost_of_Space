from PIL import Image
from Presets import img_dir
from colorthief import ColorThief


def ge_col(png):
    #color_thief = ColorThief(png)
    # get the dominant color
    color_thief = png
    #dominant_color = color_thief.get_color(quality=1)
    palette = color_thief.get_palette(color_count=2)
    return palette

'''def compute_average_image_color(img):
    width, height = img.size

    r_total = 0
    g_total = 0
    b_total = 0

    count = 0
    ListCol = {}
    for x in range(0, width):
        for y in range(0, height):
            r, g, b, a = img.getpixel((x, y))
            if r != 0 and g != 0 and b != 0:
                if (r + g + b) in ListCol:
                    ListCol[r + g + b] = []
                    ListCol[r + g + b] = ListCol[r + g + b].append((r + g + b))
                else:
                    ListCol[r + g + b] = []
                    ListCol[r + g + b] = ListCol[r + g + b].append((r + g + b))

                r_total += r
                g_total += g
                b_total += b
                count += 1

    # return r_total / count, g_total / count, b_total / count, count
    return ListCol, count


img = Image.open('Png/ino5.png')
#img = img.resize((50, 50))  # Small optimization
average_color = compute_average_image_color(img)
print(average_color)'''
