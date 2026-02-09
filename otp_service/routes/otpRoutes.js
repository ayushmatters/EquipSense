/**
 * OTP Routes
 */

const express = require('express');
const router = express.Router();
const { sendOTP } = require('../controllers/otpController');

// POST /api/otp/send
router.post('/send', sendOTP);

module.exports = router;
