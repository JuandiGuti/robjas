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
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
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
      <textarea
        className="chat-input"
        placeholder="Escribe tu pregunta..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={2}
        disabled={loading || transcribing}
      />

      <div className="chat-actions">
        <button
          className={`mic-icon-button ${recording ? "recording" : ""}`}
          onClick={handleRecord}
          disabled={loading || transcribing}
          title={recording ? "Detener grabacion" : transcribing ? "Transcribiendo" : "Grabar voz"}
          aria-label={recording ? "Detener grabacion" : transcribing ? "Transcribiendo" : "Grabar voz"}
        >
          <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M12 15a4 4 0 0 0 4-4V7a4 4 0 0 0-8 0v4a4 4 0 0 0 4 4zm7-4a1 1 0 1 0-2 0 5 5 0 0 1-10 0 1 1 0 1 0-2 0 7 7 0 0 0 6 6.92V21H8a1 1 0 1 0 0 2h8a1 1 0 1 0 0-2h-3v-3.08A7 7 0 0 0 19 11z" />
          </svg>
        </button>

        <button className="send-button" onClick={handleSend} disabled={loading || transcribing || recording}>
          {loading ? "Enviando..." : "Enviar"}
        </button>
      </div>
    </div>
  );
}

export default ChatInput;