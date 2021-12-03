# credit for this code goes to cairocoders. Source: https://www.youtube.com/watch?v=I9BBGulrOmo

from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from werkzeug.utils import secure_filename

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
		
		# mayb we can put the classification here? to get the prediction... but it would make the code harder to read
		prediction = 11111
		percent_happy = 22222
		percent_sad= 33333
		
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


if __name__ == "__main__":
	app.run()