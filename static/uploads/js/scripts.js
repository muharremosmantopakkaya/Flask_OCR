document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const fileInput = document.getElementById('file');
    const imagePreview = document.getElementById('imagePreview');
    const audioPlayer = document.getElementById('audioPlayer');
    const resultDiv = document.getElementById('result');
    const textDiv = document.getElementById('detected-text');
    const progressBar = document.getElementById('progressBar');
    const progressContainer = document.querySelector('.progress');
    const downloadLinks = document.getElementById('downloadLinks');

    fileInput.addEventListener('change', function() {
        const file = fileInput.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Image Preview" class="img-fluid"/>`;
            }
            reader.readAsDataURL(file);
        }
    });

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);

        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressBar.style.width = percentComplete + '%';
                progressBar.textContent = Math.round(percentComplete) + '%';
            }
        });

        xhr.onloadstart = function() {
            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';
            progressBar.textContent = '0%';
        };

        xhr.onload = function() {
            progressContainer.style.display = 'none';
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.processed_image_url) {
                    resultDiv.innerHTML = `<img src="${response.processed_image_url}" alt="Processed Image" class="img-fluid"/>`;

                    textDiv.innerHTML = '<h3>Algılanan metin:</h3><ul>' + response.detected_text.map(text => `<li>${text}</li>`).join('') + '</ul>';

                    if (response.audio_file_url) {
                        const audioUrl = `${response.audio_file_url}?t=${new Date().getTime()}`;
                        audioPlayer.src = audioUrl;
                        audioPlayer.style.display = 'block';
                        audioPlayer.load();

                        downloadLinks.innerHTML = `
                            <a href="${response.processed_image_url}" download class="btn btn-success mt-3">İşlenmiş Görüntüyü İndir</a>
                            <a href="${audioUrl}" download class="btn btn-success mt-3">Ses Dosyasını İndir</a>
                        `;
                    }
                } else if (response.error) {
                    alert('Hata: ' + response.error);
                } else {
                    alert('Resim işlenirken hata oluştu.');
                }
            } else {
                alert('Resim yüklenirken hata oluştu.');
            }
        };

        xhr.onloadend = function() {
            progressContainer.style.display = 'none';
        };

        xhr.send(formData);
    });
});