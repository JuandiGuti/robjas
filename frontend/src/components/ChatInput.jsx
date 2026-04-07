import { useRef, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

function ChatInput({ onSend, loading }) {
  const [message, setMessage] = useState("");
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const chunksRef = useRef([]);

  const pickRecordingMimeType = () => {
    const preferredTypes = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/mp4",
      "audio/ogg;codecs=opus",
      "audio/ogg"
    ];

    for (const mimeType of preferredTypes) {
      if (MediaRecorder.isTypeSupported(mimeType)) {
        return mimeType;
      }
    }

    return "";
  };

  const handleSend = () => {
    if (!message.trim()) return;
    onSend(message);
    setMessage("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  const stopTracks = () => {
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
  };

  const handleRecord = async () => {
    if (loading || transcribing) return;

    if (recording) {
      mediaRecorderRef.current?.stop();
      setRecording(false);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const selectedMimeType = pickRecordingMimeType();
      const recorder = selectedMimeType
        ? new MediaRecorder(stream, { mimeType: selectedMimeType })
        : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        setTranscribing(true);
        try {
          const recordedMimeType = recorder.mimeType || "audio/webm";
          const extension = recordedMimeType.includes("mp4")
            ? "mp4"
            : recordedMimeType.includes("ogg")
              ? "ogg"
              : "webm";

          const audioBlob = new Blob(chunksRef.current, { type: recordedMimeType });
          const formData = new FormData();
          formData.append("audio", audioBlob, `recording.${extension}`);

          const res = await fetch(`${API_BASE_URL}/stt`, {
            method: "POST",
            body: formData
          });

          if (!res.ok) {
            throw new Error(`Error HTTP: ${res.status}`);
          }

          const data = await res.json();
          const transcribedText = (data.text || "").trim();
          if (transcribedText) {
            setMessage((prev) => (prev ? `${prev} ${transcribedText}` : transcribedText));
          }
        } catch (error) {
          console.error("Error STT:", error);
        } finally {
          stopTracks();
          setTranscribing(false);
        }
      };

      recorder.start();
      setRecording(true);
    } catch (error) {
      console.error("No se pudo acceder al micrófono:", error);
      stopTracks();
    }
  };

  return (
    <div className="chat-input-container">
      <input
        type="text"
        className="chat-input"
        placeholder="Escribe tu pregunta..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading || transcribing}
      />

      <button className={`mic-button ${recording ? "recording" : ""}`} onClick={handleRecord} disabled={loading || transcribing}>
        {recording ? "Detener" : transcribing ? "Transcribiendo..." : "🎤 Hablar"}
      </button>

      <button className="send-button" onClick={handleSend} disabled={loading || transcribing || recording}>
        {loading ? "Enviando..." : "Enviar"}
      </button>
    </div>
  );
}

export default ChatInput;