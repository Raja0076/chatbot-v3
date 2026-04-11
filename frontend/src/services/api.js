import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:5000",
  timeout: 120000,
});

export const sendAudioToBackend = async (
  audioBlob,
  chatHistory = [],
  lastIntent = null
) => {
  try {
    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.webm");
    formData.append("chat_history", JSON.stringify(chatHistory));

    if (lastIntent) {
      formData.append("last_intent", lastIntent);
      console.log("[API] Sending last_intent:", lastIntent);
    }

    console.log("[API] Sending chat_history with", chatHistory.length, "turns");

    const response = await API.post("/voice-chat", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 120000,
    });

    return response.data;

  } catch (error) {
    if (error.code === "ECONNABORTED") {
      console.error("Request timed out - model is taking too long");
    } else if (error.response) {
      console.error("Server error:", error.response.status, error.response.data);
    } else {
      console.error("Network error:", error.message);
    }
    throw error;
  }
};