"""
OBJECT DETECTION WEB APPLICATION

@author: HAYK STEPANYAN
LAST EDIT: JANUARY 8, 2021
"""

from flask import Flask, flash, request, redirect, render_template, Response
from werkzeug.utils import secure_filename
import object_detector
import random
import video_object_detector
import requests
import os

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app=Flask(__name__)
app.secret_key = "secret key"
app.config["MAX_CONTENT_LENGTH"] = None
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

IMAGE_ALLOWED_EXTENSIONS = set(["jpg"])
VIDEO_ALLOWED_EXTENSIONS = set(["mp4"])

def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

def remove_dir_files(directory):
    for file_name in os.listdir(directory):
        os.remove(os.path.join(directory, file_name))

@app.route("/")
def index():
    return redirect("/upload")

@app.route("/upload", methods=["GET"])
def upload_file():    
    remove_dir_files("static")
    remove_dir_files(app.config["UPLOAD_FOLDER"])
    return render_template("upload.html")


@app.route("/detected", methods=["POST"])
def detected():
    file = request.files["file"]
    filename = secure_filename(file.filename)
    if allowed_file(file.filename, IMAGE_ALLOWED_EXTENSIONS):
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        img = object_detector.run()
        num = random.randrange(1, 100)
        location = os.path.join("static", "detected_image" + str(num) + ".jpg")
        img.save(location)
        return render_template("detected.html", location=location)
    elif allowed_file(file.filename, VIDEO_ALLOWED_EXTENSIONS):
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return Response(video_object_detector.gen(video=("uploads/" + filename)), mimetype="multipart/x-mixed-replace; boundary=frame")
    else:
        NOTAFICATION_MESSAGE = "The only allowed file type is jpg for images and mp4 for videos. Please choose another file."                
        return render_template("failure.html", message=NOTAFICATION_MESSAGE)
