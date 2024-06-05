# -*- coding: utf-8 -*-
import os
from flask import Flask, request, redirect, url_for, render_template, jsonify
import cv2
import easyocr
from gtts import gTTS
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Dosya bulunamadı'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Dosya adı boş'}), 400

    language = request.form.get('language', 'tr')

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        detected_text = []

        if file.filename.endswith('.pdf'):
            images = convert_from_path(filepath)
            for image in images:
                img_array = np.array(image)
                text, processed_img = process_image(img_array, language)
                detected_text.extend(text)
        else:
            img = cv2.imread(filepath)
            if img is None:
                return jsonify({'error': 'Resim bulunamadı veya yüklenemedi'}), 400
            text, processed_img = process_image(img, language)
            detected_text = text

        processed_image_filename = 'processed_' + filename.split('.')[0] + '.jpg'
        processed_image_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_image_filename)
        
        if processed_img is not None:
            cv2.imwrite(processed_image_path, processed_img)

        if processed_image_path and not os.path.exists(processed_image_path):
            return jsonify({'error': 'İşlenmiş görüntü doğru şekilde kaydedilemedi'}), 500
        
        audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'detected_text.mp3')

        detected_text_str = ' '.join(detected_text)
        tts = gTTS(detected_text_str, lang=language)
        tts.save(audio_file_path)

        response = {
            'detected_text': detected_text,
            'audio_file_url': url_for('static', filename='uploads/detected_text.mp3'),
            'processed_image_url': url_for('static', filename='uploads/' + processed_image_filename)
        }

        return jsonify(response)

def process_image(image, language):
    reader = easyocr.Reader([language], gpu=True)
    text_ = reader.readtext(image)
    threshold = 0.25
    detected_text = []

    for t_ in text_:
        bbox, text, score = t_
        if score > threshold:
            pt1 = tuple(map(int, bbox[0]))
            pt2 = tuple(map(int, bbox[2]))
            cv2.rectangle(image, pt1, pt2, (0, 255, 0), 2)
            cv2.putText(image, text, pt1, cv2.FONT_HERSHEY_COMPLEX, 0.65, (255, 0, 0), 2)
            detected_text.append(text)

    return detected_text, image

if __name__ == "__main__":
    app.run(debug=True)
