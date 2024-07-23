document.getElementById('weight').addEventListener('input', enableForageField);
document.getElementById('forage').addEventListener('input', enableHayField);
document.getElementById('hay').addEventListener('input', autofillPelletField);

function enableForageField() {
    if (this.value) {
        document.getElementById('forage').disabled = false;
    }
}

function enableHayField() {
    if (this.value) {
        document.getElementById('hay').disabled = false;
    }
}

function autofillPelletField() {
    let forage = parseFloat(document.getElementById('forage').value) || 0;
    let hay = parseFloat(document.getElementById('hay').value) || 0;

    let remainingPercentage = 100 - forage - hay;
    if (remainingPercentage < 0) {
        if (this.id === 'forage') {
            forage = 100 - hay;
            document.getElementById('forage').value = forage.toFixed(1);
        } else if (this.id === 'hay') {
            hay = 100 - forage;
            document.getElementById('hay').value = hay.toFixed(1);
        }
        remainingPercentage = 0;
    }

    document.getElementById('pellet').value = remainingPercentage.toFixed(1);
    document.getElementById('pellet').disabled = false;
}

function calculateFeed() {
    let weight = parseFloat(document.getElementById('weight').value);
    let foragePercentage = parseFloat(document.getElementById('forage').value) / 100;
    let hayPercentage = parseFloat(document.getElementById('hay').value) / 100;
    let pelletPercentage = parseFloat(document.getElementById('pellet').value) / 100;

    let dmi = weight * 0.03;

    let forageFeed = dmi * foragePercentage * 4;
    let hayFeed = dmi * hayPercentage;
    let pelletFeed = dmi * pelletPercentage;

    let totalFeed = forageFeed + hayFeed + pelletFeed;

    document.getElementById('totalFeed').innerText = totalFeed.toFixed(2);
    document.getElementById('forageFeed').innerText = forageFeed.toFixed(2);
    document.getElementById('hayFeed').innerText = hayFeed.toFixed(2);
    document.getElementById('pelletFeed').innerText = pelletFeed.toFixed(2);
    document.getElementById('result').style.display = 'block';

    // Reset the form after calculation
    resetForm();
}

function resetForm() {
    document.getElementById('feedForm').reset();
    document.getElementById('forage').disabled = true;
    document.getElementById('hay').disabled = true;
    document.getElementById('pellet').disabled = true;
}
