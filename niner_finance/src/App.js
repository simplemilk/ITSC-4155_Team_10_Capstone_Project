import React from "react";
import "./App.css";

function App() {
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

        <div className="summary-container">
          <div className="summary-box">
            <h3>Monthly Expenses</h3>
            <p>$4000</p>
          </div>
          <div className="summary-box">
            <h3>Monthly Savings</h3>
            <p>$2500</p>
          </div>
        </div>
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

