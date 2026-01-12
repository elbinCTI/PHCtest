# ----flask_app.py-----

from flask import Flask, render_template, request, send_file
import PHCcore as p
import os
fi = ''

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'dat', 'bin'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

from werkzeug.utils import secure_filename

@app.route('/', methods=['GET', 'POST'])
def index():
    f = request.form.get('keyfile') or 'enc2'
    global fi
    title = ''
    
    if request.method == 'POST':
        i = request.form.get('enc', '').strip()
        j = request.form.get('dec', '').strip()
        sheet_name = request.form.get('sheet', '').strip()

        # 🔼 HANDLE FILE UPLOAD
        uploaded = request.files.get('upload')
        if uploaded and allowed_file(uploaded.filename):
            filename = secure_filename(uploaded.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded.save(save_path)

            # remove extension for consistency
            f = os.path.splitext(filename)[0]
            title = f"Using uploaded file: {filename}"

        elif 'gen' in request.form and sheet_name:
            p.sheetgen(sheet_name)
            f = sheet_name
            title = f"Sheet '{sheet_name}' generated"

        elif j:
            fi = p.dec(j, os.path.join(UPLOAD_FOLDER, f))
            title = 'Decoded text:'

        elif i:
            fi = p.enc(i, os.path.join(UPLOAD_FOLDER, f))
            title = 'Encoded text:'

    return render_template('index.html',fi=fi,keyfile=f,title=title)

@app.route('/download')
def download_sheet():
    keyfile = request.args.get('file', 'enc2')
    filename = f"{keyfile}.dat"
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(path):
        return "File not found", 404

    return send_file(path, as_attachment=True)
if __name__ == '__main__':
    app.run(debug=True)
