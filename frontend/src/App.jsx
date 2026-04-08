import { useState } from "react";
import ChatContainer from "./components/ChatContainer";
import ChatInput from "./components/ChatInput";
import MetricsDashboard from "./components/MetricsDashboard";
import "./Styles/chat.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showMetrics, setShowMetrics] = useState(false);

  const sendMessage = async (message) => {
    const userMessage = { text: message, sender: "user" };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
      });

      if (!res.ok) {
        throw new Error(`Error HTTP: ${res.status}`);
      }

      const data = await res.json();

      const botMessage = {
        text: data.response || data.error || "No se recibió respuesta del servidor.",
        sender: "bot"
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error:", error);

      const errorMessage = {
        text: "Ocurrió un error al conectar con el servidor.",
        sender: "bot"
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="chat-card">
        <div className="chat-header">
          <h1>AIng. ROBjas</h1>
          <p>Programación Avanzada</p>
          <button 
            className="btn-metrics-toggle"
            onClick={() => setShowMetrics(!showMetrics)}
            title="Ver métricas de uso"
          >
            {showMetrics ? "Cerrar" : "Ver"} metricas
          </button>
        </div>

        <ChatContainer messages={messages} />
        <ChatInput onSend={sendMessage} loading={loading} />
      </div>

      {showMetrics && (
        <div
          className="metrics-modal-backdrop"
          onClick={() => setShowMetrics(false)}
          role="dialog"
          aria-modal="true"
          aria-label="Panel de métricas"
        >
          <div className="metrics-modal" onClick={(e) => e.stopPropagation()}>
            <MetricsDashboard onClose={() => setShowMetrics(false)} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
