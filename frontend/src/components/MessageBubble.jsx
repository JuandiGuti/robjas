import ReactMarkdown from "react-markdown";
import { useRef, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

function MessageBubble({ text, sender }) {
  const [speaking, setSpeaking] = useState(false);
  const audioRef = useRef(null);
  const urlRef = useRef(null);

  const speak = async () => {
    if (!text?.trim() || speaking) return;

    setSpeaking(true);

    try {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (urlRef.current) {
        URL.revokeObjectURL(urlRef.current);
        urlRef.current = null;
      }

      const res = await fetch(`${API_BASE_URL}/tts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ text })
      });

      if (!res.ok) {
        throw new Error(`Error HTTP: ${res.status}`);
      }

      const audioBlob = await res.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      urlRef.current = audioUrl;
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => {
        if (urlRef.current) {
          URL.revokeObjectURL(urlRef.current);
          urlRef.current = null;
        }
      };

      await audio.play();
    } catch (error) {
      console.error("Error TTS:", error);
    } finally {
      setSpeaking(false);
    }
  };

  return (
    <div className={`message-row ${sender === "user" ? "user-row" : "bot-row"}`}>
      <div
        className={`message-bubble ${
          sender === "user" ? "user-bubble user-animate" : "bot-bubble bot-animate"
        }`}
      >
        {sender === "bot" ? (
          <div className="markdown-content">
            <ReactMarkdown>{text}</ReactMarkdown>

            <button className="speak-button" onClick={speak} disabled={speaking}>
              {speaking ? "Generando audio..." : "🔊 Escuchar"}
            </button>
          </div>
        ) : (
          text
        )}
      </div>
    </div>
  );
}

export default MessageBubble;