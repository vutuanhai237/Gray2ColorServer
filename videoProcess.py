import cv2
from PIL import Image
import os, glob
import moviepy.video.io.ImageSequenceClip
import shutil
from os import path
import numpy as np
def video2Images(pathOfVideo, folder):
    vidcap = cv2.VideoCapture(pathOfVideo)
    success, image = vidcap.read()
    count = 0
    while success:
        cv2.imwrite(folder + '/frame%d.png' % count, image)
        success, image = vidcap.read()
        count += 1


def centeringAndSave(folder):
    for file in os.listdir(folder):
        img = Image.open(folder + '/' + file)
        print(file)
        crop = img
        width, height = img.size   # Get dimensions
        new_height, new_width = 0, 0
        flag = 0
        if width > height:
            new_height = height
            new_width = height
        else:
            if width < height:
                new_height = width
                new_width = width
            else:
                flag = 1

        left = (width - new_width)/2
        top = (height - new_height)/2
        right = (width + new_width)/2
        bottom = (height + new_height)/2

        # Crop the center of the image
        if flag == 0:
            img = img.crop((left, top, right, bottom))
            img = img.save(folder + '/' + file[0:len(file)-4] + '.png')
def resizeAllFile(folder):
    dim = (256,256)
    for file in os.listdir(folder):
        img = cv2.imread(folder + '/' + file)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_CUBIC)
        cv2.imwrite(folder + '/' + file, img)

def getConcat(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def concatPairImage(folder, saveFolder):
    lists = glob.glob(folder + '/*.png')
    if (path.exists('results/concat')):
        shutil.rmtree('results/concat', ignore_errors=True)
    os.makedirs(saveFolder + '/concat')
    subList = [lists[n:n+3] for n in range(0, len(lists), 3)]
    for files in subList:
        fake = Image.open(files[0])
        real = Image.open(files[1])
        number = int(((files[0].split('\\'))[-1])[5:-11])
        index = ''
        if number < 10:
            index = '00' + str(number)
        elif number < 100:
            index = '0' + str(number)
        else:
            index = str(number)
        getConcat(real, fake).save(saveFolder + '/concat/' + index + '.png')


def images2Video(folder, FPS, videoName):
    image_folder = folder
    image_files = [
        image_folder + "/" + img for img in os.listdir(image_folder) if img.endswith(".png")
    ]
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps = FPS)
    clip.write_videofile('video.mp4')

def duplicate(folder):
    for file in os.listdir(folder):
        img = cv2.imread(folder + '/' + file)
        vis = np.concatenate((img, img), axis=1)
        cv2.imwrite(folder + '/' + file, vis)

images2Video('results/concat', 30, 'video')