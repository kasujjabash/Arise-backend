import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename # This is for uploads, Its used to security, 
# from models.model import Sermon

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sermons.db'
app.config['UPLOAD_FOLDER'] = 'static/sermons'
db = SQLAlchemy(app)

class Sermon(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))
    description= db.Column(db.String(250))
    thumbnail = db.Column(db.String(250))
    path = db.Column(db.String(250))
    created_at = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    
with app.app_context():
    db.create_all()



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_sermons', methods = ['POST', 'GET'])

#POST AND GET METHODS
#? - GET Method this is the method used to request data from server,
#? - for example : When you vist blog to read an article, the Browser sends a GET request to the server to fetch the blog post data
#? - for example : When you type a query into Google's search bar and hit enter, a GET request is sent with the query parameters and google returns the search results

#? -POST Method The POST method is used to send data to the server to create or update resources. It is commonly used when submitting form data or uploading files
def add_sermons():
    if request.method == 'POST':
        sermon_name = request.form['name']
        sermon_description = request.form['description']
        image_file = request.files['thumbnail']
        audio_file = request.files['path']
        
        # get the paths of the images and audio
        image_file_name = secure_filename(image_file.filename)
        audio_file_name = secure_filename(audio_file.filename)
        
        #save image path to the server and get the file path
        image_file_path = os.path.join(app.config['UPLOAD_FOLDER']+"/thumbnails" , image_file_name)
        image_file.save(image_file_path)
        
        
        #save audio path to the server and get the file path
        audio_file_path = os.path.join(app.config['UPLOAD_FOLDER']+"/audios" , audio_file_name)
        audio_file.save(audio_file_path)
        
        #adding the form data to the database
        new_sermon = Sermon(
            name = sermon_name,
            description = sermon_description, 
            thumbnail = image_file_path, 
            path = audio_file_path
        )
        
        # add data to database
        db.session.add(new_sermon)
        db.session.commit()
        return f'We have posted data  {sermon_name}'
    
    
    
    return render_template('/add_sermons.html')

@app.route('/api')
def api():
    #getting query results of all sermon from the database
    sermons = Sermon.query.all()
    return jsonify([{'id':sermon.id, 'name': sermon.name, 'description': sermon.description , 'thumbnail': sermon.thumbnail, 'path': sermon.path, 'created_at': sermon.created_at} for sermon in sermons])

@app.route('/movie')
def movie():
    return 'This is the movie page'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)