import flask
import os

# Ricky:
# Referencing his code from: https://github.com/rickyricky787/SceneryLens/blob/main/flask_app/app.py 
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" 
from flask import Flask, render_template, request, abort
from io import BytesIO
from PIL import Image
import base64
import json
import random
import requests

import pickle
import pandas as pd
from skimage import io
from skimage import transform

app = flask.Flask(__name__, template_folder='templates')

# Ricky: Uploads can only be up to 15MB, this is checked automatically
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

# Ricky: Image types that can be accepted
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".jpeg", ".png", ".webp"]

path_to_vectorizer = 'models/vectorizer.pkl'
path_to_text_classifier = 'models/text-classifier.pkl'
path_to_image_classifier = 'models/image-classifier.pkl'

with open(path_to_vectorizer, 'rb') as f:
    vectorizer = pickle.load(f)

with open(path_to_text_classifier, 'rb') as f:
    model = pickle.load(f)

with open(path_to_image_classifier, 'rb') as f:
    image_classifier = pickle.load(f)



# Main Page
@app.route('/', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        # Just render the initial form, to get input
        return(flask.render_template('index.html'))

    if flask.request.method == 'POST':

        # Ricky:
        if flask.request.files["file"] == "": # it was form. should i change this to request.files?
            uploaded_img = request.files["file"] # changed from request.form to request.files
            img_name = uploaded_img.filename # to get the file name

        # Checks for the filetype of the file uploaded
            if img_name != "":
                file_ext = os.path.splitext(img_name)[1] # what is this doing? getting the file extension?
            
                # Checks for file extensions
                if file_ext not in app.config['UPLOAD_EXTENSIONS']: # if not .jpg, .jpeg, .png .webp
                    return render_template("index.html")
            else:
                return render_template("index.html")

            im = Image.open(uploaded_img) # necessary for rendering image # for some reason, this is not being applied

        else:                                                                      # this part commented out b/c of error?
            url = request.form["file"] # it was form. should i change this to request.files?
            try:
                response = requests.get(url)
            except:
                return render_template("index.html")
            im = Image.open(BytesIO(response.content))

        im = im.convert("RGB")
    
        # For rendering image
        data = BytesIO() 
        im.save(data, "PNG") # Saves image in-memory, no need to save it into a folder.
        encoded_img_data = base64.b64encode(data.getvalue()) 

        return render_template("results.html", img_data = encoded_img_data.decode('utf-8')) # should this be results.html or index.html?



# From Class:
@app.route('/classify_image/', methods=['GET', 'POST'])
def classify_image():
    if flask.request.method == 'GET':
        # Just render the initial form, to get input
        return(flask.render_template('classify_image.html'))

    if flask.request.method == 'POST':
        # Get file object from user input.
        file = flask.request.files['file']

        if file:
            # Read the image using skimage
            img = io.imread(file)

            # Resize the image to match the input the model will accept
            img = transform.resize(img, (28, 28))

            # Flatten the pixels from 28x28 to 784x0
            img = img.flatten()

            # Get prediction of image from classifier
            predictions = image_classifier.predict([img])

            # Get the value of the prediction
            prediction = predictions[0]

            return flask.render_template('classify_image.html', prediction=str(prediction))

    return(flask.render_template('classify_image.html'))


if __name__ == '__main__':
    app.run(debug=True)


