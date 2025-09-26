import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";
import "./Graph.css";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

function Home() {
  const [username, setUsername] = useState('');
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is logged in
    const storedUsername = localStorage.getItem('username');
    
    if (storedUsername) {
      setUsername(storedUsername);
      // For now, use a default userId or fetch it from the backend
      // You can later implement proper user ID storage
      fetchData(1); // Use a default ID temporarily
    } else {
      navigate('/login');
    }
  }, [navigate]);

  const fetchData = async (userId) => {
    try {
      const [transactionsRes, summaryRes] = await Promise.all([
        fetch(`http://localhost:4000/api/transactions/${userId}`),
        fetch(`http://localhost:4000/api/summary/${userId}`)
      ]);
      
      const transactionsData = await transactionsRes.json();
      const summaryData = await summaryRes.json();

      if (transactionsData.success) {
        setTransactions(transactionsData.transactions);
      }
      
      if (summaryData.success) {
        setSummary(summaryData.summary);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      // Fallback to original API call
      try {
        const res = await fetch("/api/finance/summary");
        const data = await res.json();
        setSummary(data);
      } catch (fallbackErr) {
        console.error("Error fetching fallback summary:", fallbackErr);
      }
    }
    setLoading(false);
  };

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  // Calculate percentages and balance
  let expensePercent = 0;
  let savingsPercent = 0;
  let balance = 0;
  if (summary) {
    const totalIncome = parseFloat(summary.totalIncome) || 0;
    const totalExpenses = parseFloat(summary.totalExpenses) || 0;
    const total = totalIncome + totalExpenses;
    expensePercent = total ? (totalExpenses / total) * 100 : 0;
    savingsPercent = total ? (totalIncome / total) * 100 : 0;
    balance = totalIncome - totalExpenses;
  }

  if (loading) {
    return <div className="Home"><p>Loading...</p></div>;
  }

  return (
    <div className="Home">
      {/* Main Content */}
      <main className="main-content">
        <h1>Welcome {username ? username : 'Guest'}</h1>
        <p>Here is your summary report:</p>

        {!summary ? (
          <p>No financial data available.</p>
        ) : (
          <>
            {/* Summary Boxes */}
            <div className="summary-container">
              <div className="summary-box">
                <h3>Monthly Expenses</h3>
                <p>${(parseFloat(summary.totalExpenses) || 0).toFixed(2)}</p>
              </div>
              <div className="summary-box">
                <h3>Monthly Income</h3>
                <p>${(parseFloat(summary.totalIncome) || 0).toFixed(2)}</p>
              </div>
              <div className="summary-box">
                <h3>Balance</h3>
                <p>${(parseFloat(summary.balance) || 0).toFixed(2)}</p>
              </div>
            </div>

            {/* Recent Transactions Section */}
            <div className="transactions-section">
              <h2>Recent Transactions</h2>
              {transactions.length === 0 ? (
                <p>No transactions found.</p>
              ) : (
                <div className="transactions-list">
                  {transactions.slice(0, 5).map(transaction => (
                    <div key={transaction.id} className="transaction-item">
                      <div className="transaction-info">
                        <span className="transaction-description">{transaction.description}</span>
                        <span className="transaction-category">{transaction.category}</span>
                      </div>
                      <div className={`transaction-amount ${transaction.type}`}>
                        {transaction.type === 'income' ? '+' : '-'}${(parseFloat(transaction.amount) || 0).toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>
                )}
            </div>

            {/* Charts Section */}
            <section id="visuals">
              <h2>Spending by Category</h2>
              {summary.categories && summary.categories.length > 0 ? (
                <PieChart width={400} height={300}>
                  <Pie
                    data={summary.categories}
                    dataKey="amount"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    fill="#8884d8"
                    label
                  >
                    {summary.categories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              ) : (
                <p>No category data available.</p>
              )}

              <h2>Savings Progress</h2>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${savingsPercent}%`,
                  }}
                >
                  {savingsPercent.toFixed(1)}%
                </div>
              </div>
            </section>
          </>
        )}
      </main>

      {/* Bottom Navigation */}
      <footer className="footer-nav">
        <a href="#visuals">Visuals</a>
        <a href="#summary">Summary</a>
        <a href="#contact">Contact</a>
      </footer>
    </div>
  );
}

export default Home;