# minimal example from:
# http://flask.pocoo.org/docs/quickstart/


import project4 as prj4
from project5 import detect

import os
from flask import Flask, flash, request, redirect, url_for,render_template, send_from_directory
from werkzeug.utils import secure_filename

OUTPUT_FOLDER = os.path.join('static', 'output')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['INPUT_FOLDER'] = 'static/input'
app.config['OUTPUT_FOLDER'] = 'static/output'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')  # the site to route to, index/main in this case
def my_form():
    return render_template('main.html')

@app.route('/english')  
def english():
    return render_template('english.html')

@app.route('/science')  
def science():
    return render_template('science.html')

@app.route('/questions', methods=['POST'])
def my_form_post():
    text = request.form['passage']
    #processed_text = text.upper()
    questions = prj4.generate_qns(text)
    return render_template('questions.html', questions=questions)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['INPUT_FOLDER'], filename))
            newfilename = 'input.' + filename.split('.')[1]
            old_fname = os.path.join(app.config['INPUT_FOLDER'], filename)
            new_fname = os.path.join(app.config['INPUT_FOLDER'], newfilename)
            os.rename(old_fname, new_fname)
            return redirect(url_for('uploaded_file',
                                    filename=newfilename))
    return render_template('machine-learning.html')

@app.route('/process/<filename>')
# @app.route('/objects-detected')
def uploaded_file(filename):
    objects = detect(filename)
    return render_template('spelling.html', filename='output/output.jpg', objects=objects)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory('static/input', filename)

if __name__ == '__main__':
    app.run()
