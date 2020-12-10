"""
OBJECT DETECTION WEB APPLICATION

@author: HAYK STEPANYAN
LAST EDIT: DECEMBER 10, 2020
"""

import os
from flask import Flask, flash, request, redirect, render_template, Response
from werkzeug.utils import secure_filename
import object_detector
import random
import camera_object_detector

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app=Flask(__name__)
app.secret_key = "secret key"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(["jpg"])

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def remove_dir_files(directory):
    for file_name in os.listdir(directory):
        os.remove(os.path.join(directory, file_name))


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "GET":
        remove_dir_files("static")
        return render_template("upload.html")
    if request.method == "POST":
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            img = object_detector.run()
            random_number = random.randint(1, 100)
            img.save("static/detected_image" + str(random_number) + ".jpg")
            remove_dir_files(app.config["UPLOAD_FOLDER"])
            return render_template("detected.html", location="static/detected_image" + str(random_number) + ".jpg")
        else:
            NOTAFICATION_MESSAGE = "The only allowed file type so far is jpg. Please choose another photo."
            return render_template("failure.html", message=NOTAFICATION_MESSAGE)


@app.route("/video_feed")
def video_feed():
    return Response(camera_object_detector.gen(), mimetype="multipart/x-mixed-replace; boundary=frame")
