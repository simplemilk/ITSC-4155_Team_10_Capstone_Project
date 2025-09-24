import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/api/finance/summary")
      .then((res) => res.json())
      .then((data) => setSummary(data))
      .catch((err) => console.error("Error fetching summary:", err));
  }, []);

  return (
    <div className="App">
      {/* Navbar */}
      <nav className="navbar">
        <div className="nav-left">
          <a href="#visuals">Visuals</a>
          <a href="#summary">Summary</a>
          <a href="#contact">Contact</a>
        </div>
        <div className="nav-right">
          <button className="login-btn">Login</button>
          <button className="register-btn">Register</button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        <h1>Welcome</h1>
        <p>Here is your summary report:</p>

        {!summary ? (
          <p>Loading...</p>
        ) : (
          <div className="summary-container">
            <div className="summary-box">
              <h3>Monthly Expenses</h3>
              <p>${summary.totalExpenses}</p>
            </div>
            <div className="summary-box">
              <h3>Monthly Savings</h3>
              <p>${summary.totalIncome}</p>
            </div>
            <div className="summary-box">
              <h3>Balance</h3>
              <p>${summary.balance}</p>
            </div>
          </div>
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

export default App;
