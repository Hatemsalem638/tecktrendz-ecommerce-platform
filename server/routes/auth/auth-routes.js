const express = require("express");
const axios = require("axios");
const {
  registerUser,
  loginUser,
  logoutUser,
  authMiddleware,
} = require("../../controllers/auth/auth-controller");

const router = express.Router();

const RECAPTCHA_SECRET_KEY = "6Ld3GR4rAAAAAKlqV5e7wGfht0MMijFSh6d-G7d6"; 

async function verifyCaptcha(token) {
  const url = `https://www.google.com/recaptcha/api/siteverify?secret=${RECAPTCHA_SECRET_KEY}&response=${token}`;
  const { data } = await axios.post(url);
  return data.success;
}

router.post("/register", async (req, res) => {
  const { captcha, ...formData } = req.body;

  if (!captcha) {
    return res.status(400).json({ success: false, message: "CAPTCHA is required." });
  }

  try {
    const isValid = await verifyCaptcha(captcha);
    if (!isValid) {
      return res.status(400).json({ success: false, message: "CAPTCHA verification failed." });
    }

    return registerUser({ body: formData }, res);
  } catch (err) {
    console.error("CAPTCHA validation error:", err.message);
    return res.status(500).json({ success: false, message: "CAPTCHA error. Try again." });
  }
});

router.post("/login", loginUser);
router.post("/logout", logoutUser);

router.get("/check-auth", authMiddleware, (req, res) => {
  const user = req.user;
  res.status(200).json({
    success: true,
    message: "Authenticated user!",
    user,
  });
});

router.post("/guest", (req, res) => {
  const guestUser = {
    id: "guest-" + Date.now(),
    userName: "Guest User",
    email: `guest${Date.now()}@guest.com`,
    isGuest: true,
  };

  res.cookie("token", "dummy-guest-token", {
    httpOnly: true,
    sameSite: "Lax",
  });

  res.status(200).json({
    success: true,
    message: "Signed in as guest",
    user: guestUser,
  });
});

module.exports = router;
