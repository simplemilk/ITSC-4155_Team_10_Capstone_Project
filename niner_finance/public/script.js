const warningModal = document.getElementById('warning-model');
const closeBtn = document.querySelector('.close-btn');
const confirmBtn = document.getElementById('confirm-btn');
const updateBtn = document.getElementById('update-btn');

const weeklyBudgetInput = document.getElementById('weekly-budget');
const weeklyExpensesInput = document.getElementById('weekly-expenses');
const weeklySavings = document.getElementById('weekly-savings');

function showWarning() {
  warningModal.style.display = 'flex';
}

function updateBudget() {
  const budget = parseFloat(weeklyBudgetInput.value);
  const expenses = parseFloat(weeklyExpensesInput.value);
  const savings = budget - expenses;

  weeklySavings.textContent = savings;

  if (expenses > budget) {
    showWarning();
  }
}

// Event listeners
updateBtn.onclick = updateBudget;

closeBtn.onclick = function() {
  warningModal.style.display = 'none';
}

confirmBtn.onclick = function() {
  alert("Confirmed!");
  warningModal.style.display = 'none';
}
