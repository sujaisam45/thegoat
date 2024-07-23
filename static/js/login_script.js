document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the form from submitting through the browser

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/'; // Redirect to home page on successful login
        } else {
            // Display an error message if login is unsuccessful
            const alertDiv = document.getElementById('alert');
            alertDiv.textContent = 'Invalid email or password. Please try again.';
            alertDiv.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        const alertDiv = document.getElementById('alert');
        alertDiv.textContent = 'Server error. Please try again later.';
        alertDiv.style.display = 'block';
    });
});
