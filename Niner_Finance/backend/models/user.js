// Simple in-memory user store for demo purposes
const users = [];

module.exports = {
  create({ email, username, password }) {
    const user = { id: users.length + 1, email, username, password };
    users.push(user);
    return user;
  },
  findByEmail(email) {
    return users.find(u => u.email === email);
  },
  // Add more methods as needed
};