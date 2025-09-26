import React, { useState } from 'react';
import { Link, useNavigate, Outlet } from 'react-router-dom';
import './Login.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const res = await fetch('http://localhost:4000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem('username', username);
        localStorage.setItem('userId', data.userId);
        setMessage('Login successful!');
        // Force navbar to update
        window.dispatchEvent(new Event('storage'));
        navigate('/');
      } else {
        setMessage(data.message || 'Login failed.');
      }
    } catch (err) {
      console.error('Login error:', err);
      setMessage('Login error.');
    }
  };

  return (
    <div className="login-root">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Login</h2>
        <label>
          Username:
          <input
            type="text"
            value={username}
            required
            onChange={e => setUsername(e.target.value)}
          />
        </label>
        <label>
          Password:
          <input
            type="password"
            value={password}
            required
            onChange={e => setPassword(e.target.value)}
          />
          <Link to="/login/forgot-password" className="forgot-link">
            Forgot Password?
          </Link>
        </label>
        <button type="submit">Log In</button>
        {message && (
          <div className={`msg${message === 'Login successful!' ? ' success' : ''}`}>
            {message}
          </div>
        )}
      </form>
      <Outlet />
    </div>
  );
}

export default Login;