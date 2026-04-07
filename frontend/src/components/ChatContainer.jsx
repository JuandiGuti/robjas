import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

function ChatContainer({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-container">
      {messages.length === 0 ? (
        <div className="empty-chat">
          <h2>Bienvenido al Tutor IA</h2>
          <p>Haz una pregunta sobre Programación Avanzada.</p>
        </div>
      ) : (
        <>
          {messages.map((msg, index) => (
            <MessageBubble key={index} text={msg.text} sender={msg.sender} />
          ))}
          <div ref={bottomRef}></div>
        </>
      )}
    </div>
  );
}

export default ChatContainer;