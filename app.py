import os
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.utils import secure_filename # This is for uploads, Its used to security, 
# from flask import jsonify, request
# from models.model import Sermon

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sermons.db'
app.config['UPLOAD_FOLDER'] = 'static/sermons'
db = SQLAlchemy(app)

#? MODELS IN THE SYSTEM


#?User model
class User(db.Model):
    __tablename__ = 'user' #this is a table name for the admin users
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    
#?Sermon model
class Sermon(db.Model):
    __tablename__ = 'sermon' #?This is a table name
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150))
    description= db.Column(db.String(250))
    thumbnail = db.Column(db.String(250))
    path = db.Column(db.String(250))
    created_at = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    
#?Video Sermon model
class Video(db.Model):
    __tablename__ = 'video' #?This is a table name
    id = db.Column(db.Integer, primary_key = True) 
    video_title = db.Column(db.String(150))
    preacher = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(250))
    youtube_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default = datetime.now(timezone.utc))
    
with app.app_context():
    db.create_all()


#?? THIS IS THE SERMON DYNAMIC FUNCTION 
# Login route

@app.route('/login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the database for the user
        user = User.query.filter_by(username=username).first()
        
        # Check if the user exists and the password is correct
        if user and user.password_hash == password:
            return 'Login successful'
        else:
            return 'Login failed'
        
    return render_template('login.html')

# Home index route

@app.route('/') #This is the home route
def index():
    try:
        # Page-nation (Page size/items)
        
        PAGE_SIZE = 5
        page = request.args.get('page', 1, type=int) #passing the variiable to the url url?variable=value
        
    
        print(f"this is page: {page}")
        
        # Get all sermons from the database
        sermons = Sermon.query.order_by(Sermon.created_at.desc()).all()
        
        # Create an HTML response to display the sermons
        sermon_text = '<div>'
        for sermon in sermons:
            sermon_text += f'{sermon.name} - {sermon.description}'
        sermon_text += '</div>'
        
        return render_template('index.html', sermons=sermons) #? Returning the index.html page and the dynamic data, Also we create a virable and we equate it to the sermons liste, ADD THIS AS A PARAMETOR IN THE RNDER TME
    except Exception as e:
        # Return error information if something goes wrong
        error_text = f"<p>The error:<br>{str(e)}</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text


        


# register route 
@app.route('/register')
def register():
    return render_template('register.html')

#Add sermon route

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

#Delete Audio sermon route

@app.route('/delete_sermon/<int:id>', methods=['DELETE'])
def delete_sermon(id):
    try:
        # Query the sermon by ID
        sermon = Sermon.query.get(id)
        if sermon is None:
            return jsonify({"error": "Sermon not found"}), 404

        # Delete the sermon
        db.session.delete(sermon)
        db.session.commit()
        return jsonify({"message": "Sermon deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Delete Video sermon route
#  TODO Make this code work for the deleting button in the video sermons page

@app.route('/delete_video/<int:id>', methods=['DELETE'])
def delete_video(id):
    try:
        # Query the sermon by ID
        video = Video.query.get(id)
        if video is None:
            return jsonify({"error": "Video Sermon not found"}), 404

        # Delete the sermon
        db.session.delete(video)
        db.session.commit()
        return jsonify({"message": "Video deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Profile route 

@app.route('/user_profile')
def user_profile():
    return render_template('users-profile.html')

@app.route('/api/sermons')
def api():
    #getting query results of all sermon from the database
    sermons = Sermon.query.all()
    return jsonify([{'id':sermon.id, 'name': sermon.name, 'description': sermon.description , 'thumbnail': sermon.thumbnail, 'path': sermon.path, 'created_at': sermon.created_at} for sermon in sermons])

# @app.route('/movie')
# def movie():
#     return 'This is the movie page'


#! Dynamic routes
@app.route('/sermon_detail/<id>')
def sermon_detail(id):
    return f"This is a sermon detail for sermon with id : {id}"
#  Update the url to display the sermon name by passing the sermon id 

@app.route('/sermon_details')
def sermon_details():
    id = request.args.get('id',1,type=int)
    return f"This is a sermon detail for sermon with id : {id}"
#  Update the url to display the sermon name by passing the sermon id 

@app.route('/add_devotions')
def add_devotions():
    return render_template('add_devotions.html')


#? V I D E O   S E R M O N S
#video sermons route
@app.route('/video_sermons')
def video_sermons():
    videos = Video.query.all()  # Query all videos
    return render_template('video_sermons.html', videos=videos)

# Add video sermon 
@app.route ('/add_video_sermon', methods = ['POST', 'GET'])

#function to add video 
def add_video():
    if request.method == 'POST':
        video_title = request.form['video_title']
        preacher = request.form['preacher']
        youtube_url = request.form['youtube_url']
        thumbnail = request.files['thumbnail']
        
        
        # get the paths of the images and audio
        thumbnail_name = secure_filename(thumbnail.filename)
        
        #save image path to the server and get the file path
        thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER']+"/thumbnails" , thumbnail_name)
        thumbnail.save(thumbnail_path)
        
        #adding the form data to the database
        new_video = Video(
            video_title = video_title,
            preacher = preacher,
            youtube_url = youtube_url, 
            thumbnail = thumbnail_path
        )
        
        # add data to database
        db.session.add(new_video)
        db.session.commit()

        return f'We have posted  {video_title}'
    return render_template('/add_video_sermons.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)