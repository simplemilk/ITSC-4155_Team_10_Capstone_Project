import React, { useEffect, useState } from 'react';
import BudgetInput from 'BudgetInput';
import BudgetTable from 'BudgetTable';
import './BudgetPage.css';

function BudgetPage() {
  const [budget, setBudget] = useState(null);
  const [warning, setWarning] = useState(false);

  // Fetch the budget data when the page loads
  useEffect(() => {
    async function fetchBudget() {
      const response = await fetch('/api/budget/1'); 
      const data = await response.json();
      setBudget(data.budget);
      
      // Check if the budget is running low
      if (data.budget.amount <= 100) { 
        setWarning(true);
      }
    }
    
    fetchBudget();
  }, []);

  return (
    <div className="budget-page">
      <h1>Weekly Budget</h1>
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

      {/* Budget Input Form */}
      <BudgetInput />
    </div>
  );
}

export default BudgetPage;