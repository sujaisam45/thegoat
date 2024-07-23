document.getElementById('registrationForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const imageInput = document.getElementById('image');
    const capturedImage = document.getElementById('capturedImage').src;
    imageInput.value = capturedImage;
    this.submit();
});

const breedList = [
    "Boer",
    "Kiko",
    "Spanish",
    "Nubian",
    "LaMancha",
    "Oberhasli",
    "Saanen",
    "Toggenburg",
    "Alpine",
    "Anglo-Nubian"
];

document.getElementById('breed').addEventListener('input', function() {
    const input = this.value.toLowerCase();
    const suggestions = breedList.filter(breed => breed.toLowerCase().startsWith(input));
    const suggestionBox = document.getElementById('breedList');
    suggestionBox.innerHTML = '';
    if (suggestions.length > 0) {
        suggestionBox.style.display = 'block';
        suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.textContent = suggestion;
            li.addEventListener('click', function() {
                document.getElementById('breed').value = suggestion;
                suggestionBox.style.display = 'none';
            });
            suggestionBox.appendChild(li);
        });
    } else {
        suggestionBox.style.display = 'none';
    }
});

document.getElementById('dateOfEntry').value = new Date().toISOString().split('T')[0];

function generatePDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const id = document.getElementById('id').value;
    const breed = document.getElementById('breed').value;
    const sex = document.querySelector('input[name="sex"]:checked').value;
    const dob = document.getElementById('dob').value;
    const weight = document.getElementById('weight').value;
    const note = document.getElementById('note').value;
    const dateOfEntry = document.getElementById('dateOfEntry').value;

    doc.text(`ID: ${id}`, 10, 10);
    doc.text(`Breed: ${breed}`, 10, 20);
    doc.text(`Sex: ${sex}`, 10, 30);
    doc.text(`Date of Birth: ${dob}`, 10, 40);
    doc.text(`Weight (kg): ${weight}`, 10, 50);
    doc.text(`Note: ${note}`, 10, 60);
    doc.text(`Date of Entry: ${dateOfEntry}`, 10, 70);

    doc.save('birth_certificate.pdf');
}

// Capture live photo
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture');
const capturedImage = document.getElementById('capturedImage');

// Get access to the camera
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
        video.srcObject = stream;
        video.play();
    });
}

// Capture photo
captureButton.addEventListener('click', function() {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const dataURL = canvas.toDataURL('image/png');
    capturedImage.src = dataURL;
    capturedImage.style.display = 'block';
});
