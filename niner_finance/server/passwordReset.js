const express = require('express');
const router = express.Router();
const { requestPasswordReset, resetPassword } = require('./passwordResetController');

router.post('/request-reset', requestPasswordReset);

router.post('/reset-password/:token', resetPassword);

module.exports = router;
