from PIL import Image
import math
import argparse


# value_charset = [" ",".","~","=","+","x","*","#","%","@"]
value_charset = [" ",".",",","-","~","=","+","x","o","*","0","$","X","#","%","@"]

#        112.5 90 67.5
#   157.5 \    _   /   22.5
# 180 |                |   0
#   202.5 /     _   \   337.5
#        247.5 270  292.5
edge_charset = ["|", "/", "_", "\\", "|", "/", "_", "\\"]


# term colors: "\x1b[32;40m"
# 24bit color: "\x1b[38;2;%d;%d;%dm"
# bolt/bright - print("\x1b[1;31m")
# reset - print("\x1b[0m")
# black 30
# red 31
# green 32
# yellow 33
# blue 34
# magenta 35
# cyan 36
# white 37


# def rgb2hsv(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
#     r = rgb[0] / 255.0
#     g = rgb[1] / 255.0
#     b = rgb[2] / 255.0

#     v = max(r, g, b)
#     c = v - min(r, g, b)
#     if c < 1e-6:
#         h = 0.0
#     else:
#         if v == r:
#             h = 60.0 * (((g - b) / c) % 6)
#             if h < 0.0:
#                 h += 360.0
#         elif v == g:
#             h = 60.0 * (((b - r) / c) + 2)
#         else:  # elif v == b:
#             h = 60.0 * (((r - b) / c) + 4)
#     if v < 1e-6:
#         s = 0.0
#     else:
#         s = c / v
#     return (h, s, v)


def calc_convolution(gs_data: list[float], x: int, y: int, w: int) -> tuple[float, float]:
    z1 = gs_data[(y - 1) * w + x - 1]
    z2 = gs_data[y * w + x - 1]
    z3 = gs_data[(y + 1) * w + x - 1]
    z4 = gs_data[(y - 1) * w + x]
    z6 = gs_data[(y + 1) * w + x]
    z7 = gs_data[(y - 1) * w + x + 1]
    z8 = gs_data[y * w + x + 1]
    z9 = gs_data[(y + 1) * w + x + 1]

    gx = (z7 + 2 * z8 + z9) - (z1 + 2 * z2 + z3)
    gy = (z3 + 2 * z6 + z9) - (z1 + 2 * z4 + z7)
    return (gx, gy)


def calc_sobels(gs_data: list[float], w: int, h: int) -> tuple[list[float], list[float]]:
    sx: list[float] = [0.0 for _ in range(0, h * w)]
    sy: list[float]= [0.0 for _ in range(0, h * w)]
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            sx[y * w + x], sy[y * w + x] = calc_convolution(gs_data, x, y, w)
    return (sx, sy)


def grayscale(img_data: list[tuple[int, int, int]], w: int, h: int) -> list[float]:
    gs: list[float] = []
    for i in range(0, h * w):
        gs.append(0.2126 * img_data[i][0] / 255.0
                    + 0.7152 * img_data[i][1] / 255.0
                    + 0.0722 * img_data[i][2] / 255.0)
    return gs


def main() -> None:
    parser = argparse.ArgumentParser(description="pic2ascii")
    parser.add_argument("filename", type=str, help="picture filename")
    parser.add_argument("-w", type=int, help="width in chars to fit picture [60]", default=60)
    parser.add_argument("-e", type=int, help="height in chars to fit picture [30]", default=30)
    parser.add_argument("-t", type=float, help="edge threshold [1.5]", default=1.5)
    parser.add_argument("-l", help="use lightness instead of value to select char", action="store_true")
    args = parser.parse_args()

    image = Image.open(args.filename)
    # real H / 2
    k = max(image.width / args.w, image.height / 2 / args.e)
    width = int(image.width / k + 0.5)
    height = int(image.height / 2.0 / k + 0.5)
    edge_threshold_square = args.t * args.t
    value_charset_count = len(value_charset)
    print(f"[{width = } {height = }]")
    img_data = list(image.resize((width, height)).getdata())  # list of tuples
    sobel_x, sobel_y = calc_sobels(grayscale(img_data, width, height), width, height)

    for y in range(0, height):
        for x in range(0, width):
            pix_idx = y * width + x
            r, g, b = img_data[pix_idx]
            # h, s, v = rgb2hsv((r,g,b))
            v = (r + g + b) / 765.0 if args.l else max(r, g, b) / 255.0
            sx = sobel_x[pix_idx]
            sy = sobel_y[pix_idx]
            sobel_magnitude_square = sx * sx + sy * sy
            sobel_angle = (math.atan2(sy, sx) * 180.0 / math.pi + 180.0 + 22.5) % 360.0

            print(f"\x1b[38;2;{r};{g};{b}m", end="")
            if sobel_magnitude_square >= edge_threshold_square:
                print(edge_charset[int(sobel_angle / 45.0 + 0.5) - 1], end="")
            else:
                print(value_charset[int(v * value_charset_count - 1)], end="")
        print(" ")
    print("\x1b[0m")


if __name__ == "__main__":
    main()
