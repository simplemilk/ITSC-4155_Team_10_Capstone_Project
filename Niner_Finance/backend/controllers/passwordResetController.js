const bcrypt = require('bcryptjs');
const db = require('../db');

// Change password using email and favorite color
const resetPasswordWithSecurity = async (req, res) => {
  const { email, favoriteColor, newPassword } = req.body;
  if (!email || !favoriteColor || !newPassword) {
    return res.status(400).json({ message: 'Email, favorite color, and new password required.' });
  }
  try {
    const [rows] = await db.query(
      'SELECT * FROM users WHERE email = ? AND favoriteColor = ?',
      [email, favoriteColor]
    );
    if (rows.length === 0) {
      return res.status(404).json({ message: 'User not found or security answer incorrect.' });
    }
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    await db.query(
      'UPDATE users SET password = ? WHERE email = ?',
      [hashedPassword, email]
    );
    return res.json({ success: true, message: 'Password has been reset.' });
  } catch (err) {
    console.error('Reset error:', err);
    return res.status(500).json({ message: 'Database error.' });
  }
};

module.exports = {
  resetPasswordWithSecurity
};

// TODO: Implement password reset with email
// const nodemailer = require('nodemailer');

// const transporter = nodemailer.createTransport({
//   service: 'gmail',
//   auth: {
//     user: process.env.EMAIL_USER, // from .env
//     pass: process.env.EMAIL_PASS, // from .env
//   },
// });

// async function sendResetEmail(to, token) {
//   const resetLink = `http://localhost:3000/reset-password/${token}`;
//   const mailOptions = {
//     from: process.env.EMAIL_USER,
//     to,
//     subject: 'Password Reset',
//     html: `<p>Click <a href="${resetLink}">here</a> to reset your password.</p>`,
//   };
//   try {
//     await transporter.sendMail(mailOptions);
//     return true;
//   } catch (err) {
//     console.error('Email send error:', err);
//     return false;
//   }
// }