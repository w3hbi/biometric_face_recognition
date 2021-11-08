# 1. What's Face Recognition ?
Facial recognition is a way of identifying or confirming an individual’s identity using their face. Facial recognition 
systems can be used to identify people in photos, videos, or in real-time.

Facial recognition is a category of biometric security. Other forms of biometric software include voice recognition, 
fingerprint recognition, and eye retina or iris recognition. The technology is mostly used for security and law 
enforcement, though there is increasing interest in other areas of use.

# 2. Face Recognition Project Steps :
- Step 1: Face detection
- Step 2: Face analysis
- Step 3: Converting the image to data
- Step 4: Finding a match

# 3. Packages used in this Project :

**numpy** :  Numpy is the core library for scientific computing in Python. It provides a high-performance 
multidimensional array object, and tools for working with these arrays. If you are already familiar with MATLAB, 
you might find this tutorial useful to get started with Numpy.

    # installing package with pip :
        pip install numpy

**open-cv** : open-source library for computer vision, machine learning, and image processing. OpenCV supports a wide 
variety of programming languages like Python, C++, Java, etc. It can process images and videos to identify objects, 
faces, or even the handwriting of a human. When it is integrated with various libraries, such as Numpy which is a 
highly optimized library for numerical operations, then the number of weapons increases in your Arsenal i.e whatever 
operations one can do in Numpy can be combined with OpenCV.

    # installing package with pip :
        pip install opencv-python

**dlib** : DLib is an open source modern C++ library implementing many machine learning algorithms and supporting 
functionality like threading and networking.

DLib also features utility functionality including :
- Threading, 
- Networking,
- Numerical Algorithms,
- Image Processing,
- Data Compression and Integrity algorithms.


    # First of all, you need to install CMake library :
        pip install cmake

    # then install dlib package :
        pip install dlib

**scipy** : SciPy is an open-source Python library which is used to solve scientific and mathematical problems. It is 
built on the NumPy extension and allows the user to manipulate and visualize data with a wide range of high-level 
commands.

    # installing package with pip :
        pip install scipy

**Important !**: you need to download `vgg-face.mat` and `shape_predictor_68_face_landmarks.dat` to execute this project