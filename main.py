

import os
import shutil
from typing import Optional

from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from werkzeug.utils import secure_filename

# Import your custom module
import PHCcore as p

app = FastAPI()

# Configuration
# OPTIMIZATION: Use absolute path to ensure robustness in cloud environments
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'dat', 'bin'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup Templates
templates = Jinja2Templates(directory="templates")

def allowed_file(filename: str) -> bool:
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "fi": "",
        "keyfile": "enc2", # Default keyfile
        "title": ""
    })

@app.post("/", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    keyfile: str = Form("enc2"),
    enc: Optional[str] = Form(None),
    dec: Optional[str] = Form(None),
    sheet: Optional[str] = Form(None),
    # Matches <button name="gen" ...>
    gen: Optional[str] = Form(None), 
    # Matches <input type="file" name="upload" ...>
    upload: Optional[UploadFile] = File(None) 
):
    fi = ""
    title = ""
    f = keyfile  # Current active keyfile name (without extension)

    # 1. HANDLE FILE UPLOAD
    if upload and upload.filename:
        if allowed_file(upload.filename):
            filename = secure_filename(upload.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save the uploaded file
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(upload.file, buffer)

            # Update 'f' to new filename without extension
            f = os.path.splitext(filename)[0]
            title = f"Using uploaded file: {filename}"
        else:
            title = "Invalid file type."

    # 2. HANDLE SHEET GENERATION
    # Your PHCcore.sheetgen hardcodes 'uploads/' internally, so we just pass the name
    elif gen is not None and sheet: 
        try:
            # Note: Ensure PHCcore uses relative paths or the same logic as UPLOAD_FOLDER
            p.sheetgen(sheet)
            f = sheet
            title = f"Sheet '{sheet}' generated"
        except Exception as e:
            title = f"Error generating sheet: {e}"

    # 3. HANDLE DECRYPTION
    elif dec:
        # PHCcore.dec adds '.dat', so we need to pass 'uploads/filename'
        path_to_file = os.path.join(UPLOAD_FOLDER, f)
        
        # Run decryption
        result = p.dec(dec.strip(), path_to_file)
        
        # Check for None (PHCcore returns None/prints if file not found)
        if result is None:
            fi = "Error: Keyfile not found."
        else:
            fi = result
            title = 'Decoded text:'

    # 4. HANDLE ENCRYPTION
    elif enc:
        # PHCcore.enc adds '.dat', so we need to pass 'uploads/filename'
        path_to_file = os.path.join(UPLOAD_FOLDER, f)
        
        # Run encryption
        result = p.enc(enc.strip(), path_to_file)
        
        if result is None:
            fi = "Error: Keyfile not found."
        else:
            fi = result
            title = 'Encoded text:'

    return templates.TemplateResponse("index.html", {
        "request": request,
        "fi": fi,
        "keyfile": f,
        "title": title
    })

@app.get("/download")
async def download_sheet(file: str = "enc2"):
    """
    Downloads the .dat file from the uploads folder.
    """
    safe_filename = secure_filename(file)
    filename_with_ext = f"{safe_filename}.dat"
    path = os.path.join(UPLOAD_FOLDER, filename_with_ext)

    if not os.path.exists(path):
        return HTMLResponse(content="File not found", status_code=404)

    return FileResponse(
        path=path, 
        filename=filename_with_ext,
        media_type='application/octet-stream'
    )

if __name__ == '__main__':
    import uvicorn
    # OPTIMIZATION: Get PORT from environment (Render sets this), default to 10000
    # OPTIMIZATION: Host must be 0.0.0.0 to expose to the internet
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)




    # for the testing use this line instead 
    # uvicorn.run(app, host="127.0.0.1", port=8000)

    




    