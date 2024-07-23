document.addEventListener('DOMContentLoaded', function () {
    function fetchRFID(fieldId) {
        fetch('/read_rfid', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.rfid) {
                document.getElementById(fieldId).value = data.rfid;
            } else {
                console.error('No RFID tag read');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // Automatically fetch and set the main goat RFID
    fetchRFID('rfid');

    // Fetch and set the Father Goat RFID
    document.getElementById('scanFatherButton').addEventListener('click', function() {
        fetchRFID('father_goat_rfid');
    });

    // Fetch and set the Mother Goat RFID
    document.getElementById('scanMotherButton').addEventListener('click', function() {
        fetchRFID('mother_goat_rfid');
    });
});
