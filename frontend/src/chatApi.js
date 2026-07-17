const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).trim();

function buildMockAnswer(question, reason) {
  console.warn(`[askAssistant] falling back to mock. reason: ${reason}`);
  return {
    answer:
      "Mock response: I received your question: " +
      question +
      ". Once backend RAG is ready, I will answer with grounded context and sources.",
    sources: [],
    mocked: true,
  };
}

export async function askAssistant(question, { timeoutMs = 60000 } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(API_BASE_URL + "/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error("Backend returned status " + response.status);
    }

    const data = await response.json();
    return {
      answer: data.answer || "No answer returned by backend.",
      sources: Array.isArray(data.sources) ? data.sources : [],
      mocked: false,
    };
  } catch (error) {
    if (error.name === "AbortError") {
      return buildMockAnswer(question, `request exceeded ${timeoutMs}ms`);
    }
    if (error instanceof TypeError) {
      return buildMockAnswer(
        question,
        `network error, is the backend actually running at ${API_BASE_URL}? check CORS too`
      );
    }
    // bad JSON, non-2xx status, anything else: this is a real bug, don't hide it
    throw error;
  } finally {
    clearTimeout(timer);
  }
}