import { useState, useEffect } from "react";
import SentimentPage from "./pages/SentimentPage";
import IntradayPage from "./pages/IntradayPage";
import { Toaster } from "react-hot-toast";
import { Moon, Sun, TrendingUp, BarChart3, Zap } from "lucide-react";
import "../index.css";
import BenchMarkingPage from "./pages/BenchMarkingPage";

const App = () => {
  const [activeTab, setActiveTab] = useState("sentiment");
  const [darkMode, setDarkMode] = useState(() => {
    return (
      localStorage.theme === "dark" ||
      (!("theme" in localStorage) &&
        window.matchMedia("(prefers-color-scheme: dark)").matches)
    );
  });

  useEffect(() => {
    localStorage.theme = darkMode ? "dark" : "light";
  }, [darkMode]);

  return (
    <>
      <Toaster position="top-right" toastOptions={{ duration: 3000 }} />

      <div className={`${darkMode ? "dark" : ""}`}>
        <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 text-gray-800 dark:from-slate-900 dark:to-slate-800 dark:text-white">
          <header className="bg-white/80 backdrop-blur-sm dark:bg-slate-800/80 shadow-lg border-b border-emerald-200 dark:border-slate-700 p-6">
            <div className="max-w-7xl mx-auto flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  Portfolio Analytics Pro
                </h1>
              </div>

              <div className="flex gap-4 items-center">
                <button
                  onClick={() => setDarkMode((prev) => !prev)}
                  className="flex items-center gap-2 px-4 py-2 text-sm rounded-full cursor-pointer bg-emerald-100 dark:bg-slate-700 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-200 dark:hover:bg-slate-600 transition-colors"
                >
                  {darkMode ? (
                    <>
                      <Sun className="w-4 h-4" />
                      <span className="hidden sm:inline">Modo Claro</span>
                    </>
                  ) : (
                    <>
                      <Moon className="w-4 h-4" />
                      <span className="hidden sm:inline">Modo Oscuro</span>
                    </>
                  )}
                </button>

                <nav className="flex gap-2">
                  <button
                    onClick={() => setActiveTab("sentiment")}
                    className={`flex items-center gap-2 px-4 py-2 rounded-full cursor-pointer transition-all ${
                      activeTab === "sentiment"
                        ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg"
                        : "bg-white/60 dark:bg-slate-700/60 text-gray-700 dark:text-gray-300 hover:bg-white dark:hover:bg-slate-600"
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
                        : "bg-white/60 dark:bg-slate-700/60 text-gray-700 dark:text-gray-300 hover:bg-white dark:hover:bg-slate-600"
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
                        : "bg-white/60 dark:bg-slate-700/60 text-gray-700 dark:text-gray-300 hover:bg-white dark:hover:bg-slate-600"
                    }`}
                  >
                    <BarChart3 className="w-4 h-4" />
                    <span>Rendimiento</span>
                  </button>
                </nav>
              </div>
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
