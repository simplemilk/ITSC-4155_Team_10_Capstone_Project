import React, { useState } from 'react';
import { Link, Outlet } from 'react-router-dom';
import './Register.css';

export default function Register() {
  const [form, setForm] = useState({ email: '', username: '', password: '', favoriteColor: '' });
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(false);

  function onChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setMsg('');
    try {
      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      setMsg(data.message || 'Registration complete.');
    } catch {
      setMsg('Error registering.');
    }
    setLoading(false);
  }

  return (
    <div className="register-root">
      <form className="register-form" onSubmit={onSubmit}>
        <h2>Register</h2>
        <label>
          Email
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={onChange}
            required
          />
        </label>
        <label>
          Username
          <input
            name="username"
            type="text"
            value={form.username}
            onChange={onChange}
            required
          />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            value={form.password}
            onChange={onChange}
            required
          />
        </label>
        <label>
          Security Question: What is your favorite color?
          <input
            name="favoriteColor"
            type="text"
            value={form.favoriteColor}
            onChange={onChange}
            required
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
        {msg && (
          <div className={`msg${msg.includes('complete') ? ' success' : ''}`}>
            {msg}
          </div>
        )}
      </form>
    </div>
  );
}