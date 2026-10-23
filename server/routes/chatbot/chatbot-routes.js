const express = require("express");
const { spawn } = require("child_process");
const path = require("path");

const router = express.Router();

router.post("/", (req, res) => {
  const userMessage = req.body.message;
  console.log("[Node] User input:", userMessage);  

  const scriptPath = path.join(__dirname, "../../Chatbot/chatbot.py");
  const scriptDir = path.dirname(scriptPath);
  

  const child = spawn("python", ["-u", scriptPath], { cwd: scriptDir });

  let botReply = "";

  child.stdout.on("data", (chunk) => {
    botReply += chunk.toString();
    console.log("[Node] Python output:", chunk.toString());  
  });

  child.stderr.on("data", (errChunk) => {
    console.error("[Node] Python stderr:", errChunk.toString());  
  });

  child.on("error", (err) => {
    console.error("Failed to start subprocess:", err);
    res.status(500).send("Bot error");
  });

  child.on("close", (code) => {
    console.log(`[Node] Python process exited with code ${code}`);  
    if (botReply) {
      res.json({ reply: botReply.trim() });
    } else {
      res.json({ reply: "(No response)" });
    }
  });

  // Send the user input and end stdin
  child.stdin.write(userMessage + "\n");
  child.stdin.end();
});

module.exports = router;
