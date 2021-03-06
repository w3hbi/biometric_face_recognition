# -*- coding: utf-8 -*-
from threading import Thread
import numpy as np
import cv2
from keras import backend as K
from keras.layers import Convolution2D, MaxPooling2D
from keras.layers import Flatten, Dropout, Activation, Permute
from keras.models import Sequential, Model
import os
from multiprocessing.dummy import Pool
from scipy.spatial.distance import cosine as dcos
from scipy.io import loadmat

K.set_image_data_format('channels_last')

""" Step 1 : find face + Step 2 : crop around face """


def auto_crop_image(image):
    if image is not None:
        im = image.copy()
        # Load HaarCascade from the file with OpenCV
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

        # Read the image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        if len(faces) > 0:
            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            (x, y, w, h) = faces[0]
            center_x = x + w / 2
            center_y = y + h / 2
            height, width, channels = im.shape
            b_dim = min(max(w, h) * 1.2, width, height)
            box = [center_x - b_dim / 2, center_y - b_dim / 2, center_x + b_dim / 2, center_y + b_dim / 2]
            box = [int(x) for x in box]
            # Crop Image
            if box[0] >= 0 and box[1] >= 0 and box[2] <= width and box[3] <= height:
                crp_im = im[box[1]:box[3], box[0]:box[2]]
                crp_im = cv2.resize(crp_im, (224, 224), interpolation=cv2.INTER_AREA)
                print("Found {0} faces!".format(len(faces)))
                return crp_im, image, (x, y, w, h)
    return None, image, (0, 0, 0, 0)


""" Step 3 : load a pretrained CNN to generate vectors from faces """


def convblock(cdim, nb, bits=3):
    List = []
    for k in range(1, bits + 1):
        conv_name = 'conv' + str(nb) + '_' + str(k)
        List.append(Convolution2D(cdim, kernel_size=(3, 3), padding='same', activation='relu', name=conv_name))
    List.append(MaxPooling2D((2, 2), strides=(2, 2)))
    return List


def vgg_face_blank():
    withDO = True  # no effect during evaluation but usefull for fine-tuning
    if True:
        mdl = Sequential()
        mdl.add(Permute((1, 2, 3), input_shape=(224, 224, 3)))
        for l in convblock(64, 1, bits=2):
            mdl.add(l)
        for l in convblock(128, 2, bits=2):
            mdl.add(l)
        for l in convblock(256, 3, bits=3):
            mdl.add(l)
        for l in convblock(512, 4, bits=3):
            mdl.add(l)
        for l in convblock(512, 5, bits=3):
            mdl.add(l)
        mdl.add(Convolution2D(4096, kernel_size=(7, 7), activation='relu', name='fc6'))
        if withDO:
            mdl.add(Dropout(0.5))
        mdl.add(Convolution2D(4096, kernel_size=(1, 1), activation='relu', name='fc7'))
        if withDO:
            mdl.add(Dropout(0.5))
        mdl.add(Convolution2D(2622, kernel_size=(1, 1), activation='relu', name='fc8'))
        mdl.add(Flatten())
        mdl.add(Activation('softmax'))

        return mdl


def copy_mat_to_keras(kmodel):
    kerasnames = [lr.name for lr in kmodel.layers]
    prmt = (0, 1, 2, 3)

    for i in range(L.shape[1]):
        matname = L[0, i][0, 0].name[0]
        if matname in kerasnames:
            kindex = kerasnames.index(matname)
            l_weights = L[0, i][0, 0].weights[0, 0]
            l_bias = L[0, i][0, 0].weights[0, 1]
            f_l_weights = l_weights.transpose(prmt)
            assert (f_l_weights.shape == kmodel.layers[kindex].get_weights()[0].shape)
            assert (l_bias.shape[1] == 1)
            assert (l_bias[:, 0].shape == kmodel.layers[kindex].get_weights()[1].shape)
            assert (len(kmodel.layers[kindex].get_weights()) == 2)
            kmodel.layers[kindex].set_weights([f_l_weights, l_bias[:, 0]])


""" Step 4 : find closest vector in database """


def generate_database(folder_img="images"):
    database = {}
    for the_file in os.listdir(folder_img):
        file_path = os.path.join(folder_img, the_file)
        try:
            if os.path.isfile(file_path):
                name = the_file.split(".")[0]
                img = cv2.imread(file_path)
                crp_im, src_img, (_, y, w, h) = auto_crop_image(img)
                vector_image = crp_im[None, ...]
                database[name] = feature_model.predict(vector_image)[0, :]
        except Exception as e:
            print(e)
    return database


def find_closest(img, database, min_detection=2.5):
    im_arr1 = np.asarray(img)
    im_arr1 = im_arr1[None, ...]
    # Prediction
    fvec1 = feature_model.predict(im_arr1)[0, :]
    # Closest person in DB
    dmin = 0.0
    umin = ""
    for key, value in database.items():
        fvec2 = value
        dcos_1_2 = dcos(fvec1, fvec2)
        if umin == "":
            dmin = dcos_1_2
            umin = key
        elif dcos_1_2 < dmin:
            dmin = dcos_1_2
            umin = key
    if dmin > min_detection:
        umin = ""
    return umin, dmin


""" Main function """


def webcam_face_recognizer(database):
    cv2.namedWindow("preview")
    vc = cv2.VideoCapture(0)
    ready_to_detect_identity = True

    while vc.isOpened():
        _, frame = vc.read()
        img = frame
        # Image analysis (start here with img loaded with your image)
        # We do not want to detect a new identity while the program is in the process of identifying another person
        img_crop, img, (x, y, w, h) = auto_crop_image(img)

        if ready_to_detect_identity and img_crop is not None:
            # Stop analysis while identifying
            # ready_to_detect_identity = False
            pool = Pool(processes=1)
            name, ready_to_detect_identity = pool.apply_async(recognize_image, [img_crop, database]).get()
            pool.close()
            cv2.putText(img=frame, text=name, org=(int(x), int(y + h + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        thickness=2, fontScale=1, color=(0, 255, 0))
        key = cv2.waitKey(1000)
        cv2.imshow("preview", img)

        if key == 27:  # exit on ESC
            break
    cv2.destroyWindow("preview")


""" Bonus functions """


def recognize_image(img, database):
    print("******** PROCEDING FACIAL RECOGNITION ********")
    name, dmin = find_closest(img, database)

    print("******** RESUME ANALYSIS ********")
    return name, True


def capture_screenshot(name):
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()
    if ret:
        img = frame
        cv2.imwrite("images/" + name + ".jpg", img)
    video_capture.release()


""" Initializing Face Detection """
# CNN model initialization
face_model = vgg_face_blank()
print('[INFO]...Face Mode CNN Initialized Successfully')

# Load the pretrained weights into the model
data = loadmat('vgg-face.mat', matlab_compatible=False, struct_as_record=False)
print('[INFO]...Pretrained weights Loaded into the model Successfully')

L = data['layers']

description = data['meta'][0, 0].classes[0, 0].description

copy_mat_to_keras(face_model)

# Final model that can get inputs and generate a prediction as an output
feature_model = Model(inputs=face_model.layers[0].input,
                      outputs=face_model.layers[-2].output,
                      name='encoder')

print('[INFO]...Inputs available now')
print('[INFO]...Generating Prediction as an Output')

# Using Face Detection with Camera
db = generate_database()

# Scan every frame
webcam_face_recognizer(db)
