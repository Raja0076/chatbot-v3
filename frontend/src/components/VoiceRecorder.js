import React, { useRef, useState } from "react";
import { FaMicrophone, FaStop } from "react-icons/fa";

function VoiceRecorder({ onRecordingComplete }) {
  const mediaRecorderRef = useRef(null);
  const audioChunksRef   = useRef([]);
  const intervalRef      = useRef(null);

  const [isRecording, setIsRecording] = useState(false);
  const [duration,    setDuration]    = useState(0);

  const startRecording = async () => {
    try {
      const stream        = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current   = [];
      setDuration(0);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        onRecordingComplete(audioBlob, duration);
        stream.getTracks().forEach(track => track.stop());
        clearInterval(intervalRef.current);
      };

      mediaRecorder.start();
      setIsRecording(true);

      intervalRef.current = setInterval(() => {
        setDuration(prev => prev + 1);
      }, 1000);

    } catch (error) {
      alert("Microphone access denied or unavailable.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div style={{ textAlign: "center" }}>
      {!isRecording ? (
        <button
          onClick={startRecording}
          style={{
            backgroundColor: "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "50%",
            width: "60px",
            height: "60px",
            fontSize: "22px",
            cursor: "pointer",
          }}
        >
          <FaMicrophone />
        </button>
      ) : (
        <button
          onClick={stopRecording}
          style={{
            backgroundColor: "#dc2626",
            color: "white",
            border: "none",
            borderRadius: "50%",
            width: "60px",
            height: "60px",
            fontSize: "22px",
            cursor: "pointer",
          }}
        >
          <FaStop />
        </button>
      )}

      {isRecording && (
        <div style={{ marginTop: "10px", color: "#6b7280" }}>
          Recording... {duration}s
        </div>
      )}
    </div>
  );
}

export default VoiceRecorder;