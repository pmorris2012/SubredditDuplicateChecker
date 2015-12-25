from PIL import Image
import numpy as np
from scipy.fftpack import dct
from math import sqrt, ceil

'''
copied from https://github.com/JohannesBuchner/imagehash

img - a PIL Image object
bits - the desired bit length of the hash (64, 256, 1024, etc)
'''
def pHash(img, bits):
    size = int(ceil(sqrt(bits)) * 4)
    img = img.convert("L")
    img = img.resize((size, size), Image.ANTIALIAS)
    pixels = np.array(img.getdata(), dtype=np.float)
    pixels = pixels.reshape((size, size))
    transform = dct(dct(pixels, axis = 0), axis = 1)
    low = transform[:size / 4, :size / 4]
    median = np.median(low)
    difference = (low > median).flatten()
    hash = 0
    for (bit, i) in zip(difference, xrange(len(difference))):
        hash += bit * 2**i
    return hash