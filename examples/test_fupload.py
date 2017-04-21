import os
from hotpot import Hotpot, request, redirect, url_for
# from werkzeug import secure_filename

UPLOAD_FOLDER = 'upload_files'
ALLOWED_EXTENSIONS = set(['txt'])

app = Hotpot(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    print "[allowed_file]: filename is:", filename
    print '.' in filename
    print filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    print "ALLOWED_EXTENSIONS IS:", ALLOWED_EXTENSIONS
    print filename.rsplit('.', 1)[1]
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        print "file is:", file
        print "request.files is:", request.files
        print "file.filename is:", file.filename
        print "allowed_file(file.filename) is", allowed_file(file.filename)
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index'))
    return """
    <!doctype html>
    <title>Upload new file</title>
    <h1>Upload new file</h1>
    <form action="" method=post enctype=multipart/form-data>
        <p><input type=file name=file>
            <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br".join(os.listdir(app.config['UPLOAD_FOLDER'],))

if __name__ == '__main__':
    app.run()
