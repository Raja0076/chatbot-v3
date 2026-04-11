import React, { useState, useRef, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import MessageBubble from "./MessageBubble";
import VoiceRecorder from "./VoiceRecorder";
import { sendAudioToBackend } from "../services/api";
import bgImage from "../assets/bg6.webp";
import { FaStop } from "react-icons/fa";

function ChatUI() {
  const [messages, setMessages] = useState([
    {
      id: uuidv4(),
      sender: "bot",
      type: "text",
      text: "Hello! Ask your career questions using voice.",
    },
  ]);

  const [chatHistory, setChatHistory] = useState([]);
  const [lastIntent,  setLastIntent]  = useState(null);
  const [loading,     setLoading]     = useState(false);
  const [loadingDots, setLoadingDots] = useState("");
  const [isPlaying,   setIsPlaying]   = useState(false);

  const currentAudioRef = useRef(null);
  const chatEndRef      = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (!loading) return;
    const interval = setInterval(() => {
      setLoadingDots(prev => (prev.length >= 3 ? "" : prev + "."));
    }, 500);
    return () => clearInterval(interval);
  }, [loading]);

  // ── Stop any currently playing audio ─────────────────────────────────────
  const stopAudio = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }
    setIsPlaying(false);
  };

  // ── Play audio and track it so it can be stopped ──────────────────────────
  const playAudio = (url) => {
    stopAudio();

    const audio = new Audio(url);
    currentAudioRef.current = audio;
    setIsPlaying(true);

    audio.play();

    audio.onended = () => {
      currentAudioRef.current = null;
      setIsPlaying(false);
    };

    audio.onerror = () => {
      currentAudioRef.current = null;
      setIsPlaying(false);
    };
  };

  const handleRecordingComplete = async (audioBlob, duration = 5) => {
    // Stop any playing audio when user starts a new recording
    stopAudio();

    const userAudioUrl = URL.createObjectURL(audioBlob);

    setMessages(prev => [
      ...prev,
      {
        id:       uuidv4(),
        sender:   "user",
        type:     "audio",
        audioUrl: userAudioUrl,
        duration,
      },
    ]);
    setLoading(true);

    try {
      console.log("[ChatUI] Sending with history:", chatHistory.length, "turns");
      console.log("[ChatUI] Sending last_intent:", lastIntent);

      const data = await sendAudioToBackend(audioBlob, chatHistory, lastIntent);

      // ── Save lastIntent only if it was a confident direct prediction ───────
      // ── not from context recovery — avoids locking into stale intent ───────
      if (
        data.intent &&
        data.intent !== "default" &&
        !data.used_context_recovery &&
        data.confidence >= 0.12
      ) {
        setLastIntent(data.intent);
        console.log(
          "[ChatUI] Saved last_intent:", data.intent,
          "confidence:", data.confidence
        );
      } else if (data.used_context_recovery) {
        console.log(
          "[ChatUI] Context recovery used — keeping old last_intent:", lastIntent
        );
      }

      // ── Update chat history ───────────────────────────────────────────────
      setChatHistory(prev => [
        ...prev,
        { role: "user",      content: data.english_question },
        { role: "assistant", content: data.english_reply     },
      ]);
      console.log(
        "[ChatUI] History updated, total turns:", chatHistory.length + 2
      );

      setMessages(prev => [
        ...prev,
        {
          id:     uuidv4(),
          sender: "bot",
          type:   "text",
          text:   `English: ${data.english_reply}\nTamil: ${data.tamil_reply}`,
        },
        {
          id:       uuidv4(),
          sender:   "bot",
          type:     "audio",
          audioUrl: data.audio_url,
          duration: 5,
        },
      ]);

      // ── Auto-play response audio ──────────────────────────────────────────
      if (data.audio_url) {
        playAudio(data.audio_url);
      }

    } catch (error) {
      let errorText = "Error connecting to AI server.";

      if (error.code === "ECONNABORTED") {
        errorText = "Response is taking too long. Please try again.";
      } else if (error.response?.status === 500) {
        errorText = "Server error. Please try again.";
      } else if (error.response?.status === 504) {
        errorText = "AI model timed out. Please try again.";
      } else if (!error.response) {
        errorText = "Cannot connect to server. Make sure the backend is running.";
      }

      setMessages(prev => [
        ...prev,
        { id: uuidv4(), sender: "bot", type: "text", text: errorText },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundImage: `url(${bgImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "Inter, sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "720px",
          height: "85vh",
          background: "rgba(10,20,40,0.45)",
          borderRadius: "25px",
          backdropFilter: "blur(15px)",
          WebkitBackdropFilter: "blur(15px)",
          border: "1px solid rgba(255,255,255,0.15)",
          boxShadow: "0 0 60px rgba(0,0,0,0.6)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* HEADER */}
        <div
          style={{
            padding: "20px",
            borderBottom: "1px solid rgba(255,255,255,0.08)",
            fontSize: "18px",
            fontWeight: "600",
            color: "#38bdf8",
            letterSpacing: "2px",
            textAlign: "center",
            textShadow: "0 0 10px #38bdf8",
          }}
        >
          AI VOICE ASSISTANT
        </div>

        {/* CHAT AREA */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "25px",
            color: "white",
          }}
        >
          {messages.map(msg => (
            <MessageBubble
              key={msg.id}
              sender={msg.sender}
              type={msg.type}
              text={msg.text}
              audioUrl={msg.audioUrl}
              duration={msg.duration}
            />
          ))}

          {loading && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                color: "#94a3b8",
                fontSize: "14px",
                padding: "10px 0",
              }}
            >
              <div
                style={{
                  width: "16px",
                  height: "16px",
                  border: "2px solid #38bdf8",
                  borderTop: "2px solid transparent",
                  borderRadius: "50%",
                  animation: "spin 0.8s linear infinite",
                }}
              />
              <span>AI is thinking{loadingDots}</span>
              <style>{`
                @keyframes spin {
                  from { transform: rotate(0deg); }
                  to   { transform: rotate(360deg); }
                }
              `}</style>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* BOTTOM BAR */}
        <div
          style={{
            padding: "20px",
            borderTop: "1px solid rgba(255,255,255,0.08)",
            background: "rgba(0,0,0,0.3)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "12px",
          }}
        >
          {/* Stop button — only visible while audio is playing */}
          {isPlaying && (
            <button
              onClick={stopAudio}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                backgroundColor: "#dc2626",
                color: "white",
                border: "none",
                borderRadius: "20px",
                padding: "8px 20px",
                fontSize: "14px",
                cursor: "pointer",
                fontFamily: "Inter, sans-serif",
              }}
            >
              <FaStop style={{ fontSize: "12px" }} />
              Stop Speaking
            </button>
          )}

          <VoiceRecorder onRecordingComplete={handleRecordingComplete} />
        </div>
      </div>
    </div>
  );
}

export default ChatUI;