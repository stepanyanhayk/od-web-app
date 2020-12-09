"""
OBJECT DETECTION WEB APPLICATION

CREATED BY HAYK STEPANYAN
LAST EDIT: DECEMBER 8, 2020
"""

import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import object_detector_copy

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app=Flask(__name__)
app.secret_key = "secret key"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(["jpg"])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img = object_detector_copy.run()
            img.save("static/detected_image.jpg")
            flash('File successfully uploaded')
            return redirect("/detected")
        else:
            flash('Allowed file type so far is only jpg')
            return redirect(request.url)

@app.route("/detected")
def detected():
    location = "static/detected_image.jpg"
    return render_template("detected.html", location=location)
