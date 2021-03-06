# credit for this code goes to cairocoders. Source: https://www.youtube.com/watch?v=I9BBGulrOmo

import flask
from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename

#########################################

import scipy.io
import numpy as np
import pandas as pd

import pickle

#!pip install opencv-python
import cv2

import glob

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

#!pip install cmake  
import cmake
#!pip install dlib

#import dlib
from PIL import Image
from skimage import io
import matplotlib.pyplot as plt

lr_model  = pickle.load(open('model_lr.sav', 'rb'))

def get_images_from_folder(imdir):
    ext = ['png', 'jpg', 'gif']    # Add image formats here

    files = []
    [files.extend(glob.glob(imdir + '*.' + e)) for e in ext] #arbitrary ordering of files 
    files = sorted(files) # to get back file ordering
    images = [cv2.imread(file) for file in files]

    return images


def detect_faces(image): # this function doesn't work because dlib hasn't been imported

    # Create a face detector
    face_detector = dlib.get_frontal_face_detector()

    # Run detector and get bounding boxes of the faces on image.
    detected_faces = face_detector(image, 1)
    face_frames = [(x.left(), x.top(),
                    x.right(), x.bottom()) for x in detected_faces]

    return face_frames

def facelist(path): # this function also doesn't work if detect_faces doesn't work
    
    # Load image
    img_path = path
    image = io.imread(img_path)

    # Detect faces
    detected_faces = detect_faces(image) 

    #create a list of n faces to store 
    list_of_faces =[]

    # Crop faces and plot and resize 
    newsize = (100,100)
    for n, face_rect in enumerate(detected_faces):
        face = Image.fromarray(image).crop(face_rect)
    
        #plt.subplot(1, len(detected_faces), n+1)
        #plt.axis('off')
        #plt.imshow(face)
        list_of_faces.append(face.resize(newsize))
    return list_of_faces

def X(faces):
    #convert from bgr to gray scale
    images =[]
    
    if(type(faces) != 'numpy.ndarray'):
        for face in faces: 
            images.append(np.array(face))
  
    #if it is a numpy array type 
    else:  
        images = faces 
        
    images_gray = [cv2.cvtColor(images[i], cv2.COLOR_BGR2GRAY) for i in range(len(images)) ]
    #convert from a 100x100 to a 1D row of 1000 cols
    flatten_gray = [images_gray[i].flatten() for i in range(len(images_gray))]
    #create into a df of flatten images 
    flatten_df = pd.DataFrame(flatten_gray)
    
    return flatten_df

##########################################

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/' # need to have this folder in the same folder as app.py

app.secret_key = "secret key" # previously cairocoders-ednalan - some kind of password. seems changable. might not be necessary for this project.
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file present')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image has been selected to be uploaded')
		return redirect(request.url)
	if file and allowed_file(file.filename): # if the file exists and if it has a correct extension
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # save it in the static/uploads/ folder
		#print('upload_image filename: ' + filename)
		flash('Image was successfully uploaded')
		
		uploaded_file_path = UPLOAD_FOLDER + filename 
		print(uploaded_file_path) # this prints the path and the filename (Ex. static/uploads/image.jpg)
		print(type(uploaded_file_path)) # shows that this is a str file type

		# mayb we can put the classification here? to get the prediction... but it would make the code harder to read
		image_directory = "static/uploads/"
		sample_images = get_images_from_folder(image_directory)
		#sample_images
		flatten_images_df = X(sample_images)
		flatten_images_df

		a = lr_model.predict_proba(flatten_images_df.tail(1)/255)
		b = lr_model.predict(flatten_images_df.tail(1)/255) 
		percent_happy = "{:.3f}".format(a[0][0])
		percent_sad = "{:.3f}".format(a[0][1])
		prediction = b[0]

		# try to get only the last image in the dataframe (the latest uploaded image) [-1] or tail ?
		# or to delete every file in the static/uploads/ folder after every classification

		#os.remove(uploaded_file_path) # does remove the file, but in this position, it prevents pic from being shown

		return render_template('index.html', filename=filename, 
			prediction=prediction, percent_happy=percent_happy, percent_sad=percent_sad) 
		# if everything goes well, the code should run till here for this function
	else:
		flash('The allowed image types are: png, jpg, jpeg, gif')
		return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/input_URL/', methods=['GET','POST'])
def input_URL():
	if flask.request.method == 'GET':
		return(flask.render_template('input_URL.html'))

	if flask.request.method == 'POST':
		# to get input/URL from user
		u_var = flask.request.form['inputted_variable']

		# you can put the classification here
		prediction = "Happy"
		percent_happy = 99.99
		percent_sad= 0.01

		return(flask.render_template('input_URL.html', inputted_URL=u_var,
			prediction=prediction, percent_happy=percent_happy, percent_sad=percent_sad))

	return(flask.render_template('input_URL.html'))


if __name__ == "__main__":
	app.run()