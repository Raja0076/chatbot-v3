import React from "react";
import { FaPlay } from "react-icons/fa";

function MessageBubble({
  sender,
  type,
  text,
  audioUrl,
  duration,
  recognizedTamil,
  recognizedEnglish,
}) {

  const isUser = sender === "user";

  const formatDuration = (seconds = 0) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "16px",
      }}
    >
      <div style={{ maxWidth: "75%" }}>

        {type === "audio" ? (

          <div
            style={{
              background: isUser
                ? "linear-gradient(135deg,#2563eb,#38bdf8)"
                : "rgba(255,255,255,0.05)",
              color: "white",
              padding: "14px 18px",
              borderRadius: "18px",
              backdropFilter: "blur(10px)",
              border: "1px solid rgba(255,255,255,0.08)",
              boxShadow: isUser
                ? "0 0 15px rgba(56,189,248,0.4)"
                : "0 0 8px rgba(0,0,0,0.4)",
            }}
          >

            {/* AUDIO HEADER */}

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
              }}
            >

              {/* PLAY ICON */}

              <div
                style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "50%",
                  background: isUser ? "white" : "#38bdf8",
                  color: isUser ? "#2563eb" : "#020617",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <FaPlay size={12} />
              </div>

              {/* WAVEFORM */}

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "3px",
                  flex: 1,
                }}
              >
                {[10,18,12,20,14,18,11,16,13,19,12,17].map((h,i)=>(
                  <span
                    key={i}
                    style={{
                      width: "4px",
                      height: `${h}px`,
                      background: isUser ? "white" : "#38bdf8",
                      borderRadius: "4px",
                      opacity: 0.9,
                    }}
                  />
                ))}
              </div>

              {/* DURATION */}

              <div
                style={{
                  fontSize: "13px",
                  color: "rgba(255,255,255,0.8)"
                }}
              >
                {formatDuration(duration)}
              </div>

            </div>

            {/* AUDIO PLAYER */}

            <audio
              controls
              src={audioUrl}
              style={{
                width: "100%",
                marginTop: "12px",
                filter: "invert(1)"
              }}
            />

            {/* SPEECH TEXT */}

            {isUser && (recognizedTamil || recognizedEnglish) && (
              <div
                style={{
                  marginTop: "12px",
                  paddingTop: "10px",
                  borderTop: "1px solid rgba(255,255,255,0.1)",
                  fontSize: "14px",
                  lineHeight: "1.6",
                  color: "rgba(255,255,255,0.85)"
                }}
              >
                <div>
                  <strong style={{color:"#38bdf8"}}>Tamil:</strong> {recognizedTamil}
                </div>
                <div>
                  <strong style={{color:"#38bdf8"}}>English:</strong> {recognizedEnglish}
                </div>
              </div>
            )}

          </div>

        ) : (

          <div
            style={{
              background: isUser
                ? "linear-gradient(135deg,#2563eb,#38bdf8)"
                : "rgba(255,255,255,0.05)",
              color: "white",
              padding: "14px 18px",
              borderRadius: "18px",
              whiteSpace: "pre-line",
              backdropFilter: "blur(10px)",
              border: "1px solid rgba(255,255,255,0.08)",
              boxShadow: isUser
                ? "0 0 15px rgba(56,189,248,0.4)"
                : "0 0 8px rgba(0,0,0,0.4)",
              fontSize: "15px",
              lineHeight: "1.6",
            }}
          >
            {text}
          </div>

        )}

      </div>
    </div>
  );
}

export default MessageBubble;