const warningModel = document.getElementById('warning-model');
const closeBtn = document.querySelector('.close-btn');
const confirmBtn = document.getElementById('confirm-btn');
const updateBtn = document.getElementById('update-btn');
const modelMessage = document.getElementById('model-message');

const weeklyIncomeInput = document.getElementById('weekly-income');
const weeklyExpensesInput = document.getElementById('weekly-expenses');
const weeklySavingsInput = document.getElementById('weekly-savings');
const weeklyBudgetDisplay = document.getElementById('weekly-budget');

function showModel(message) {
  modelMessage.innerHTML = message;
  warningModel.style.display = 'flex';
}

function updateBudget() {
  const income = parseFloat(weeklyIncomeInput.value) || 0;
  const expenses = parseFloat(weeklyExpensesInput.value) || 0;
  const savings = parseFloat(weeklySavingsInput.value) || 0;

  const remainingBudget = income - (expenses + savings);
  weeklyBudgetDisplay.textContent = remainingBudget.toFixed(2);

  if (remainingBudget < 0) {
    showModel("<strong>Warning!</strong> You have exceeded your budget!");
  } else {
    showModel("✅ Budget confirmed! You still have money left.");
  }
}

updateBtn.onclick = updateBudget;

closeBtn.onclick = function() {
  warningModel.style.display = 'none';
}

confirmBtn.onclick = function() {
  warningModel.style.display = 'none';
}

window.onclick = function(event) {
  if (event.target == warningModel) {
    warningModel.style.display = 'none';
  }
}

async function updateBudget() {
  const income = parseFloat(weeklyIncomeInput.value) || 0;
  const expenses = parseFloat(weeklyExpensesInput.value) || 0;
  const savings = parseFloat(weeklySavingsInput.value) || 0;

  const remainingBudget = income - (expenses + savings);
  weeklyBudgetDisplay.textContent = remainingBudget.toFixed(2);

  // CALL YOUR BACKEND TO AWARD POINTS
  try {
    const res = await fetch("http://127.0.0.1:5000/api/game/complete-budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: 1 })
    });

    const data = await res.json();
    console.log("Gamification Response:", data);

  } catch (err) {
    console.error("Gamification error:", err);
  }

  if (remainingBudget < 0) {
    showModel("<strong>Warning!</strong> You have exceeded your budget!");
  } else {
    showModel("✅ Budget confirmed! You earned points!");
  }
}
