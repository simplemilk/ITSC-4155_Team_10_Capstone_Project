import React, { useEffect, useState } from 'react';
import BudgetInput from 'BudgetInput';
import BudgetTable from 'BudgetTable';
import './BudgetPage.css';

function BudgetPage() {
  const [budget, setBudget] = useState(null);
  const [warning, setWarning] = useState(false);

  const [gameData, setGameData] = useState({
    points: 0,
    level: 1,
    current_streak: 0
  });

  useEffect(() => {
    async function fetchAll() {
      // Fetch budget info
      const resBudget = await fetch('/api/budget/1');
      const dataBudget = await resBudget.json();

      setBudget(dataBudget.budget);

      if (dataBudget.budget.amount <= 100) {
        setWarning(true);
      }

      const resGame = await fetch('/api/game/user/1');
      const dataGame = await resGame.json();

      setGameData(dataGame);
    }

    fetchAll();
  }, []);

  async function awardBudgetPoints() {
    const res = await fetch("/api/game/complete-budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: 1 })
    });

    const data = await res.json();
    console.log("Gamification:", data);

    const resGame = await fetch("/api/game/user/1");
    const updated = await resGame.json();
    setGameData(updated);
  }


  return (
    <div className="budget-page">
      <h1>Weekly Budget</h1>

      <div className="game-box">
        <p>⭐ Level: {gameData.level}</p>
        <p>🔥 Points: {gameData.points}</p>
        <p>⏳ Streak: {gameData.current_streak} days</p>
      </div>

      {warning && <div className="warning">Warning: You are about to run out of your budget!</div>}

      {budget ? (
        <div className="budget-summary">
          <p>Weekly Budget: ${budget.amount}</p>
          <p>Weekly Income: ${budget.income}</p>
          <p>Weekly Expenses: ${budget.expenses}</p>
          <p>Weekly Savings: ${budget.savings}</p>
        </div>
      ) : (
        <p>Loading your budget...</p>
      )}

      <BudgetInput onBudgetSubmit={awardBudgetPoints} />
    </div>
  );
}

export default BudgetPage;
