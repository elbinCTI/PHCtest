# ----flask_app.py-----

from flask import Flask, render_template, request
import PHCcore as p
from flask import send_file
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def index():
    f = request.form.get('keyfile', 'enc2')
    fi = ''
    title = ''
    if request.method == 'POST':
        i = request.form.get('enc', '').strip()
        j = request.form.get('dec', '').strip()
        sheet_name = request.form.get('sheet', '').strip()

        if 'gen' in request.form and sheet_name:
            p.sheetgen(sheet_name)
            f = sheet_name
            title = f"Sheet '{sheet_name}' generated"

        elif j:
            fi = p.dec(j, f)
            title = 'Decoded text:'

        elif i:
            fi = p.enc(i, f)
            title = 'Encoded text:'

    return render_template('index.html',fi=fi,keyfile=f,title=title)
@app.route('/download')
def download_sheet():
    keyfile = request.args.get('file', 'enc2')
    filename = f"{keyfile}.dat"

    if not os.path.exists(filename):
        return "File not found", 404

    return send_file(filename,as_attachment=True,download_name=filename)
if __name__ == '__main__':
    app.run(debug=True)
