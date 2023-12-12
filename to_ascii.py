from PIL import Image, ImageFilter
import glob
import time
import os
import requests

import cv2

class glob:
    ASCII = None
    COLORIZED = None
RESET = '\033[0m'

def to_ascii(VIEWED, WIDTH, HEIGHT, ISVIDEO, COLORIZED = True, ASCII = True, FPS=2, DEFAULT_CHAR="█", ASCII_DENSITY = "Ñ@#W$9876543210?!abc;:+=-,._"):
    glob.ASCII = ASCII
    glob.COLORIZED = COLORIZED
    """ RUN """
    print("\033[?25h", end="") #hide cursor

    if ISVIDEO:
        vidcap = cv2.VideoCapture(VIEWED)
        
        if not os.path.exists('images'):
            os.makedirs('images')
        
        count = 0
        while True:
            success,image = vidcap.read()
            if not success:
                break
            cv2.imwrite(os.path.join('images',"frame{:d}.jpg".format(count)), image)     # save frame as JPEG file
            count += 1
        
        print("{} images are extacted".format(count))
        path = "images/frame{:d}.jpg".format(0)
        time.sleep(0.3)
        print("\033c", end = "")
        
        image = get_image(path, WIDTH, HEIGHT)
        if COLORIZED:
            pixels = get_color(image)
        else:
            pixels = get_brightness(image)
        
        oldim = None
        old = get_image(path, WIDTH, HEIGHT)
        if COLORIZED:
            oldim = get_color(old)
        else:
            oldim = get_brightness(old)

        print_image(WIDTH, HEIGHT, ASCII_DENSITY, DEFAULT_CHAR, pixels)
        for i in range(count): #assuming gif
            path = "images/frame{:d}.jpg".format(i)
            
            image = get_image(path, WIDTH, HEIGHT)
            if COLORIZED:
                pixels = get_color(image)/3
            else:
                pixels = get_brightness(image)
            
            oldim = print_image1(WIDTH, HEIGHT, ASCII_DENSITY, DEFAULT_CHAR, pixels, oldim)
            
            #print("\033c")
            #os.remove(path)
        os.remove('images')

    else:
        image = get_image(VIEWED, WIDTH, HEIGHT)
        if(COLORIZED):
            pixels = get_color(image)
        else:
            pixels = get_brightness(image)
        print_image(WIDTH, HEIGHT, ASCII_DENSITY, DEFAULT_CHAR, pixels)

def get_color_escape(r, g, b, background=False):
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)

#######################################################

def get_image(PHOTO, WIDTH, HEIGHT):
    image = Image.open(PHOTO)
    image = image.resize((WIDTH, HEIGHT))
    
    return image
    
#######################################################
    
def get_brightness(image):
    image = image.convert("L") # Blank and White Image
    pixels_brightness = image.load()
    
    return pixels_brightness
    
#######################################################
    
def get_color(image):
    image = image.convert('RGB') # RGB Image
    pixels_color = image.load()
    
    return pixels_color
    
#######################################################

def get_ASCII_char(ASCII_density, brightness):
    density = 255 / len(ASCII_density)
    value = 0
    character = None
    i = 0
    brightness = (brightness[0]+brightness[1]+brightness[2])/3
    while True:
        if value < brightness:
            value = value + density
        else:
            try:
                character = ASCII_density[i]
            except:
                character = ASCII_density[-1]
            break
        i += 1
        
    return character
        
#######################################################

def print_image1(WIDTH, HEIGHT, ASCII_DENSITY, DEFAULT_CHAR, pixels, pixels1):
    if(pixels!=pixels1):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if(pixels[x,y]!=pixels1[x,y]):
                    pixel = DEFAULT_CHAR # Pixel displayed on screen
                    if ASCII:
                        brightness = pixels[x,y]
                        pixel = get_ASCII_char(ASCII_DENSITY, brightness)
                    print("\033["+str(y)+";"+str(x)+"H", end ="")
                    if COLORIZED:
                        r, g, b = pixels[x,y]
                        
                        print(get_color_escape(r, g, b)
                          + pixel
                          + RESET, end="")
                    elif ASCII:
                        print(pixel, end="")
                    pixels1[x,y] = pixels[x,y]
    return pixels1

#######################################################

def print_image(WIDTH, HEIGHT, ASCII_DENSITY, DEFAULT_CHAR, pixels):
    ASCII=glob.ASCII
    COLORIZED=glob.COLORIZED
    for y in range(HEIGHT):
        for x in range(WIDTH):
            pixel = DEFAULT_CHAR # Pixel displayed on screen
            if ASCII:
                brightness = pixels[x,y]
                pixel = get_ASCII_char(ASCII_DENSITY, brightness)
            
            if COLORIZED:
                r, g, b = pixels[x,y]
                
                print(get_color_escape(r, g, b)
                  + pixel
                  + RESET, end="")
            elif ASCII:
                print(pixel, end="")
        print("")
#######################################################

