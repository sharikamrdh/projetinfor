from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, jsonify 
import os
import zlib
from PIL import Image
import librosa
import shutil
from pydub import AudioSegment
import gzip
import subprocess


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'downloads')

def showProgressBar():
    return "showProgressBar();"

def hideProgressBar():
    return "hideProgressBar();"


# Import de la fonction determine_data_type
def determine_data_type(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension in ['.txt', '.csv', '.json', '.xml', '.yaml', '.ini']:
        return 'text'
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff']:
        return 'image'
    elif file_extension in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a']:
        return 'audio'
    elif file_extension in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']:
        return 'video'
    elif file_extension in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.odt', '.ods', '.odp']:
        return 'document'
    elif file_extension in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
        return 'compressed'
    elif file_extension in ['.html', '.htm', '.css', '.js', '.php', '.asp', '.jsp']:
        return 'web'
    elif file_extension in ['.py', '.c', '.cpp', '.java', '.php', '.rb', '.pl', '.sh', '.bat']:
        return 'code'
    elif file_extension in ['.exe', '.dll', '.so']:
        return 'executable'
    elif file_extension in ['.ttf', '.otf']:
        return 'font'
    elif file_extension in ['.stl', '.obj', '.fbx', '.blend']:
        return '3d_model'
    elif file_extension in ['.csv', '.kml', '.gpx']:
        return 'GIS_data'
    else:
        return 'unknown'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], request.form['file_path'])

    if os.path.exists(file_path):
        filename, ext = os.path.splitext(os.path.basename(request.form['file_path']))
        
        # Appel de determine_data_type pour déterminer le type de fichier
        file_type = determine_data_type(file_path)
        
        download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename + '_compressed' + ext)

        showProgressBar()
        
        if ext in ['.jpg', '.jpeg', '.png', '.mp4']:
            compress_image_or_video(file_path, download_path)
        elif ext in ['.mp3', '.wav']:
            compress_audio(file_path, download_path)
        elif ext == '.txt':
            compress_text(file_path, download_path)
        elif ext == '.pdf':
            compress_pdf(file_path, download_path)
        elif ext in ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx']:
            compress_office(file_path, download_path)
        else:
            return "Unsupported file format"

        original_size = os.path.getsize(file_path)
        compressed_size = os.path.getsize(download_path)
        compression_ratio = round((original_size - compressed_size) / original_size * 100, 2)

        session['compression_data'] = {
            'filename': filename,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'file_type': file_type  # Ajout du type de fichier dans les données de compression
        }

        # Passer les données de compression au template
        return render_template('compression_result.html', compression_data=session['compression_data'])
    else:
        return render_template('index.html', error_compress="File not found", error_compress_file_path=request.form['file_path'])



def compress_image_or_video(file_path, output_path):
    if file_path.endswith(('.jpeg', '.png')):
        img = Image.open(file_path)
        img = img.convert('RGB')
        img.save(output_path, format='JPEG', quality=50)
    elif file_path.endswith('.mp4'):
        subprocess.run(['ffmpeg', '-i', file_path, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-b:a', '128k', output_path])

def compress_audio(file_path, output_path):
    y, sr = librosa.load(file_path)
    librosa.output.write_wav(output_path, y, sr, norm=False)

def compress_text(file_path, output_path):
    with open(file_path, 'rb') as f_in:
        with gzip.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def compress_pdf(file_path, output_path):
    subprocess.run(['gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4', '-dPDFSETTINGS=/ebook', '-dNOPAUSE', '-dQUIET', '-dBATCH', '-sOutputFile=' + output_path, file_path])

def compress_office(file_path, output_path):
    try:
        unoconv_output = subprocess.check_output(['unoconv', '-f', 'pdf', '--stdout', file_path])
        with open(output_path, 'wb') as f_out:
            f_out.write(unoconv_output)
        print("Office file compression successful.")
    except subprocess.CalledProcessError as e:
        print("Error during office file compression:", e)
        

@app.route('/decompress', methods=['POST'])
def decompress():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], request.form['file_path'])

    
    if os.path.exists(file_path):
        filename, ext = os.path.splitext(os.path.basename(request.form['file_path']))
        
        file_type = determine_data_type(file_path)
        
        download_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)

        showProgressBar()
        
        if ext == '.compressed':
            decompress_lossless(file_path, download_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mov', '.txt', '.csv', '.doc', '.docx', '.xls', '.xlsx']:
            decompress_lossy(file_path, download_path)
            return redirect(url_for('download', filename=filename))
        else:
            return "Unsupported file format for decompression"
        
        original_size = os.path.getsize(file_path)
        compressed_size = os.path.getsize(download_path)
        compression_ratio = round((original_size - compressed_size) / original_size * 100, 2)


        session['decompression_data'] = {
            'filename': filename,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'file_type': file_type,
        }

        return render_template('decompression_result.html', decompression_data=session['decompression_data'])
    else:
        return render_template('index.html', error_decompress="File not found", error_compress_file_path=request.form['file_path'])

def decompress_lossless(compressed_file_path, output_path):
    try:
        with open(compressed_file_path, 'rb') as f:
            compressed_data = f.read()
        decompressed_data = zlib.decompress(compressed_data)
        with open(output_path, 'wb') as f:
            f.write(decompressed_data)
        print("Lossless decompression successful.")
    except zlib.error as e:
        print("Error during lossless decompression:", e)

def decompress_lossy(compressed_file_path, output_path):
    try:
        if compressed_file_path.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            subprocess.run(["convert", compressed_file_path, output_path])
        elif compressed_file_path.endswith(('.mp3', '.wav', '.ogg')):
            subprocess.run(["ffmpeg", "-i", compressed_file_path, output_path])
        elif compressed_file_path.endswith(('.mp4', '.avi', '.mov')):
            subprocess.run(["ffmpeg", "-i", compressed_file_path, "-c:v", "copy", output_path])
        elif compressed_file_path.endswith(('.txt', '.csv', '.doc', '.docx', '.xls', '.xlsx')):
            with open(compressed_file_path, 'rb') as f_in:
                compressed_data = f_in.read()
            with open(output_path, 'wb') as f_out:
                f_out.write(compressed_data)
        else:
            print("Unsupported file format for lossy decompression")
            return
        print("Lossy decompression successful.")
    except Exception as e:
        print("Error during lossy decompression:", e)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

@app.route('/compression_report')
def compression_report():
    compression_data = session.pop('compression_data', None)
    return render_template('compression_report.html', compression_data=compression_data)

@app.route('/decompression_report')
def decompression_report():
    decompression_data = session.pop('decompression_data', None)
    return render_template('decompression_report.html', decompression_data=decompression_data)
