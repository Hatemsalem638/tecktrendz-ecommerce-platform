import { useState } from "react";

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { sender: "user", text: input }]);

    const res = await fetch("http://localhost:5000/api/chatbot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: input }),
    });

    const data = await res.json();
    setMessages((prev) => [...prev, { sender: "bot", text: data.reply }]);
    setInput("");
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded-full shadow-md hover:bg-blue-700 focus:outline-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? "Close Chat" : "Chat"}
      </button>

      {isOpen && (
        <div className="mt-2 w-[300px] bg-background text-foreground border shadow-lg rounded-lg p-4 dark:bg-[#1f2937] dark:text-white">
          <div className="overflow-y-auto h-64 mb-2">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`text-sm my-1 ${
                  msg.sender === "user"
                    ? "text-right text-foreground"
                    : "text-left text-blue-400"
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>
          <div className="flex">
            <input
              type="text"
              className="flex-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-black dark:text-white rounded-l px-2 py-1"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Say something..."
            />
            <button
              onClick={sendMessage}
              className="bg-blue-500 text-white px-3 py-1 rounded-r hover:bg-blue-600"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chatbot;
