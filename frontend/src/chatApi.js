const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).trim();

function withTimeout(promise, ms) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Request timed out")), ms)
    ),
  ]);
}

function buildMockAnswer(question) {
  return {
    answer:
      "Mock response: I received your question: " +
      question +
      ". Once backend RAG is ready, I will answer with grounded context and sources.",
    sources: [],
    mocked: true,
  };
}

export async function askAssistant(question) {
  try {
    const response = await withTimeout(
      fetch(API_BASE_URL + "/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      }),
      12000
    );

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
    if (error instanceof TypeError || /timed out/i.test(error.message)) {
      return buildMockAnswer(question);
    }
    throw error;
  }
}