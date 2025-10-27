<<<<<<< HEAD
import React, { useState } from 'react';

function BudgetInput() {
  const [amount, setAmount] = useState('');
  const [weekStartDate, setWeekStartDate] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const user_id = 1;

    const response = await fetch('/api/budget', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id, amount, week_start_date: weekStartDate }),
    });

    const data = await response.json();

    if (response.ok) {
      setMessage('Budget saved successfully!');
    } else {
      setMessage(data.error || 'Error saving budget');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Weekly Budget Amount: </label>
        <input
          type="number"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
      </div>

      <div>
        <label>Week Start Date: </label>
        <input
          type="date"
          value={weekStartDate}
          onChange={(e) => setWeekStartDate(e.target.value)}
          required
        />
      </div>

      <button type="submit">Set Budget</button>

      {message && <p>{message}</p>}
    </form>
  );
}

export default BudgetInput;
=======
import React, { useState } from 'react';

function BudgetInput() {
  const [amount, setAmount] = useState('');
  const [weekStartDate, setWeekStartDate] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const user_id = 1;

    const response = await fetch('/api/budget', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id, amount, week_start_date: weekStartDate }),
    });

    const data = await response.json();

    if (response.ok) {
      setMessage('Budget saved successfully!');
    } else {
      setMessage(data.error || 'Error saving budget');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Weekly Budget Amount: </label>
        <input
          type="number"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
      </div>

      <div>
        <label>Week Start Date: </label>
        <input
          type="date"
          value={weekStartDate}
          onChange={(e) => setWeekStartDate(e.target.value)}
          required
        />
      </div>

      <button type="submit">Set Budget</button>

      {message && <p>{message}</p>}
    </form>
  );
}

export default BudgetInput;
>>>>>>> c663b277920c15a2a6b669ad40363a728377b600
