# -*- coding: utf-8 -*-
import cv2
from skimage.feature import hog
from PIL import Image

print('[INFO]...All Libraries are imported correctly ')

scale = 10
filename = 'images/wahbi yaakoub.jpg'

print('[INFO]...Image Treatment on ' + filename)


def generate_hog(file_name):
    im = cv2.imread(file_name)
    gr = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    image = 255 - gr
    print(image)
    fd, hog_image = hog(image, orientations=8, pixels_per_cell=(16, 16), cells_per_block=(1, 1), visualize=True)
    return hog_image


def save_hog(file_name, hog_image):
    name = file_name[:-4] + "__HOG.png"
    img = Image.fromarray(hog_image * scale).convert('L')
    img.save(name)
    print("[INFO]...Picture Saved as " + name)


img_hog = generate_hog(filename)
save_hog("hog.png", img_hog)

print('[INFO]...Done')
