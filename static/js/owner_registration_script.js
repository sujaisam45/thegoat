function validateInputLength(input, maxLength) {
    if (input.value.length > maxLength) {
        input.value = input.value.slice(0, maxLength);
    }
}

function toggleCompanyFields() {
    const businessType = document.getElementById('business_type').value;
    const companyFields = document.querySelectorAll('.company-only');
    if (businessType === 'company') {
        companyFields.forEach(field => field.style.display = 'block');
    } else {
        companyFields.forEach(field => field.style.display = 'none');
    }
}

function selectGender(gender) {
    const genderInput = document.getElementById('gender');
    genderInput.value = gender;  // Update the hidden input value

    document.querySelectorAll('.gender-icon').forEach(icon => {
        icon.classList.remove('active');  // Remove active class from all icons
    });
    document.getElementById(gender).classList.add('active');  // Add active class to the selected icon
}

function validateEmail() {
    const emailInput = document.getElementById('email');
    const errorDiv = document.getElementById('email-error');
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;  // Simple regex for email validation

    if (!regex.test(emailInput.value)) {
        errorDiv.textContent = 'Please enter a valid email address.';
        errorDiv.classList.add('active');
    } else {
        errorDiv.textContent = '';
        errorDiv.classList.remove('active');
    }
}

function formatICNo(input) {
    let value = input.value.replace(/[^0-9]/g, '');  // Remove all non-numeric characters
    if (value.length >= 6) {
        value = value.slice(0, 6) + '-' + value.slice(6);
    }
    if (value.length >= 9) {
        value = value.slice(0, 9) + '-' + value.slice(9);
    }
    input.value = value.slice(0, 14);  // Ensure the length does not exceed 14 characters

    // Autofill the date of birth field based on the first 6 digits of IC No.
    if (value.length >= 6) {
        const dobStr = value.slice(0, 6);
        const year = parseInt(dobStr.slice(0, 2), 10) + 2000;  // Assume 2000s for simplicity
        const month = dobStr.slice(2, 4);
        const day = dobStr.slice(4, 6);
        document.getElementById('dob').value = `${day}-${month}-${year % 100}`;
    }
}

function validatePassword() {
    const passwordInput = document.getElementById('password').value;
    const minLength = document.getElementById('min-length');
    const uppercase = document.getElementById('uppercase');
    const numeric = document.getElementById('numeric');
    const specialChar = document.getElementById('special-char');

    // Check for minimum length
    if (passwordInput.length >= 8) {
        minLength.classList.add('valid');
    } else {
        minLength.classList.remove('valid');
    }

    // Check for uppercase letter
    if (/[A-Z]/.test(passwordInput)) {
        uppercase.classList.add('valid');
    } else {
        uppercase.classList.remove('valid');
    }

    // Check for numeric digit
    if (/[0-9]/.test(passwordInput)) {
        numeric.classList.add('valid');
    } else {
        numeric.classList.remove('valid');
    }

    // Check for special character
    if (/[!@#$%^&*(),.?":{}|<>]/.test(passwordInput)) {
        specialChar.classList.add('valid');
    } else {
        specialChar.classList.remove('valid');
    }
}
async function onPostalCodeChange() {
    const postalCode = document.getElementById('postal_code').value;
    if (postalCode.length === 5) { // Assuming postal codes are 5 digits
        const locationDetails = await fetchLocationDetails(postalCode);
        document.getElementById('city').value = locationDetails.city;
        document.getElementById('district').value = locationDetails.district;
        document.getElementById('state').value = locationDetails.state;
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
            district: place['state abbreviation'],
            state: place['state']
        };
    } catch (error) {
        console.error('Failed to fetch location details:', error);
        return { city: '', district: '', state: '' };
    }
}
