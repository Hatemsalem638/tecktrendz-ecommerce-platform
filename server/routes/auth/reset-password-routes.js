const express = require('express');
const router = express.Router();
const crypto = require('crypto');
const nodemailer = require('nodemailer');
const bcrypt = require('bcryptjs'); 
const User = require('../../models/User'); 

const otpStore = {};

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'your_email@gmail.com',        
    pass: 'your_app_password',           
  },
});

router.post('/request-reset', async (req, res) => {
  const { email } = req.body;
  if (!email) return res.status(400).json({ success: false, message: 'Email is required' });

  const otp = Math.floor(100000 + Math.random() * 900000).toString();
  otpStore[email] = otp;

  try {
    await transporter.sendMail({
      from: 'no-reply@yourapp.com',
      to: email,
      subject: 'Your OTP Code',
      text: `Your OTP for password reset is: ${otp}`,
    });

    return res.json({ success: true, message: 'OTP sent to your email.' });
  } catch (error) {
    console.error("Error sending email:", error);
    return res.status(500).json({ success: false, message: 'Failed to send OTP.' });
  }
});

router.post('/verify-otp', (req, res) => {
  const { email, otp } = req.body;
  if (!email || !otp) {
    return res.status(400).json({ success: false, message: 'Email and OTP are required' });
  }

  if (otpStore[email] === otp) {
    return res.json({ success: true, message: 'OTP verified' });
  }

  return res.status(400).json({ success: false, message: 'Invalid OTP' });
});

router.post('/reset-password', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) {
    return res.status(400).json({ success: false, message: 'Email and password are required' });
  }

  try {
    const user = await User.findOne({ email });
    if (!user) return res.status(404).json({ success: false, message: 'User not found' });

    const hashedPassword = await bcrypt.hash(password, 10);
    user.password = hashedPassword;
    await user.save();

    delete otpStore[email];

    return res.json({ success: true, message: 'Password has been updated.' });
  } catch (error) {
    console.error("Password reset error:", error);
    return res.status(500).json({ success: false, message: 'Failed to reset password.' });
  }
});

module.exports = router;
