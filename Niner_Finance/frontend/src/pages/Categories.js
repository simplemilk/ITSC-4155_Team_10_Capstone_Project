import React, { useState } from 'react';
import './Categories.css';

export default function Categories() {
  const [type, setType] = useState('expense');
  const [categoryName, setCategoryName] = useState('');
  const [amount, setAmount] = useState('');
  const [date, setDate] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    if (!type || !categoryName || !amount || !date) {
      setError('Please fill in all fields.');
      return;
    }

    // Get userId from localStorage (set during login)
    const userId = localStorage.getItem('userId');
    if (!userId) {
      setError('Please log in first.');
      return;
    }

    try {
      const res = await fetch('/api/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type,
          category: categoryName,
          subcategory: null, // Add this since backend expects it
          amount: parseFloat(amount),
          date,
          userId: parseInt(userId) // Add userId here
        })
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess('Transaction saved!');
        // Trigger home page refresh
        window.dispatchEvent(new CustomEvent('transactionAdded'));
        setType('expense');
        setCategoryName('');
        setAmount('');
        setDate('');
      } else {
        setError(data.error || 'Failed to save transaction.');
      }
    } catch {
      setError('Failed to save transaction.');
    }
  };

  return (
    <div className="categories-root">
      <h1>Add Transaction</h1>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}
      <form className="categories-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <label>
            Type:
            <select value={type} onChange={e => setType(e.target.value)}>
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>
          </label>
        </div>
        <div className="form-row">
          <label>
            Category Name:
            <input
              type="text"
              value={categoryName}
              onChange={e => setCategoryName(e.target.value)}
              placeholder="Enter category name"
              required
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Amount:
            <input
              type="number"
              value={amount}
              onChange={e => setAmount(e.target.value)}
              min="0"
              step="0.01"
              required
            />
          </label>
        </div>
        <div className="form-row">
          <label>
            Date:
            <input
              type="date"
              value={date}
              onChange={e => setDate(e.target.value)}
              required
            />
          </label>
        </div>
        <button className="submit-btn" type="submit">Submit</button>
      </form>
    </div>
  );
}