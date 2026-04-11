import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/homepage";
import ChatUI from "./components/ChatUI";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/chatUI" element={<ChatUI />} />
      </Routes>
    </Router>
  );
}

export default App;