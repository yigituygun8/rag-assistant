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

function renderFormattedContent(content, messageId) {
  if (!content) return null;

  // Split text by bracket citations like [1], [2], [1][2], [1, 2]
  const regex = /(\[\d+(?:[,\s]*\d+)*\])/g;
  const parts = content.split(regex);

  return (
    <div className="message-body">
      {parts.map((part, index) => {
        const citationMatch = part.match(/^\[([\d,\s]+)\]$/);
        if (citationMatch) {
          const numbers = citationMatch[1]
            .split(/[\s,]+/)
            .filter(Boolean)
            .map((num) => parseInt(num, 10))
            .filter((num) => !isNaN(num));

          return (
            <span key={index} className="citation-badges-wrapper">
              {numbers.map((num) => (
                <button
                  key={num}
                  type="button"
                  className="citation-badge"
                  title={`View Source [${num}]`}
                  onClick={() => {
                    const el = document.getElementById(`source-${messageId}-${num}`);
                    if (el) {
                      el.open = true;
                      el.scrollIntoView({ behavior: "smooth", block: "nearest" });
                    }
                  }}
                >
                  [{num}]
                </button>
              ))}
            </span>
          );
        }

        // Render plain text preserving line breaks
        return <span key={index}>{part}</span>;
      })}
    </div>
  );
}

function App() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [draft, setDraft] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [lastError, setLastError] = useState("");
  const listRef = useRef(null);

  const hasMockedAnswer = useMemo(() => {
    const assistantMessages = messages.filter((message) => message.role === "assistant");
    if (assistantMessages.length === 0) {
      return false;
    }
    return !!assistantMessages[assistantMessages.length - 1].meta?.mocked;
  }, [messages]);

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
                {message.role === "assistant" ? (
                  renderFormattedContent(message.content, message.id)
                ) : (
                  <p>{message.content}</p>
                )}

                {Array.isArray(message.sources) && message.sources.length > 0 && (
                  <div className="source-list">
                    <div className="source-list-header">
                      <span>Sources & Citations:</span>
                    </div>
                    {message.sources.map((src, index) => {
                      const id = src.id || index + 1;
                      const sourceName = src.source || src;
                      const page = src.page_number;
                      const content = src.content;

                      return (
                        <details
                          className="source-detail"
                          id={`source-${message.id}-${id}`}
                          key={index}
                        >
                          <summary className="source-pill">
                            <span className="source-id-badge">[{id}]</span>
                            <span className="source-filename">{sourceName}</span>
                            {page && (
                              <span className="source-page-badge">Page {page}</span>
                            )}
                          </summary>
                          {content && (
                            <div className="source-content">
                              {content}
                            </div>
                          )}
                        </details>
                      );
                    })}
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
            Running in fallback mode because the backend is currently unreachable.
          </p>
        )}

        <p className="footer-text">
          Made By Osman Yiğit Uygun: <a href="https://github.com/yigituygun8">GitHub</a> | <a href="https://www.linkedin.com/in/osmanyigituygun8/">LinkedIn</a>
        </p>
      </main>
    </div>
  );
}

export default App;
