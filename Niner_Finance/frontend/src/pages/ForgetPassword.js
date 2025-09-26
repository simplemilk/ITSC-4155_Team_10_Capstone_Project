import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './ForgetPassword.css';

function ForgetPassword() {
  const [email, setEmail] = useState('');
  const [favoriteColor, setFavoriteColor] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
  e.preventDefault();
  setMessage('');
  try {
    const res = await fetch('http://localhost:4000/api/verify-security', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, favoriteColor }),
    });
    const data = await res.json();
    if (data.success) {
      navigate('/reset-password', { state: { email, favoriteColor } });
    } else {
      setMessage(data.message || 'Incorrect email or security answer.');
    }
  } catch (err) {
    console.error('Error verifying security answer:', err);
    setMessage('Error verifying security answer.');
  }
};

  const handleCancel = () => {
    navigate(-1);
  };

  return (
    <div className="forgot-password-container">
      <h2>Verify Security Question</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Email:
          <input
            type="email"
            value={email}
            required
            onChange={e => setEmail(e.target.value)}
          />
        </label>
        <label>
          Security Question: What is your favorite color?
          <input
            type="text"
            value={favoriteColor}
            required
            onChange={e => setFavoriteColor(e.target.value)}
          />
        </label>
        <button type="submit">Next</button>
        <button type="button" onClick={handleCancel}>
          Cancel
        </button>
      </form>
      {message && <p style={{ marginTop: 15 }}>{message}</p>}
    </div>
  );
}

export default ForgetPassword;