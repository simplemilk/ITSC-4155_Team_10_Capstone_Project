import React, { useEffect, useState } from "react";
import "./Home.css";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

function Home() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/api/finance/summary")
      .then((res) => res.json())
      .then((data) => setSummary(data))
      .catch((err) => console.error("Error fetching summary:", err));
  }, []);

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

  return (
    <div className="Home">
      

      {/* Main Content */}
      <main className="main-content">
        <h1>Welcome</h1>
        <p>Here is your summary report:</p>

        {!summary ? (
          <p>Loading...</p>
        ) : (
          <>
            {/* Summary Boxes */}
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

            {/* Charts Section */}
            <section id="visuals">
              <h2>Spending by Category</h2>
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

              <h2>Savings Progress</h2>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{
                    width: `${(summary.totalIncome / (summary.totalIncome + summary.totalExpenses)) * 100}%`,
                  }}
                >
                  {(summary.totalIncome / (summary.totalIncome + summary.totalExpenses) * 100).toFixed(1)}%
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