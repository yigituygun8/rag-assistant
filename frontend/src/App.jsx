import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import { askAssistant } from "./chatApi";

const WELCOME_MESSAGE = {
  id: "welcome",
  role: "assistant",
  content:
    "Hi! I am your local RAG assistant. Ask me anything about your documents.",
  sources: [],
  meta: { mocked: false },
};

function createMessage(role, content, extra = {}) {
  return {
    id: Math.random().toString(36).slice(2),
    role,
    content,
    sources: extra.sources ?? [],
    meta: extra.meta ?? {},
  };
}

function App() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]); // Initialize with the welcome message
  const [draft, setDraft] = useState(""); // State for the current draft message
  const [isSending, setIsSending] = useState(false); // State to track if a message is being sent
  const [lastError, setLastError] = useState("");
  const listRef = useRef(null); // Ref for the chat log container to manage scrolling

  const hasMockedAnswer = useMemo(
    () => messages.some((message) => message.role === "assistant" && message.meta?.mocked),
    [messages]
  ); // useMemo is a React hook that memoizes the result of a computation. In this case, it checks if any assistant message has been mocked, and only recalculates when the messages array changes. Returns true if there is at least one mocked assistant message, otherwise false.

  useEffect(() => {
    if (!listRef.current) {
      return;
    }
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages, isSending]);

  async function handleSend() {
    const question = draft.trim();
    if (!question || isSending) {
      return;
    }

    setLastError("");
    setDraft("");

    const userMessage = createMessage("user", question);
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);

    try {
      const result = await askAssistant(question);
      const assistantMessage = createMessage("assistant", result.answer, {
        sources: result.sources,
        meta: { mocked: result.mocked },
      });
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const assistantMessage = createMessage(
        "assistant",
        "Something went wrong while generating a response. Please try again.",
        { meta: { mocked: false } }
      );
      setMessages((prev) => [...prev, assistantMessage]);
      setLastError(error.message || "Unknown error");
    } finally {
      setIsSending(false);
    }
  }

  function onComposerKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="app-shell">
      <div className="ambient-shape ambient-a" />
      <div className="ambient-shape ambient-b" />

      <main className="chat-card">
        <header className="chat-header">
          <div>
            <p className="eyebrow">Offline first</p>
            <h1>Local RAG Assistant</h1>
          </div>
          <span className="status-chip">{isSending ? "Thinking..." : "Ready"}</span>
        </header>

        <section className="chat-log" ref={listRef}>
          {messages.map((message) => (
            <article
              key={message.id}
              className={"bubble-row " + (message.role === "user" ? "row-user" : "row-assistant")}
            >
              <div
                className={
                  "bubble " + (message.role === "user" ? "bubble-user" : "bubble-assistant")
                }
              >
                <p>{message.content}</p>

                {Array.isArray(message.sources) && message.sources.length > 0 && (
                  <div className="source-list">
                    {message.sources.map((source, index) => (
                      <span className="source-pill" key={index}>
                        {source}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </article>
          ))}

          {isSending && (
            <article className="bubble-row row-assistant">
              <div className="bubble bubble-assistant typing">
                <span />
                <span />
                <span />
              </div>
            </article>
          )}
        </section>

        <footer className="composer-wrap">
          <label htmlFor="composer" className="sr-only">
            Ask a question
          </label>

          <textarea
            id="composer"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={onComposerKeyDown}
            placeholder="Ask about your local documents..."
            rows={2}
            disabled={isSending}
          />

          <div className="composer-actions">
            <small>Enter to send, Shift + Enter for newline</small>
            <button type="button" onClick={handleSend} disabled={isSending || !draft.trim()}>
              {isSending ? "Sending..." : "Send"}
            </button>
          </div>
        </footer>

        {lastError && <p className="error-text">Last error: {lastError}</p>}
        {hasMockedAnswer && (
          <p className="mock-note">
            Running in fallback mode for some responses because backend was unreachable.
          </p>
        )}
      </main>
    </div>
  );
}

export default App;
