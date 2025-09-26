import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Categories.css';

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [type, setType] = useState('expense');
  const [category, setCategory] = useState('');
  const [subcategory, setSubcategory] = useState('');
  const [amount, setAmount] = useState('');
  const [date, setDate] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is logged in
    const userId = localStorage.getItem('userId');
    if (!userId) {
      navigate('/login');
      return;
    }
    fetchCategories();
  }, [navigate]);

  const fetchCategories = async () => {
    try {
      const res = await fetch('http://localhost:4000/api/categories');
      const data = await res.json();
      if (data.success) {
        setCategories(data.categories || []);
      }
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setLoading(true);

    const userId = localStorage.getItem('userId');
    if (!userId) {
      setMessage('Please log in to add transactions.');
      setLoading(false);
      return;
    }

    try {
      const res = await fetch('http://localhost:4000/api/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type,
          category,
          subcategory,
          amount: parseFloat(amount),
          date,
          userId: parseInt(userId)
        })
      });

      const data = await res.json();
      if (data.success) {
        setMessage('Transaction added successfully!');
        // Clear form
        setCategory('');
        setSubcategory('');
        setAmount('');
        setDate('');
      } else {
        setMessage(data.error || 'Failed to add transaction.');
      }
    } catch (err) {
      console.error('Error adding transaction:', err);
      setMessage('Error adding transaction.');
    }
    setLoading(false);
  };

  return (
    <div className="categories-container">
      <h1>Add Transaction</h1>
      
      <form onSubmit={handleSubmit} className="transaction-form">
        <div className="form-group">
          <label>Type:</label>
          <select 
            value={type} 
            onChange={(e) => setType(e.target.value)}
            required
          >
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
        </div>

        <div className="form-group">
          <label>Category:</label>
          <select 
            value={category} 
            onChange={(e) => setCategory(e.target.value)}
            required
          >
            <option value="">Select a category</option>
            {categories
              .filter(cat => cat.type === type)
              .map(cat => (
                <option key={cat.id} value={cat.name}>
                  {cat.name}
                </option>
              ))
            }
          </select>
        </div>

        <div className="form-group">
          <label>Subcategory (Optional):</label>
          <input
            type="text"
            value={subcategory}
            onChange={(e) => setSubcategory(e.target.value)}
            placeholder="e.g., Groceries, Gas, etc."
          />
        </div>

        <div className="form-group">
          <label>Amount:</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            required
          />
        </div>

        <div className="form-group">
          <label>Date:</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Adding...' : 'Add Transaction'}
        </button>
      </form>

      {message && (
        <div className={`message ${message.includes('success') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      <div className="available-categories">
        <h2>Available Categories</h2>
        <div className="category-lists">
          <div className="income-categories">
            <h3>Income Categories</h3>
            <ul>
              {categories
                .filter(cat => cat.type === 'income')
                .map(cat => (
                  <li key={cat.id}>{cat.name}</li>
                ))
              }
            </ul>
          </div>
          <div className="expense-categories">
            <h3>Expense Categories</h3>
            <ul>
              {categories
                .filter(cat => cat.type === 'expense')
                .map(cat => (
                  <li key={cat.id}>{cat.name}</li>
                ))
              }
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}