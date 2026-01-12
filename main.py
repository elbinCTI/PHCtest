# ----main.py-----
import os
import shutil
from typing import Optional

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from werkzeug.utils import secure_filename

# Import your custom module
# Ensure PHCcore.py is in the same directory
import PHCcore as p

app = FastAPI()

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'dat', 'bin'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup Templates
templates = Jinja2Templates(directory="templates")

# Optional: Mount static files if you have CSS/JS
# app.mount("/static", StaticFiles(directory="static"), name="static")

def allowed_file(filename: str) -> bool:
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Default state for GET request
    return templates.TemplateResponse("index.html", {
        "request": request,
        "fi": "",
        "keyfile": "enc2",
        "title": ""
    })

@app.post("/", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    keyfile: str = Form("enc2"),
    enc: Optional[str] = Form(None),
    dec: Optional[str] = Form(None),
    sheet: Optional[str] = Form(None),
    # Captures specific submit buttons if they have name="gen"
    gen: Optional[str] = Form(None), 
    upload: Optional[UploadFile] = File(None)
):
    fi = ""
    title = ""
    
    # We use a local variable f to track the current keyfile name
    f = keyfile

    # 🔼 HANDLE FILE UPLOAD
    # Check if a file was actually sent (filename is not empty)
    if upload and upload.filename:
        if allowed_file(upload.filename):
            filename = secure_filename(upload.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save the file
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(upload.file, buffer)

            # Remove extension for consistency (matching Flask logic)
            f = os.path.splitext(filename)[0]
            title = f"Using uploaded file: {filename}"
        else:
            title = "Invalid file type."

    # 🔼 HANDLE GENERATE SHEET
    elif gen is not None and sheet:
        # Assuming p.sheetgen creates a file in the current dir or specific path
        # You might need to adjust PHCcore to save into UPLOAD_FOLDER
        # or move the file after generation.
        # Here we assume p.sheetgen handles it or saves to root.
        
        # If PHCcore saves to root, move it to uploads to keep logic consistent
        p.sheetgen(sheet) 
        
        # Check if PHCcore saved it with .dat or .bin, assume .dat for now
        # Move generated file to upload folder if it's not generated there
        generated_file = f"{sheet}.dat"
        if os.path.exists(generated_file) and generated_file != os.path.join(UPLOAD_FOLDER, generated_file):
             shutil.move(generated_file, os.path.join(UPLOAD_FOLDER, generated_file))

        f = sheet
        title = f"Sheet '{sheet}' generated"

    # 🔼 HANDLE DECRYPTION
    elif dec:
        try:
            # Construct full path to keyfile
            key_path = os.path.join(UPLOAD_FOLDER, f)
            # If extension is missing in 'f', PHCcore might expect it or the file logic needs it.
            # Based on your flask code: p.dec(j, os.path.join(UPLOAD_FOLDER, f))
            # You might need to append .dat if 'f' doesn't have it.
            
            # Auto-resolving extension if file not found exactly as 'f'
            if not os.path.exists(key_path):
                 if os.path.exists(key_path + ".dat"):
                     key_path += ".dat"
            
            fi = p.dec(dec.strip(), key_path)
            title = 'Decoded text:'
        except Exception as e:
            fi = f"Error: {str(e)}"

    # 🔼 HANDLE ENCRYPTION
    elif enc:
        try:
            key_path = os.path.join(UPLOAD_FOLDER, f)
            # Auto-resolving extension logic
            if not os.path.exists(key_path):
                 if os.path.exists(key_path + ".dat"):
                     key_path += ".dat"

            fi = p.enc(enc.strip(), key_path)
            title = 'Encoded text:'
        except Exception as e:
            fi = f"Error: {str(e)}"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "fi": fi,
        "keyfile": f,
        "title": title
    })

@app.get("/download")
async def download_sheet(file: str = "enc2"):
    # Sanitize input to prevent directory traversal
    safe_filename = secure_filename(file)
    
    # Assuming the files have .dat extension based on Flask code
    filename_with_ext = f"{safe_filename}.dat"
    path = os.path.join(UPLOAD_FOLDER, filename_with_ext)

    if not os.path.exists(path):
        # Fallback to check if file param already had extension
        path = os.path.join(UPLOAD_FOLDER, safe_filename)
        if not os.path.exists(path):
             raise HTTPException(status_code=404, detail="File not found")
        filename_with_ext = safe_filename

    return FileResponse(
        path, 
        media_type='application/octet-stream', 
        filename=filename_with_ext
    )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)