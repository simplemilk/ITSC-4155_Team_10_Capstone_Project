import React from "react";

export default function BudgetTable({ budgets, deleteBudget }) {
  const total = budgets.reduce((sum, b) => sum + b.amount, 0);

  return (
    <div className="budget-table">
      <h2>Budgets</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Amount</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {budgets.map((budget, index) => (
            <tr key={index}>
              <td>{budget.name}</td>
              <td>${budget.amount.toFixed(2)}</td>
              <td>
                <button onClick={() => deleteBudget(index)}>Delete</button>
              </td>
            </tr>
          ))}
          <tr className="total-row">
            <td>Total</td>
            <td>${total.toFixed(2)}</td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
