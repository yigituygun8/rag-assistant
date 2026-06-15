import { useState } from "react";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleAsk() {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      setAnswer("Error reaching backend: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Local RAG Assistant</h1>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleAsk()}
        placeholder="Ask a question..."
        style={{ width: "100%", padding: 8, boxSizing: "border-box" }}
      />
      <button onClick={handleAsk} disabled={loading} style={{ marginTop: 8 }}>
        {loading ? "Thinking..." : "Ask"}
      </button>
      {answer && <p style={{ marginTop: 16 }}>{answer}</p>}
    </div>
  );
}

export default App;
