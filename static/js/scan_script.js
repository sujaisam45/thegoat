document.getElementById('scanForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const rfid = document.getElementById('rfid').value;
    localStorage.setItem('rfid', rfid);

    fetch('/process_scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rfid: rfid }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect_url;
        } else {
            console.error('Error:', data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
