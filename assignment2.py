from random import randint
import numpy as np
from math import floor
from PIL import Image
import cairo
from copy import deepcopy
import json

#COLORS is contant that contains all from original image
COLORS = []
#path to the original image
PATH = "samples/image.jpg"
#original image in numpy array format(colors is combination of red, green, blue, alpha)
DEFAULT = np.asarray(Image.open(PATH, mode='r').convert("RGBA"), dtype=np.uint8)


class Organism:
    def __init__(self):
        self.SYMBOLS = "⛾"# symbol to draw to make
        self.img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 512, 512)#blank image
        ctx = cairo.Context(self.img)
        ctx.rectangle(0, 0, 511, 511)#make blank image white
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        self.genes = []#gene contain information about color, coordinate, font size, symbol

    def save_genes(self):#serialization for genes
        with open("samples/genes.json", "w") as write_file:
            json.dump(self.genes, write_file)

    def load_genes(self):#deserialization for genes
        with open("samples/genes.json", "r") as load_file:
            self.genes = json.load(load_file)

    @staticmethod
    def save_colors():#serialization for colors
        global COLORS
        with open("samples/colors.json", "w") as write_file:
            json.dump(COLORS, write_file)

    @staticmethod
    def load_colors():#deserialization for genes
        global COLORS
        with open("samples/colors.json", "r") as load_file:
            COLORS = json.load(load_file)

    def generate_genes(self):
        for i in range(4*4096):
            x = (i % 128) * 4#iteratively fill all surface
            y = (i // 128) * 4#in the end it will look life a net
            coord = (x, y)
            gen = {"color": self.random_color(), "coord": coord,
                   "text": self.SYMBOLS, "font": self.font}
            self.genes.append(gen)

    def get_ctx(self):#context for drawing
        return cairo.Context(self.img)

    def copy(self):#make a copy of organism(it will contain blank image and all genes from initial image)
        org = Organism()
        org.genes = deepcopy(self.genes)
        return org

    def draw(self, setting: dict):#drawing function, it will draw based on setting that contains all information about gen(for the setting details look at generate_genes method)
        ctx = self.get_ctx()
        ctx.select_font_face("SYMBOLA", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)#seting font
        #you need to have SYMBOLA font in your system, but you can choose any font you want if your symbol is in your font
        ctx.set_font_size(setting["font"])#seting fontsize
        x, y = setting["coord"]#seting coordinates
        ctx.move_to(x, y)
        r, g, b, a = setting["color"]#seting colors
        ctx.set_source_rgba(r, g, b, a)
        ctx.show_text(setting["text"])#seting symbol

    def draw_from_genes(self):#if self.img is blank, you need to draw image using this method, beware you need to have self.genes filled with genes
        for g in self.genes:
            self.draw(setting=g)

    @property
    def fitness_f(self):#fitness function is sum of all differences between original and drawed image colors
        global DEFAULT
        diff = np.array(self.img.get_data(), dtype=np.uint8).reshape(512, 512, 4) - DEFAULT
        return np.sum(np.absolute(diff), dtype=np.uint64) / 1_000_000

    def save(self, step):#save image in png format
        self.img.write_to_png(f"samples/art{step}.png")
        self.save_genes()

    @staticmethod
    def random_coord():#getter for coordinates
        x = int(floor((randint(0, 511))/4))*4
        y = int(floor((randint(0, 511))/4))*4
        return x, y

    @property
    def font(self):#getter for font size
        return 4

    @staticmethod
    def random_color():#getter for color
        global COLORS
        # r = lambda: floor(random()*10)/10
        # if rand:
        #    return r(), r(), r(), r()
        color = COLORS[randint(0, len(COLORS) - 1)]
        r = color[0]
        g = color[1]
        b = color[2]
        a = color[3]
        return r, g, b, a

    def mutate_color(self, i):#setter for colors in specific gen in organism
        self.genes[i]["color"] = self.random_color()

    def mutate_gen(self):#function that random which gen should be mutated and mutate it afterwards
        ind = randint(0, len(self.genes) - 1)
        self.mutate_color(ind)

    def mutate(self, n: int = 4):#function that mutate specific number of genes
        for _ in range(n):
            self.mutate_gen()

    @staticmethod
    def write_colors():#function that process original image and extract all possible colors from it
        global DEFAULT, COLORS
        for i in range(DEFAULT.shape[0]):
            for j in range(DEFAULT.shape[1]):
                el = DEFAULT[i][j]/255
                color = [el[0], el[1], el[2], el[3]]
                if color not in COLORS:
                    COLORS.append(color)


class GenerativeAlg:
    def __init__(self, index: int = 1, processing: bool = False, continuation: bool = False):
        #index is number of next image
        #if processing is true, that means program will deserialize colors.json and uses colors from it
        # if continuation is true, that means program will deserialize genes.json and uses genes from it
        self.org = Organism()
        if processing:
            self.org.load_colors()
        else:
            self.org.write_colors()
            self.org.save_colors()
        self.continuation = continuation
        self.index = index
        if continuation:
            self.org.load_genes()
        else:
            self.org.generate_genes()

    def mutation(self, n: int = 1000):
        if not self.continuation:
            self.org.save(self.index - 1)
        for i in range(n):#iteratively do a crossover and save image to the samples folder
            self.crossover()
            self.org.save(self.index+i)
            print(f"step {self.index + i}")

    def crossover(self):
        for i in range(100):
            options = []
            original = self.org.copy()#make a copy of organism
            original.draw_from_genes()#draw image
            options.append(original)#append parent
            for j in range(0, 50):
                copy = self.org.copy()
                copy.mutate()
                copy.draw_from_genes()
                #make a copy, mutate certain genes and, and choose image with best(minimum) fitness value
                options.append(copy)
            self.org = min(*options, key=lambda x: x.fitness_f)


#start processing
image = GenerativeAlg(index=54, continuation=True, processing=True)
image.mutation()
