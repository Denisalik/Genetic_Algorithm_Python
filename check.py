import numpy as np
from PIL import Image
import cairo
import sys
import matplotlib.pyplot as plt


def fitness_f(default, img):
    if img is None:
        return img
    diff = np.array(img.get_data(), dtype=np.uint8).reshape(512, 512, 4) - default
    #return 1 - np.sum(np.absolute(diff), dtype=np.uint64)/255/512/4/512
    return np.sum(np.absolute(diff), dtype=np.uint64)/1_000_000#/255/512/3/512


def get_img(index):
    path = f"samples/art{index}.png"
    try:

        arr = np.array(Image.open(path, mode='r').convert("RGBA"), dtype=np.uint8)
        arr2 = from_np_to_cairo(arr)
        return arr2
    except Exception:
        return None


def from_np_to_cairo(arr):
    return cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_ARGB32, 512, 512)


def plot():
    x = []
    for j in range(len(arr)):
        x.append(j)
    plt.plot(x, arr)
    plt.show()

t = 10
n = t if len(sys.argv) == 1 else sys.argv[1]
default = np.array(Image.open("samples/image.jpg", mode='r').convert("RGBA"), dtype=np.uint8)
arr = []
for i in range(int(n)+1):
    img = get_img(i)
    score = fitness_f(default=default, img=img)
    if score is not None:
        arr.append(score)
    print(score)
if len(sys.argv) == 3:
    plot()
"cd study\python\dbs"
"venv\Scripts\activate.bat"
"python check.py"
