let veterinaryCount = 1;

function addVeterinaryDetails() {
    veterinaryCount++; // Increment the counter
    const container = document.getElementById('additionalVeterinaries');
    const newSection = document.createElement('div');
    newSection.className = 'veterinary-details';
    newSection.innerHTML = `
        <h3>Veterinary ${veterinaryCount}</h3>
        <div class="form-group">
            <label for="veterinary_name_${veterinaryCount}">Veterinary Name:</label>
            <input type="text" id="veterinary_name_${veterinaryCount}" name="veterinary_name[]" required>
        </div>
        <!-- Duplicate for other fields as needed -->
        <div class="form-group">
            <label for="mobile_number_${veterinaryCount}">Mobile Number:</label>
            <input type="text" id="mobile_number_${veterinaryCount}" name="mobile_number[]" required maxlength="10" oninput="validateInputLength(this, 10)">
        </div>

        <div class="form-group">
            <label for="clinic_name_${veterinaryCount}">Clinic Name:</label>
            <input type="text" id="clinic_name_${veterinaryCount}" name="clinic_name[]" required>
        </div>

        <div class="form-group">
            <label for="clinic_number_${veterinaryCount}">Clinic Number:</label>
            <input type="text" id="clinic_number_${veterinaryCount}" name="clinic_number[]" required maxlength="10" oninput="validateInputLength(this, 10)">
        </div>
    `;
    container.appendChild(newSection);
}



function validateInputLength(input, maxLength) {
    if (input.value.length > maxLength) {
        input.value = input.value.slice(0, maxLength);
    }
}

async function fetchLocationDetails(postalCode) {
    try {
        const response = await fetch(`https://api.zippopotam.us/my/${postalCode}`);
        if (!response.ok) {
            throw new Error('Postal code not found');
        }
        const data = await response.json();
        const place = data.places[0];
        return {
            city: place['place name'],
            state: place['state']
        };
    } catch (error) {
        console.error(error);
        return { city: '', state: '' };
    }
}

async function onPostalCodeChange() {
    const postalCode = document.getElementById('postal_code').value;
    if (postalCode.length === 5) {
        const locationDetails = await fetchLocationDetails(postalCode);
        document.getElementById('city').value = locationDetails.city;
        document.getElementById('state').value = locationDetails.state;
    }
}
