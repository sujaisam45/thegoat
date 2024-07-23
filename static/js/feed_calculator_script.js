function goBack() {
    window.history.back();
}

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
    const goatType = document.querySelector('input[name="goatType"]:checked').value;
    let weight = parseFloat(document.getElementById('weight').value);
    let foragePercentage = parseFloat(document.getElementById('forage').value) / 100;
    let hayPercentage = parseFloat(document.getElementById('hay').value) / 100;
    let pelletPercentage = parseFloat(document.getElementById('pellet').value) / 100;

    let dmi;
    if (goatType === 'grower') {
        dmi = weight * 0.03;
    } else if (goatType === 'maintain') {
        dmi = weight * 0.025;
    } else if (goatType === 'lactating') {
        dmi = weight * 0.04;
    } else if (goatType === 'breeding') {
        dmi = weight * 0.035;
    }

    let forageFeed = dmi * foragePercentage * 4;
    let hayFeed = dmi * hayPercentage;
    let pelletFeed = dmi * pelletPercentage;

    let totalFeed = forageFeed + hayFeed + pelletFeed;

    document.getElementById('totalFeed').innerText = totalFeed.toFixed(2);
    document.getElementById('forageFeed').innerText = forageFeed.toFixed(2);
    document.getElementById('hayFeed').innerText = hayFeed.toFixed(2);
    document.getElementById('pelletFeed').innerText = pelletFeed.toFixed(2);
    document.getElementById('result').style.display = 'block';

    const chartType = document.getElementById('chartType').value;
    displayChart(chartType, forageFeed, hayFeed, pelletFeed);

    resetForm();
}

function displayChart(chartType, forage, hay, pellet) {
    const ctx = document.getElementById('feedChart').getContext('2d');
    let chart;
    if (chartType === 'bar') {
        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Forage', 'Hay', 'Pellet'],
                datasets: [{
                    label: 'Feed Amount (kg)',
                    data: [forage, hay, pellet],
                    backgroundColor: ['#4CAF50', '#FFC107', '#FF5722'],
                    borderColor: ['#388E3C', '#FFA000', '#E64A19'],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    } else if (chartType === 'pie') {
        chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: ['Forage', 'Hay', 'Pellet'],
                datasets: [{
                    label: 'Feed Amount (kg)',
                    data: [forage, hay, pellet],
                    backgroundColor: ['#4CAF50', '#FFC107', '#FF5722']
                }]
            },
            options: {
                plugins: {
                    legend: {
                        display: true
                    }
                }
            }
        });
    }
}

function resetForm() {
    document.getElementById('feedForm').reset();
    document.getElementById('forage').disabled = true;
    document.getElementById('hay').disabled = true;
    document.getElementById('pellet').disabled = true;
}

function downloadPDF() {
    const { jsPDF } = window.jspdf;
    html2canvas(document.getElementById('content')).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF();
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save('goat_feed_calculator.pdf');
    });
}
