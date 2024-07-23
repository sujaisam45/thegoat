document.addEventListener('DOMContentLoaded', function () {
    function fetchRFID() {
        fetch('/read_rfid', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.rfid) {
                document.getElementById('rfid').value = data.rfid;
                fetchRFIDDetails(data.rfid);
            } else {
                console.error('No RFID tag read');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function fetchRFIDDetails(rfid) {
        fetch(`/get_goat_details/${rfid}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data) {
                document.getElementById('gender').value = data.gender;
                document.getElementById('dob').value = data.dob;
                document.getElementById('weight').value = data.weight;
            } else {
                console.error('No details found for RFID:', rfid);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    fetchRFID();
});
function showAdditionalFields() {
    const status = document.querySelector('input[name="status"]:checked').value;
    const additionalFields = document.getElementById('additionalFields');
    additionalFields.innerHTML = '';

    if (status === 'sold') {
        additionalFields.innerHTML = `
            <label for="sold_amt">Sold Amount:</label>
            <input type="number" id="sold_amt" name="sold_amt" required>

            <label for="buyer_name">Buyer Name:</label>
            <input type="text" id="buyer_name" name="buyer_name" required>
        `;
    } else if (status === 'died') {
        additionalFields.innerHTML = `
            <label for="cause_of_death">Cause of Death:</label>
            <input type="text" id="cause_of_death" name="cause_of_death" required>
        `;
    } else if (status === 'slaughtered') {
        additionalFields.innerHTML = `
            <label for="slaughter_cost">Slaughter Cost:</label>
            <input type="number" id="slaughter_cost" name="slaughter_cost" required>
        `;
    }
}
