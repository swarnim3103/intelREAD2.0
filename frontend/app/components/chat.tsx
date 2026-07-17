import { useState } from "react";
import ReactMarkdown from "react-markdown";

type Source = {
  source: string;
  page: number | null;
  chunk_index: number | null;
  score: number;
};

type Message = {
  sender: "user" | "bot";
  text: string;
  sources?: Source[];
  mode?: "strict" | "hybrid";
};

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [allowOutsideKnowledge, setAllowOutsideKnowledge] = useState(false);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg: Message = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userMsg.text,
          allow_outside_knowledge: allowOutsideKnowledge,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        const detail = errData?.detail || "Something went wrong on the server.";
        setMessages((prev) => [...prev, { sender: "bot", text: `Error: ${detail}` }]);
        return;
      }

      const data = await res.json();
      const botMsg: Message = {
        sender: "bot",
        text: data.answer,
        sources: data.sources,
        mode: data.mode,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error: could not reach the server." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div className="flex flex-col h-[80vh] w-[50vh] border rounded-lg bg-white p-4">
      {/* Hybrid mode toggle */}
      <div className="flex items-center justify-between mb-3 pb-3 border-b">
        <span className="text-sm text-gray-600">Allow outside knowledge</span>
        <button
          onClick={() => setAllowOutsideKnowledge((prev) => !prev)}
          className={`w-11 h-6 rounded-full relative transition-colors ${
            allowOutsideKnowledge ? "bg-blue-500" : "bg-gray-300"
          }`}
          aria-label="Toggle outside knowledge"
        >
          <span
            className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform ${
              allowOutsideKnowledge ? "translate-x-5" : ""
            }`}
          />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 mb-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.sender === "user" ? "text-right" : "text-left"}>
            <div
              className={`inline-block p-2 rounded-lg max-w-[90%] ${
                msg.sender === "user" ? "bg-blue-100" : "bg-gray-100"
              }`}
            >
              {msg.sender === "bot" && msg.mode && (
                <span
                  className={`inline-block text-xs px-2 py-0.5 rounded-full mb-1 ${
                    msg.mode === "strict"
                      ? "bg-green-200 text-green-800"
                      : "bg-yellow-200 text-yellow-800"
                  }`}
                >
                  {msg.mode === "strict" ? "Strict" : "Hybrid"}
                </span>
              )}
              {msg.sender === "bot" ? (
                <div className="text-sm leading-relaxed">
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => <p className="my-1">{children}</p>,
                      ul: ({ children }) => (
                        <ul className="list-disc pl-5 my-1 space-y-0.5">{children}</ul>
                      ),
                      ol: ({ children }) => (
                        <ol className="list-decimal pl-5 my-1 space-y-0.5">{children}</ol>
                      ),
                      li: ({ children }) => <li>{children}</li>,
                      strong: ({ children }) => (
                        <strong className="font-semibold">{children}</strong>
                      ),
                      h1: ({ children }) => <h3 className="font-semibold my-1">{children}</h3>,
                      h2: ({ children }) => <h3 className="font-semibold my-1">{children}</h3>,
                      h3: ({ children }) => <h3 className="font-semibold my-1">{children}</h3>,
                      code: ({ children }) => (
                        <code className="bg-gray-200 px-1 py-0.5 rounded text-xs font-mono">
                          {children}
                        </code>
                      ),
                    }}
                  >
                    {msg.text}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="whitespace-pre-wrap">{msg.text}</div>
              )}

              {msg.sender === "bot" && msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-300 text-xs text-gray-500 space-y-0.5">
                  <div className="font-medium">Sources:</div>
                  {msg.sources.map((s, i) => (
                    <div key={i}>
                      {s.source}
                      {s.page != null ? `, page ${s.page}` : ""} (score {s.score.toFixed(2)})
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <div className="text-left text-sm text-gray-400 italic">Thinking...</div>}
      </div>

      <div className="flex gap-2">
        <input
          className="flex-1 border rounded-lg p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          className="bg-blue-500 text-white px-4 rounded-lg disabled:opacity-50"
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}