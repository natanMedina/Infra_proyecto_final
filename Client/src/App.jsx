import { useState } from "react";
import SentimentPage from "./pages/SentimentPage";
import IntradayPage from "./pages/IntradayPage";
import { Toaster } from "react-hot-toast";
import { TrendingUp, BarChart3, Zap } from "lucide-react";
import "../index.css";
import BenchMarkingPage from "./pages/BenchMarkingPage";

const App = () => {
  const [activeTab, setActiveTab] = useState("sentiment");

  return (
    <>
      <Toaster position="top-right" toastOptions={{ duration: 3000 }} />

      <div className="dark">
        <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
          <header className="bg-slate-800/80 backdrop-blur-sm shadow-lg border-b border-slate-700 p-6">
            <div className="max-w-7xl mx-auto flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  Portfolio Analytics Pro
                </h1>
              </div>

              <nav className="flex gap-2">
                <button
                  onClick={() => setActiveTab("sentiment")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-full cursor-pointer transition-all ${
                    activeTab === "sentiment"
                      ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg"
                      : "bg-slate-700/60 text-gray-300 hover:bg-slate-600"
                  }`}
                >
                  <TrendingUp className="w-4 h-4" />
                  <span>Análisis Social</span>
                </button>
                <button
                  onClick={() => setActiveTab("intraday")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-full cursor-pointer transition-all ${
                    activeTab === "intraday"
                      ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg"
                      : "bg-slate-700/60 text-gray-300 hover:bg-slate-600"
                  }`}
                >
                  <Zap className="w-4 h-4" />
                  <span>Trading Intradía</span>
                </button>
                <button
                  onClick={() => setActiveTab("benchmarking")}
                  className={`flex items-center gap-2 px-4 py-2 rounded-full cursor-pointer transition-all ${
                    activeTab === "benchmarking"
                      ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg"
                      : "bg-slate-700/60 text-gray-300 hover:bg-slate-600"
                  }`}
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>Rendimiento</span>
                </button>
              </nav>
            </div>
          </header>

          <main className="p-6 max-w-7xl mx-auto">
            {activeTab === "sentiment" && <SentimentPage />}
            {activeTab === "intraday" && <IntradayPage />}
            {activeTab === "benchmarking" && <BenchMarkingPage />}
          </main>
        </div>
      </div>
    </>
  );
};

export default App;
