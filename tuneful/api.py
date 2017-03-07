import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path

# JSON Schema describing the structure of a song
song_schema = {
    "properties": {
        "file": {
            "properties": {
                "id" : {"type" : "number"},
                "name": {"type": "string"}
            },
         },
    },
    "required": ["file"]
}

# API endpt to get songs
@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():
    """Get a list of songs"""
    #Get and filter the posts from the db
    songs = session.query(models.Song).order_by(models.Song.id)
    
    # Convert the posts to JSON and return a response
    data = json.dumps([song.as_dictionary() for song in songs])
    return Response(data, 200, mimetype="application/json")

#API endpt to add songs
@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_add():
    """Add a new song"""
    data = request.json 
    print(data)
    # Check that the JSON supplied is valid
    # If not you return a 422 Unprocessable Entity
    try:
        validate(data, song_schema)
        song = session.query(models.File).filter_by(name=data["file"]["name"]).first()
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
    
    #Add the song to the db
    song = models.Song(file_id=data["file"]["id"])
    session.add(song)
    session.commit()
    
    #return a 201 created, containing the post as JSON and with the 
    #location header set to the location of the post
    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("songs_get")}
    return Response(data, 201, headers=headers, mimetype="application/json")
    