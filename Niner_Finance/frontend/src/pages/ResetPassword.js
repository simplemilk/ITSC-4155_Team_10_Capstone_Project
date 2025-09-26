import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './ResetPassword.css';

function ResetPasswordPage() {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email;
  const favoriteColor = location.state?.favoriteColor;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');

    if (newPassword !== confirmPassword) {
      setMessage('Passwords do not match.');
      return;
    }

    if (newPassword.length < 6) {
      setMessage('Password must be at least 6 characters long.');
      return;
    }

    if (!email || !favoriteColor) {
      setMessage('Session expired. Please restart the password reset process.');
      return;
    }

    try {
      const res = await fetch('http://localhost:4000/api/reset-password-security', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, favoriteColor, newPassword }),
      });
      const data = await res.json();
      setMessage(data.message || 'Password has been reset.');
      
      if (data.success) {
        setTimeout(() => navigate('/login'), 2000);
      }
    } catch (err) {
      console.error('Error resetting password:', err);
      setMessage('Error resetting password.');
    }
  };

  return (
    <div className="reset-password-container">
      <form className="reset-password-form" onSubmit={handleSubmit}>
        <h2>Reset Password</h2>
        
        <div className="form-group">
          <label>New Password:</label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            minLength="6"
            placeholder="Enter new password"
          />
        </div>

        <div className="form-group">
          <label>Confirm Password:</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength="6"
            placeholder="Confirm new password"
          />
        </div>

        <button type="submit">Reset Password</button>

        {message && (
          <div className={`message ${message.includes('successfully') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </form>
    </div>
  );
}

export default ResetPasswordPage;