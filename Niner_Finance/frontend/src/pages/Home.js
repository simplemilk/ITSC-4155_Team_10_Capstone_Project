import React, { useEffect, useState } from 'react';
import './Home.css';

export default function Home() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    fetch('/api/summary')
      .then(res => res.json())
      .then(data => setSummary(data))
      .catch(() => setError('Failed to load summary.'));
  }, [refreshKey]); // Refetch when refreshKey changes

  // Listen for custom events when transactions are added
  useEffect(() => {
    const handleTransactionAdded = () => {
      setRefreshKey(prev => prev + 1);
    };
    
    window.addEventListener('transactionAdded', handleTransactionAdded);
    return () => window.removeEventListener('transactionAdded', handleTransactionAdded);
  }, []);

  // Format currency properly
  const formatCurrency = (amount) => {
    return `$${Number(amount).toFixed(2)}`;
  };

  // Format date properly
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  if (error) return <div className="home-root"><div className="error">{error}</div></div>;
  if (!summary) return <div className="home-root"><div className="loading">Loading...</div></div>;

  return (
    <div className="home-root">
      <h1 className="home-title">Finance Summary</h1>
      <div className="summary-cards">
        <div className="summary-card income">
          <h3>Total Income</h3>
          <p className="amount">{formatCurrency(summary.totalIncome)}</p>
        </div>
        <div className="summary-card expenses">
          <h3>Total Expenses</h3>
          <p className="amount">{formatCurrency(summary.totalExpenses)}</p>
        </div>
        <div className="summary-card balance">
          <h3>Balance</h3>
          <p className="amount">{formatCurrency(summary.balance)}</p>
        </div>
      </div>
      
      <div className="section">
        <h2 className="section-title">Expenses by Category</h2>
        <ul className="category-list">
          {summary.categories.map(cat => (
            <li key={cat.name} className="category-item">
              <span className="category-name">{cat.name}</span>
              <span className="category-amount">{formatCurrency(cat.amount)}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="section">
        <h2 className="section-title">Recent Transactions</h2>
        <ul className="transaction-list">
          {summary.recent.map(tx => (
            <li key={tx.id} className={`transaction-item ${tx.type}`}>
              <span className="transaction-date">[{formatDate(tx.date)}]</span>
              <span className="transaction-type">{tx.type}</span>
              <span className="transaction-category">{tx.category}</span>
              <span className="transaction-amount">{formatCurrency(tx.amount)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}