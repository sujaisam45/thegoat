document.addEventListener('DOMContentLoaded', function () {
    const scanMaleButton = document.getElementById('scanMaleButton');
    const maleRfidInput = document.getElementById('male_rfid');

    scanMaleButton.addEventListener('click', function () {
        fetch('/read_rfid', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.rfid) {
                maleRfidInput.value = data.rfid;
            } else {
                alert('No RFID tag read');
            }
        })
        .catch(error => console.error('Error:', error));
    });

    const scanFemaleButton = document.getElementById('scanFemaleButton');
    const femaleRfidInput = document.getElementById('female_rfid');

    scanFemaleButton.addEventListener('click', function () {
        fetch('/read_rfid', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.rfid) {
                femaleRfidInput.value = data.rfid;
            } else {
                alert('No RFID tag read');
            }
        })
        .catch(error => console.error('Error:', error));
    });

    const programDateInput = document.getElementById('program_date');
    const pregnancyCheckDateInput = document.getElementById('pregnancy_check_date');
    const expectedBirthDateInput = document.getElementById('expected_birth_date');
    const gestationPeriod = 150; // Average gestation period for goats in days

    programDateInput.addEventListener('input', function () {
        const programDate = new Date(programDateInput.value);
        if (!isNaN(programDate)) {
            // Set Pregnancy Check Date to one month after Program Date
            const pregnancyCheckDate = new Date(programDate);
            pregnancyCheckDate.setMonth(programDate.getMonth() + 1);
            pregnancyCheckDateInput.value = pregnancyCheckDate.toISOString().split('T')[0];

            // Set Expected Birth Date to 150 days after Pregnancy Check Date
            const expectedBirthDate = new Date(pregnancyCheckDate);
            expectedBirthDate.setDate(pregnancyCheckDate.getDate() + gestationPeriod);
            expectedBirthDateInput.value = expectedBirthDate.toISOString().split('T')[0];
        }
    });

    const breedingMethodSelect = document.getElementById('breeding_method');
    const aiDetails = document.getElementById('ai_details');
    const etDetails = document.getElementById('et_details');

    breedingMethodSelect.addEventListener('change', function () {
        const selectedMethod = breedingMethodSelect.value;
        if (selectedMethod === 'AI') {
            aiDetails.classList.remove('hidden');
            etDetails.classList.add('hidden');
        } else if (selectedMethod === 'ET') {
            etDetails.classList.remove('hidden');
            aiDetails.classList.add('hidden');
        } else {
            aiDetails.classList.add('hidden');
            etDetails.classList.add('hidden');
        }
    });

    // Trigger change event to set the initial state
    breedingMethodSelect.dispatchEvent(new Event('change'));
});
