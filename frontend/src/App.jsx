import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { saveAs } from "file-saver";
// import "highlight.js/styles/github.css"; // light GitHub-like theme
import "highlight.js/styles/github-dark.css";
import "./App.css";

/** Model metadata: label + tooltip for UX and routing **/
const MODELS = [
  {
    value: "deepseek-coder:6.7b",
    label: "DeepSeek Coder 6.7B",
    tooltip: "Best for code: debugging, writing functions, repo Q&A, error analysis.",
    intent: "code",
  },
  {
    value: "mistral:latest",
    label: "Mistral (latest)",
    tooltip: "Fast general-purpose model. Good balance for most tasks.",
    intent: "general",
  },
  {
    value: "llama3:latest",
    label: "LLaMA 3 (latest)",
    tooltip: "Best for reasoning/explanations and step-by-step thinking.",
    intent: "reasoning",
  },
  {
    value: "openchat:latest",
    label: "OpenChat (latest)",
    tooltip: "Best for conversation, tone, rewriting, and emails.",
    intent: "conversation",
  },
];

function App() {
  /** -------------------- State (with restore on reload) -------------------- */
  const [sessions, setSessions] = useState(() => {
    const saved = localStorage.getItem("chatSessions");
    return saved ? JSON.parse(saved) : [];
  });

  const [history, setHistory] = useState(() => {
    // Prefer restoring a live draft, else last saved session
    const draft = localStorage.getItem("currentChat");
    if (draft) {
      try {
        const parsed = JSON.parse(draft);
        return Array.isArray(parsed.messages) ? parsed.messages : [];
      } catch { /* ignore */ }
    }
    const saved = localStorage.getItem("chatSessions");
    if (saved) {
      const arr = JSON.parse(saved);
      const last = arr[arr.length - 1];
      return last ? last.messages : [];
    }
    return [];
  });

  const [chatTitle, setChatTitle] = useState(() => {
    const draft = localStorage.getItem("currentChat");
    if (draft) {
      try {
        const parsed = JSON.parse(draft);
        return parsed?.name || "";
      } catch { /* ignore */ }
    }
    const saved = localStorage.getItem("chatSessions");
    if (saved) {
      const arr = JSON.parse(saved);
      const last = arr[arr.length - 1];
      return last?.name || "";
    }
    return "";
  });

  const [model, setModel] = useState(() => {
    return localStorage.getItem("currentModel") || "deepseek-coder:6.7b";
  });

  const [query, setQuery] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);

  const chatRef = useRef(null);
  const abortRef = useRef(null);

  /** Tooltip for the current model */
  const currentTooltip =
    MODELS.find((m) => m.value === model)?.tooltip ||
    "Select the model. Hover for its strengths.";

  /** -------------------- Persistence effects -------------------- */
  useEffect(() => {
    localStorage.setItem("chatSessions", JSON.stringify(sessions));
  }, [sessions]);

  useEffect(() => {
    // Save the selected model
    localStorage.setItem("currentModel", model);
  }, [model]);

  useEffect(() => {
    // Persist the current ongoing chat (draft) continuously
    const draft = {
      name: chatTitle || "",
      messages: history || [],
    };
    localStorage.setItem("currentChat", JSON.stringify(draft));
  }, [history, chatTitle]);

  /** -------------------- UI effects -------------------- */
  useEffect(() => {
    document.body.className = darkMode ? "dark-mode" : "";
  }, [darkMode]);

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" });
  }, [history]);

  /** -------------------- Intent router (explicit + heuristics) -------------------- */
  function chooseModelForQuery(q, currentModel) {
    const lowered = q.toLowerCase();

    // Map common directives to model IDs
    const explicitToModel = (name) => {
      switch (name) {
        case "deepseek":
        case "deepseek-coder":
        case "code":
          return "deepseek-coder:6.7b";
        case "mistral":
        case "general":
          return "mistral:latest";
        case "llama3":
        case "reasoning":
          return "llama3:latest";
        case "openchat":
        case "conversation":
        case "chat":
          return "openchat:latest";
        default:
          return null;
      }
    };

    // Explicit commands
    const explicitPatterns = [
      /\[model:\s*([a-z0-9\-:]+)\]/i,
      /\/model\s+([a-z0-9\-:]+)/i,
      /use\s+(best\s+for\s+)?(code|conversation|chat|reasoning|general)/i,
      /#(code|conversation|chat|reasoning|general)/i,
    ];
    
    for (const pat of explicitPatterns) {
      const m = lowered.match(pat);
      if (m) {
        const key = (m[2] || m[1] || "").replace(/[^a-z0-9:.\\-]/g, "");
        const mapped = explicitToModel(key);
        if (mapped) return { model: mapped, reason: "explicit" };
        // Or allow exact model value
        if (MODELS.some((x) => x.value === key)) return { model: key, reason: "explicit" };
      }
    }

    // Heuristics
    const codeHints = [
      "code", "bug", "fix", "refactor", "function", "class", "api",
      "stack trace", "traceback", "error", "exception", "compile",
      ".py", ".js", ".ts", ".java", ".cpp", ".ipynb", "regex", "sql"
    ];
    const conversationHints = ["draft email", "polite", "tone", "rewrite", "chatty", "friendly"];
    const reasoningHints = ["why", "explain", "step by step", "reason", "prove", "derivation"];

    const hasAny = (arr) => arr.some((kw) => lowered.includes(kw));

    if (hasAny(codeHints)) return { model: "deepseek-coder:6.7b", reason: "heuristic" };
    if (hasAny(conversationHints)) return { model: "openchat:latest", reason: "heuristic" };
    if (hasAny(reasoningHints)) return { model: "llama3:latest", reason: "heuristic" };

    return { model: currentModel, reason: "none" };
  }

  /** -------------------- Ask / Stop -------------------- */
  const askQuestion = async () => {
    if (!query.trim() || loading) return;

    const routed = chooseModelForQuery(query, model);
    const modelToUse = routed.model || model;
    if (modelToUse !== model) setModel(modelToUse);

    const userMessage = { role: "user", content: query };
    setHistory((prev) => [...prev, userMessage]);
    setLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    const currentQuery = query;
    setQuery("");

    try {
      const res = await fetch("http://einstein.neurology.emory.edu:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: currentQuery, model: modelToUse }),
        signal: controller.signal,
      });

      const data = await res.json();
      const botMessage = {
        role: "assistant",
        content: data?.response || "⚠️ Unexpected response format.",
      };
      setHistory((prev) => [...prev, botMessage]);
    } catch (err) {
      if (err.name === "AbortError") {
        setHistory((prev) => [...prev, { role: "assistant", content: "⏹️ Stopped." }]);
      } else {
        setHistory((prev) => [...prev, { role: "assistant", content: "❌ Network error: " + err.message }]);
      }
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  /** -------------------- Session helpers -------------------- */
  const saveSession = () => {
    if (history.length === 0) return;
    const title = chatTitle || `Chat @ ${new Date().toLocaleString()}`;
    const session = { name: title, messages: history };
    setSessions((prev) => [...prev, session]);
    setHistory([]);
    setChatTitle("");
    localStorage.removeItem("currentChat"); // clear draft after saving
  };

  const deleteSession = (index) => {
    setSessions(sessions.filter((_, i) => i !== index));
  };

  const exportChat = () => {
    const content = history
      .map((msg) => `${msg.role === "user" ? "You" : "Bot"}:\\n${msg.content}`)
      .join("\\n\\n");
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    saveAs(blob, `${chatTitle || "chat"}.md`);
  };

  /** -------------------- Render -------------------- */
  return (
    <div className="chat-ui">
      <aside className="sidebar">
        <h2 title="Saved Chat Sessions">💬 Chats</h2>

        <button
          title="Start new chat"
          onClick={() => {
            // Auto-save current if not empty
            if (history.length > 0) {
              const title = chatTitle || `Chat @ ${new Date().toLocaleString()}`;
              const session = { name: title, messages: history };
              setSessions((prev) => [...prev, session]);
              setChatTitle("");
            }
            // Clear for new chat
            setHistory([]);
            setQuery("");
            localStorage.removeItem("currentChat"); // start a clean draft
          }}
          className="new-chat-btn"
        >
          ➕ New Chat
        </button>

        <ul>
          {sessions.map((s, i) => (
            <li key={i}>
              <span
                title="Load chat"
                onClick={() => {
                  setHistory(s.messages);
                  setChatTitle(s.name);
                  // also set as current draft immediately
                  localStorage.setItem(
                    "currentChat",
                    JSON.stringify({ name: s.name, messages: s.messages })
                  );
                }}
              >
                {s.name}
              </span>
              <div style={{ display: "flex", gap: "4px" }}>
                <button
                  title="Rename chat"
                  onClick={() => {
                    const newName = prompt("Rename chat:", s.name);
                    if (newName) {
                      const updated = [...sessions];
                      updated[i].name = newName;
                      setSessions(updated);
                      // If it's the currently open chat, reflect it in title/draft
                      if (chatTitle === s.name) {
                        setChatTitle(newName);
                      }
                    }
                  }}
                >
                  ✏️
                </button>
                <button title="Delete chat" onClick={() => deleteSession(i)}>🗑️</button>
              </div>
            </li>
          ))}
        </ul>

        <div className="bottom-controls">
          <input
            value={chatTitle}
            onChange={(e) => setChatTitle(e.target.value)}
            placeholder="Chat title..."
            title="Enter chat title"
          />
          <button onClick={saveSession} title="Save this chat">💾 Save</button>
          <button onClick={exportChat} title="Export chat to markdown">⬇️ Export</button>
          <button onClick={() => setDarkMode(!darkMode)} title="Toggle Light/Dark mode">
            {darkMode ? "☀️ Light" : "🌙 Dark"}
          </button>
        </div>
      </aside>

      <main>
        <div className="header">
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="model-selector"
            title={currentTooltip}
          >
            {MODELS.map((m) => (
              <option key={m.value} value={m.value} title={m.tooltip}>
                {m.label}
              </option>
            ))}
          </select>
          <h1>GitHub Chatbot</h1>
        </div>

        <div className="chat-box" ref={chatRef}>
          {history.map((msg, i) => (
            <div key={i} className={`chat-line ${msg.role}`}>
              <div className="bubble">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[
                    [rehypeHighlight, { detect: true, ignoreMissing: true }],
                  ]}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-line assistant typing">
              <div className="bubble">
                <div className="typing-dots"><span>.</span><span>.</span><span>.</span></div>
              </div>
            </div>
          )}
        </div>

        <div className="input-area">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask something..."
            title="Type your question"
            disabled={loading}
          />
          <button
            onClick={() => {
              if (loading && abortRef.current) {
                abortRef.current.abort(); // stop current request
              } else {
                askQuestion();
              }
            }}
            title={loading ? "Stop" : "Send"}
          >
            {loading ? "◼" : "↑"}
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;
