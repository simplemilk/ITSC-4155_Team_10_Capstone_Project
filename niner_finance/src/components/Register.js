import React, { useState } from 'react';
import './Register.css';

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '', terms: false });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loading, setLoading] = useState(false);

  function onChange(e) {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  }

  function validate() {
    if (!form.name.trim()) return 'Name is required.';
    if (!/\S+@\S+\.\S+/.test(form.email)) return 'Valid email required.';
    if (form.password.length < 8) return 'Password must be at least 8 characters.';
    if (form.password !== form.confirm) return 'Passwords do not match.';
    if (!form.terms) return 'You must accept the terms.';
    return null;
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    const v = validate();
    if (v) return setError(v);
    setLoading(true);
    try {
      const res = await fetch('http://localhost:4000/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: form.name, email: form.email, password: form.password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Registration failed');
      setSuccess('Account created — you can now log in.');
      setForm({ name: '', email: '', password: '', confirm: '', terms: false });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="register-root">
      <form className="register-form" onSubmit={onSubmit}>
        <h2>Create an account</h2>
        {error && <div className="error">{error}</div>}
        {success && <div className="success">{success}</div>}
        <label>
          Name
          <input name="name" value={form.name} onChange={onChange} />
        </label>
        <label>
          Email
          <input name="email" value={form.email} onChange={onChange} />
        </label>
        <label>
          Password
          <input type="password" name="password" value={form.password} onChange={onChange} />
        </label>
        <label>
          Confirm Password
          <input type="password" name="confirm" value={form.confirm} onChange={onChange} />
        </label>
        <label className="terms">
          <input type="checkbox" name="terms" checked={form.terms} onChange={onChange} /> I agree to the terms and conditions
        </label>
        <button type="submit" disabled={loading}>{loading ? 'Creating...' : 'Create Account'}</button>
      </form>
    </div>
  );
}
