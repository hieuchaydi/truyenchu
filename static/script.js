// src.js

// Function to toggle password visibility with an icon
const togglePasswordVisibility = (id) => {
    const passwordField = document.getElementById(id);
    const toggleIcon = document.getElementById(`toggle_${id}`);
    
    if (passwordField.type === "password") {
        passwordField.type = "text";
        toggleIcon.textContent = "🙈";  // Show "hide" icon
    } else {
        passwordField.type = "password";
        toggleIcon.textContent = "👁️";  // Show "show" icon
    }
};

// Function to validate form passwords
const validateForm = () => {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password');
    
    if (confirmPassword && password !== confirmPassword.value) {
        alert("Passwords do not match!");
        return false;
    }
    return true;
};

// Function to show confirmation dialog
const confirmAction = async (message = "Are you sure you want to proceed?") => {
    return new Promise((resolve) => {
        const confirmed = confirm(message);
        resolve(confirmed);
    });
};

// Initialize event listeners once the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', () => {
            const fieldId = btn.dataset.field;
            togglePasswordVisibility(fieldId);
        });
    });

    // Form validation
    document.querySelectorAll('form.needs-validation').forEach(form => {
        form.addEventListener('submit', (event) => {
            if (!validateForm()) event.preventDefault();
        });
    });

    // Confirmation before deleting or any dangerous action
    document.querySelectorAll('.confirm-action').forEach(btn => {
        btn.addEventListener('click', async (event) => {
            const confirmed = await confirmAction(btn.dataset.message);
            if (!confirmed) event.preventDefault();
        });
    });
});
