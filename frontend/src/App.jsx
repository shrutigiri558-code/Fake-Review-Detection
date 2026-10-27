import React from "react";
import { Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import DetectReview from "./pages/DetectReview";
import UploadFile from "./pages/UploadFile";
import Result from "./pages/Result";
import History from "./pages/History";

function App() {
  return (
    <div className="min-h-screen bg-black text-white flex flex-col relative overflow-hidden">

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-linear-to-b from-violet-900/30 via-black/50 to-black z-10" />

      {/* Navigation */}
      <div className="relative z-20">
        <Navbar />
      </div>

      {/* Main Content */}
      <main className="grow relative z-20">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/detect" element={<DetectReview />} />
          <Route path="/upload" element={<UploadFile />} />
          <Route path="/result" element={<Result />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>

      {/* footer */}
      <div className="relative z-20">
        <br />
        <br />
        <br />
      </div>
    </div>
  );
}

export default App;