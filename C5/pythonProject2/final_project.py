# The Project #
# 1. This is a project with minimal scaffolding. Expect to use the the discussion forums to gain insights! It’s not cheating to ask others for opinions or perspectives!
# 2. Be inquisitive, try out new things.
# 3. Use the previous modules for insights into how to complete the functions! You'll have to combine Pillow, OpenCV, and Pytesseract
# 4. There are hints provided in Coursera, feel free to explore the hints if needed. Each hint provide progressively more details on how to solve the issue. This project is intended to be comprehensive and difficult if you do it without the hints.

### The Assignment ###
# Take a [ZIP file](https://en.wikipedia.org/wiki/Zip_(file_format)) of images and process them, using a [library built into python](https://docs.python.org/3/library/zipfile.html) that you need to learn how to use. A ZIP file takes several different files and compresses them, thus saving space, into one single file. The files in the ZIP file we provide are newspaper images (like you saw in week 3). Your task is to write python code which allows one to search through the images looking for the # occurrences of keywords and faces. E.g. if you search for "pizza" it will return a contact sheet of all of the faces which were located on the newspaper page which mentions "pizza". This will test your ability to learn a new ([library](https://docs.python.org/3/library/zipfile.html)), your ability to use OpenCV to detect faces, your ability to use tesseract to do optical character recognition, and your ability to use PIL to composite images together into contact sheets.

# Each page of the newspapers is saved as a single PNG image in a file called [images.zip](./readonly/images.zip). These newspapers are in english, and contain a variety of stories, advertisements and images. Note: This file is fairly large (~200 MB) and may take some time to work with, I would encourage you to use [small_img.zip](./readonly/small_img.zip) for testing.

# Here's an example of the output expected. Using the [small_img.zip](./readonly/small_img.zip) file, if I search for the string "Christopher" I should see the following image:
# ![Christopher Search](./readonly/small_project.png)
# If I were to use the [images.zip](./readonly/images.zip) file and search for "Mark" I should see the following image (note that there are times when there are no faces on a page, but a word is found!):
# ![Mark Search](./readonly/large_project.png)
#
# Note: That big file can take some time to process - for me it took nearly ten minutes! Use the small one for testing.

from zipfile import ZipFile

from PIL import Image
import pytesseract
import cv2 as cv
import numpy as np

# loading the face detection classifier
face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier('readonly/haarcascade_eye.xml')
# the rest is up to you!

def get_images(zip_file, cv_imgs, pil_imgs):
    file_names = []
    with ZipFile(zip_file, 'r') as archive:
        for entry in archive.infolist():
            with archive.open(entry) as file:
                pil_img = Image.open(file).convert('RGB')
                print(entry.filename, pil_img.size, len(pil_img.getdata()))
                file_names.append(entry.filename)
                # resize large images
                if len(pil_img.getdata()) > 22680000:
                    pil_img = pil_img.resize((int(pil_img.width*0.6),int(pil_img.height*0.6)))
                    print('Resizing file: {}'. format(entry.filename))
                    print(entry.filename, pil_img.size, len(pil_img.getdata()))
                cv_img = cv.cvtColor(np.array(pil_img), cv.COLOR_RGB2GRAY)
                cv_imgs.append(cv_img)
                pil_imgs.append(pil_img)
    return file_names

global_cv_images = []
global_pil_images = []
# global_file_names = get_images('readonly/small_img.zip', global_cv_images, global_pil_images)
global_file_names = get_images('readonly/images.zip', global_cv_images, global_pil_images)
print('Finished loading')

# get text from images
def get_text(img):
    return pytesseract.image_to_string(img)

def get_file_name(file_input):
    # return 'small_text/{}.txt'.format(file_input[:-4])
    return 'large_text/{}.txt'.format(file_input[:-4])

# Because the time to execute the the OCR from image files takes a
# very long time we will cache the results of OCR to text files so
# we don't have to do the OCR every single time
text_list=[]
for (file_idx, img) in enumerate(global_cv_images):
    file_name = get_file_name(global_file_names[file_idx])
    # try to open the files locally
    try:
        print('Try to open {}'.format(file_name))
        with open(file_name, 'r') as file_read:
            text_list.append(file_read.read())
            print('File {} read succesfully'.format(file_name))
    # if files do not exist, perform OCR on image files
    except FileNotFoundError:
        print('Failed!')
        with open(file_name, 'w') as file_write:
            text = get_text(Image.fromarray(img, "L"))
            text_list.append(text)
            file_write.write(text)
            print('File {} write succesfully'.format(file_name))
print('OCR finished')

# search trough text for for input string
def search_text(txt_lst, str_to_search, text_found_d):
    text_found_d[str_to_search] = []
    for (file_idx, text) in enumerate(txt_lst):
        temp_text = text.split()
        for word in temp_text:
            if str_to_search in word:
                text_found_d[str_to_search].append(file_idx)
                print("'{}' found in file {}".format(str_to_search, global_file_names[file_idx]))
                break
    return (text_found_d)

d_string = {}
search_text(text_list, 'Christopher', d_string)
search_text(text_list, 'Mark', d_string)
print(d_string)

def get_face(cv_image):
    """Input: cv_image file (narray)
    Output: list of rectangles containing faces defined as: (x,y,w,h)"""
    faces = face_cascade.detectMultiScale(cv_image)
    faces_list = []
    for f in faces:
        faces_list.append(f.tolist())
    return faces_list

def get_eyes(cv_image):
    """Input: cv_image file (narray)
    Output: list of rectangles containing eyes  defined as:(x,y,w,h)"""
    eyes = eye_cascade.detectMultiScale(cv_image, minNeighbors = 1)
    eyes_list = []
    for e in eyes:
        eyes_list.append(e.tolist())
    return eyes_list

def eye_in_face(e, f):
    """determines if an eye rectangle exists inside a face rectangle
    returns True/False"""
    (xe,ye,we,he) = e
    (xf,yf,wf,hf) = f
    if xe >= xf and ye >= yf: # top left corner
        if ((xe+we) <= xf+wf) and ((ye+he) <= (yf+hf)): # bottom right corner
            return True
    return False

def get_faces_with_eyes(faces, eyes):
    """returns faces that contain eyes
    these are most certainly true positives"""
    ok_faces = []
    # interate through faces and try to find if it has eyes
    for face in faces:
        for eye in eyes:
            if eye_in_face(eye, face):
                ok_faces.append(face)
                break
    return ok_faces

from PIL import ImageDraw
from PIL import ImageFont

def show_rects(img, r1, r2 = None):
    pil_img=img.convert("RGB")
    drawing=ImageDraw.Draw(pil_img)
    fnt = ImageFont.truetype('readonly/fanwood-webfont.ttf', 75)
    idx = 0
    for x,y,w,h in r1:
        drawing.rectangle((x,y,x+w,y+h), outline="red")
        drawing.text((x, y), str(idx), font = fnt, fill= 'red')
        idx += 1

    idx = 0
    if r2 is not None:
        for x,y,w,h in r2:
            drawing.rectangle((x,y,x+w,y+h), outline="green")
            drawing.text((x, y), str(idx), font = fnt, fill= 'green')
            idx += 1
    # resize image
    pil_img = pil_img.resize((int(pil_img.width/4),int(pil_img.height/4)))
    display(pil_img)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __str__(self):
        return '(x={}, y={})'.format(self.x, self.y)

# (x, y)         (x+w, y)
# |-------------|
# |             |
# |_____________|
# (x, y+h)      (x+w, y+h)

def get_rect_coord(x, y, w, h):
    """gets input in x,y,w,h (cv_image boxes)
    returns: corner coordinates of Point type (x,y)"""
    top_left     = Point(x, y)
    top_right    = Point(x+w, y)
    bottom_left  = Point(x, y+h)
    bottom_right = Point(x+w, y+h)
    return top_left, top_right, bottom_left, bottom_right

def point_in_rect(point, top_left, bottom_right):
    """determines if a point is inside a rectangle
    input: point (x,y)
    input: rectangle (top_left corner, bottom_right corner
    output: True/False"""
    # point(x,y), rectangle(top_left(x,y), bottom_right(x,y))
    if point.x > top_left.x and point.y > top_left.y:
        if point.x < bottom_right.x and point.y < bottom_right.y:
            return True
    return False

def rectangle_overlap(r1, r2): # r1 = (x1, y1, w1, h1), r2 = (x2, y2, w2, h2)
    """Determines if two rectangles overlap. If a rectangle overlaps another
    at least one corner is inside the other one.
    input: two rectangles in (x,y,w,h) format
    output: True/False"""
    top_left1, top_right1, bottom_left1, bottom_right1 = get_rect_coord(*r1)
    top_left2, top_right2, bottom_left2, bottom_right2 = get_rect_coord(*r2)

    # a rectangle overlaps another if at least one corner is inside the other one
    for corner in get_rect_coord(*r1):
        if point_in_rect(corner, top_left2, bottom_right2):
            return True

    for corner in get_rect_coord(*r2):
        if point_in_rect(corner, top_left1, bottom_right1):
            return True
    # else
    return False

def remove_self_overlap(r1_keep):
    """removes overlaping rectangles in the same list"""
    r_out = r1_keep[:]
    for i in range(0, len(r1_keep)-1):
        for j in range(i+1, len(r1_keep)):
            if(rectangle_overlap(r1_keep[i],r1_keep[j])):
                # keep largest one
                (xi, yi, wi, hi) = r1_keep[i]
                (xj, yj, wj, hj) = r1_keep[j]
                if wi*hi < wj*hj:
                    r_out[i] = None
                    # print('removed item {}'. format(i))
                else:
                    r_out[j] = None
                    # print('removed item {}'. format(j))
    r_out = [x for x in r_out if x is not None]
    return r_out

def remove_overlap(r1_keep, r2_mod):
    """Compares two rectangle lists and returns a list
    with no overlaps
    input: r1_keep, this is the array that remains unchanged
    input: r2_mod this is the array on which the output is based"""
    r_out = r2_mod[:]
    removed = []
    for f1 in r1_keep:
        for (idx,f2) in enumerate(r2_mod):
            if f1 != f2:
                if(rectangle_overlap(f1,f2)):
                    if(r_out[idx] not in removed):
                        removed.append(r_out[idx])
                        r_out[idx] = None
                        # print('removed item {}'. format(idx))
    r_out = [x for x in r_out if x is not None]
    return r_out

def detect_eyes_in_rectangle(cv_image, rect): # r= (x,y,w,h)
    """searches for eyes in a small rectangle containing a
    possible face. Aggressive minNeighbors = 0 finds eyes
    even if they are closed. Sometimes provides false positives
    inside text regions"""
    (x,y,w,h) = rect
    box = cv_image[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(box, minNeighbors = 0)
    if len(eyes) > 0:
        return True
    else:
        return False

def detect_text_in_rectangle(cv_image, rect): # r= (x,y,w,h)
    """searches for text inside a potential face. If text is
    found (more than 10 characters) returns True and this result
    can be discarded as a false possitive)"""
    (x,y,w,h) = rect
    box = cv_image[y:y+h, x:x+w]
    text = get_text(Image.fromarray(box, "L"))
    # print('text:', text)
    if len(text) > 10:
        return True
    else:
        return False

def get_filtered_faces_large(cv_img_test, file_idx):
    """Function gets an images as input and finds
    faces inside using open_cv
    Algorithm searches for faces and eyes.
    If a face contains eyes than it is a very probable
    candidate.
    Faces that don't contain eyes could be potential
    candidates. A new eye detection algorithm is redone
    for each of these small rectangles to detect eyes.
    If eyes are detected, these faces are also addd to
    the final version"""
    # print(global_file_names[file_idx])
    # Use open_CV library to detect faces and eyes
    #
    faces = get_face(cv_img_test)
    # print("Got {} faces".format(len(faces)))
    faces_with_eyes = []
    for rect in faces:
        if(detect_eyes_in_rectangle(cv_img_test, rect)):
            faces_with_eyes.append(rect)
    # print('Discovered {} eligible faces'.format(len(faces_with_eyes)))

    # Display results so far, most likely candidates
    #
    # print("Displaying faces with eyes")
    # show_rects(Image.fromarray(cv_img_test,mode="L"), faces_with_eyes)

    # remove overlaps
    faces_with_eyes_no = remove_self_overlap(faces_with_eyes)

    faces_so_far = faces_with_eyes_no
    # Print number of faces discovered so far
    # print('Total number of faces discovered: {}'.format(len(faces_so_far)))

    # check to see if text is present in face
    # sometime the very aggresive eye-detection procedure
    # used in the previous step finds eyes inside the text
    # To make sure these false positives are eliminated we
    # search for text inside, if 10 or more characters are found
    # this false positive is discarded
    total_faces = faces_so_far[:]
    for (idx, r) in enumerate(total_faces):
        if(detect_text_in_rectangle(cv_img_test, r)):
            print('Text found at index: {}'.format(idx))
            total_faces[idx] = None
    total_faces = [x for x in total_faces if x is not None]

    # Final display
    # show_rects(global_pil_images[file_idx], total_faces)

    return total_faces

# creates a sheet (5 pictures / row) with faces
def create_sheet(faces, file_idx):
    # get file name
    img = global_pil_images[file_idx]

    # create blank file
    IMG_W = 200
    IMG_H = 200
    IMG_PER_ROW = 5
    NO_ROWS = int(len(faces) / IMG_PER_ROW) + 1
    new_image = Image.new('RGB', (IMG_W * IMG_PER_ROW, IMG_H * NO_ROWS))

    # crop faces from file
    cropped_faces = []
    for face in faces:
        # get top_left, bottom_right
        x,y,w,h = face
        face_img = img.crop((x, y, x+w, y+h))
        # resize images to IMG_W, IMG_H (e.g. 200 x 200)
        ratio = IMG_W / face_img.width
        face_img = face_img.resize((int(face_img.width*ratio),int(face_img.height*ratio)))
        cropped_faces.append(face_img)

    # collate faces
    x=0
    y=0

    for face in cropped_faces:
        new_image.paste(face, (x,y))
        x += IMG_W
        if x == IMG_W * IMG_PER_ROW:
            x = 0
            y += IMG_H

    # display result
    display(new_image)
    return None

# search trough text for for input string
# if string is found faces are extracted from that file
# by calling get_filtered_faces_large function.
# if faces are found, a sheet is generated and displayed
def search_text_print_faces(txt_lst, str_to_search):
    text_found_d = {}
    text_found_d[str_to_search] = []
    for (file_idx, text) in enumerate(txt_lst):
        temp_text = text.split()
        for word in temp_text:
            if str_to_search in word:
                text_found_d[str_to_search].append(file_idx)
                print("Results found in file {}".format(global_file_names[file_idx]))
                filtered_faces = get_filtered_faces_large(global_cv_images[file_idx], file_idx)
                if len(filtered_faces) > 0:
                    create_sheet(filtered_faces, file_idx)
                else:
                    print('But there were no faces in that file!')
                break
    return (text_found_d)

# Test program:
search_text_print_faces(text_list, 'Christopher')

search_text_print_faces(text_list, 'Mark')
