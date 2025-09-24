const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const nodemailer = require('nodemailer');
// TODO: Import User model when MySQL is set up
// const User = require('../models/User');

// Temporary in-memory storage for development
// This will be replaced with MySQL queries
const tempUsers = new Map();

const testEmail = 'insert-email';
const testPassword = 'password123';

const hashedPassword = bcrypt.hashSync(testPassword, 10);
tempUsers.set(testEmail, {
  email: testEmail,
  password: hashedPassword,
  resetToek: null,
  resetTokenExpiration: null
});

const requestPasswordReset = async (req, res) => {
  try {
    const { email } = req.body;

    // Validate email
    if (!email || !email.includes('@')) {
      return res.status(400).json({ 
        success: false, 
        message: 'Valid email is required' 
      });
    }

    // TODO: Replace with MySQL query when database is set up
    // const user = await User.findOne({ where: { email } });
    // For now, simulate user lookup
    const user = tempUsers.get(email) || { email, password: 'hashedpassword' };
    
    if (!user) {
      return res.status(404).json({ 
        success: false, 
        message: 'User not found' 
      });
    }

    const resetToken = crypto.randomBytes(32).toString('hex');
    const resetTokenExpiration = Date.now() + 3600000; // 1 hour

    // TODO: Replace with MySQL update when database is set up
    // await User.update(
    //   { resetToken, resetTokenExpiration },
    //   { where: { email } }
    // );
    
    // Store token temporarily for development
    tempUsers.set(email, { ...user, resetToken, resetTokenExpiration });

    // Email configuration - update with actual credentials
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.EMAIL_USER || 'your-email@gmail.com',
        pass: process.env.EMAIL_PASS || 'your-app-password',
      },
    });

    const resetLink = `http://localhost:3000/reset-password/${resetToken}`;
    const mailOptions = {
      from: process.env.EMAIL_USER || 'your-email@gmail.com',
      to: email,
      subject: 'Password Reset Request - Niner Finance',
      html: `
        <h2>Password Reset Request</h2>
        <p>You requested a password reset for your Niner Finance account.</p>
        <p>Click the following link to reset your password:</p>
        <a href="${resetLink}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this reset, please ignore this email.</p>
      `,
    };

    transporter.sendMail(mailOptions, (error, info) => {
      if (error) {
        console.error('Email error:', error);
        return res.status(500).json({ 
          success: false, 
          message: 'Error sending email' 
        });
      }
      res.status(200).json({ 
        success: true, 
        message: 'Password reset email sent successfully' 
      });
    });
  } catch (error) {
    console.error('Request password reset error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Internal server error' 
    });
  }
};

const resetPassword = async (req, res) => {
  try {
    const { token } = req.params;
    const { newPassword } = req.body;

    // Validate password
    if (!newPassword || newPassword.length < 6) {
      return res.status(400).json({ 
        success: false, 
        message: 'Password must be at least 6 characters long' 
      });
    }

    // TODO: Replace with MySQL query when database is set up
    // const user = await User.findOne({ where: { resetToken: token } });
    
    // Find user by token in temporary storage
    let user = null;
    for (let [email, userData] of tempUsers.entries()) {
      if (userData.resetToken === token) {
        user = userData;
        break;
      }
    }

    if (!user || user.resetTokenExpiration < Date.now()) {
      return res.status(400).json({ 
        success: false, 
        message: 'Invalid or expired token' 
      });
    }

    const hashedPassword = await bcrypt.hash(newPassword, 10);
    
    // TODO: Replace with MySQL update when database is set up
    // await User.update(
    //   { 
    //     password: hashedPassword, 
    //     resetToken: null, 
    //     resetTokenExpiration: null 
    //   },
    //   { where: { resetToken: token } }
    // );
    
    // Update temporary storage
    tempUsers.set(user.email, {
      ...user,
      password: hashedPassword,
      resetToken: null,
      resetTokenExpiration: null
    });

    res.status(200).json({ 
      success: true, 
      message: 'Password has been reset successfully' 
    });
  } catch (error) {
    console.error('Reset password error:', error);
    res.status(500).json({ 
      success: false, 
      message: 'Internal server error' 
    });
  }
};

module.exports = {
  requestPasswordReset,
  resetPassword,
};
