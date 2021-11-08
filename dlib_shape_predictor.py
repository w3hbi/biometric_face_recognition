# -*- coding: utf-8 -*-
# import dlib
import cv2
from imutils import face_utils

print('[INFO]...All Libraries are imported correctly ')

filename = "images/emma watson.jpg"
image = cv2.imread(filename)
print('[INFO]...Reading picture in ' + filename)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
print(gray)

detector = dlib.get_frontal_face_detector()
print('[INFO]...Loading Image detector')
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
print('[INFO]...Loading image predictor')
dots_size = 5

rects = detector(gray, 1)

# loop over the face detections
for (i, rect) in enumerate(rects):

	# determine the facial landmarks for the face region, then
	# convert the facial landmark (x, y)-coordinates to a NumPy
	# array
	shape = predictor(gray, rect)
	shape = face_utils.shape_to_np(shape)

	# convert dlib's rectangle to a OpenCV-style bounding box
	# [i.e., (x, y, w, h)], then draw the face bounding box
	(x, y, w, h) = face_utils.rect_to_bb(rect)
	cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

	# show the face number
	cv2.putText(image, "Face #{}".format(i + 1), (x - 10, y - 10),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

	# loop over the (x, y)-coordinates for the facial landmarks
	# and draw them on the image
	for (x, y) in shape:
		cv2.circle(image, (x, y), dots_size, (0, 255, 0), -1)

# show the output image with the face detections + facial landmarks
print('[INFO]...Generated Picture Outputd')
cv2.imshow("Output", image)
cv2.waitKey(10000)
print('[INFO]...Done')
