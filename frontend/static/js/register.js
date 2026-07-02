document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('register-form');
  const button = document.getElementById('register-btn');
  const messageBox = document.getElementById('form-message');

  function showMessage(text, type = 'error') {
    messageBox.textContent = text;
    messageBox.className = `message ${type}`;
  }

  function clearMessage() {
    messageBox.textContent = '';
    messageBox.className = 'message';
  }

  function validateForm() {
    const full_name = document.getElementById('full_name').value.trim();
    const company = document.getElementById('company').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    if (!full_name || !company || !email || !password || !confirmPassword) {
      showMessage('Please fill in all required fields.');
      return false;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email)) {
      showMessage('Please enter a valid work email address.');
      return false;
    }

    if (password.length < 8) {
      showMessage('Password must be at least 8 characters long.');
      return false;
    }

    if (password !== confirmPassword) {
      showMessage('Password and confirm password must match.');
      return false;
    }

    clearMessage();
    return true;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const full_name = document.getElementById('full_name').value.trim();
    const company = document.getElementById('company').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;

    button.disabled = true;
    button.textContent = 'Creating Account...';
    clearMessage();

    try {
      await APIClient.post('/auth/register', {
        full_name,
        company,
        email,
        password
      });

      showMessage('Recruiter account created successfully. Redirecting to Login...', 'success');

      setTimeout(() => {
        window.location.href = 'login.html';
      }, 2000);
    } catch (err) {
      button.disabled = false;
      button.textContent = 'Create Recruiter Account';
      showMessage(err.message || 'Unable to create recruiter account. Please try again.');
    }
  });
});
