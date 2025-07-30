import { useState, useEffect } from "react";
import {
  runIntradayStrategy,
  getAvailableDates,
  getReturns,
  getDailyReturns,
  getDownloadLink,
} from "../api/intradayAPI";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import Swal from "sweetalert2";
import { Zap, Play, Calendar, Download, TrendingUp, Clock } from "lucide-react";

const IntradayPage = () => {
  const [status, setStatus] = useState("");
  const [dates, setDates] = useState([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [returnsData, setReturnsData] = useState([]);
  const [tipoRetorno, setTipoRetorno] = useState("acumulado");

  const loadDates = async () => {
    try {
      const res = await getAvailableDates();
      setDates(res);
    } catch (err) {
      console.error("Error cargando fechas", err);
    }
  };

  const handleRunStrategy = async () => {
    setStatus("Ejecutando estrategia...");
    try {
      const res = await runIntradayStrategy();
      setStatus(res.message);
      await loadDates();

      Swal.fire({
        title: "¡Estrategia Ejecutada!",
        text: "La estrategia intradía se ha ejecutado con éxito. Seleccione las fechas para ver los resultados",
        icon: "success",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#10b981",
      });
    } catch {
      setStatus("❌ Error al ejecutar la estrategia");

      Swal.fire({
        title: "¡Error!",
        text: "Hubo un problema al ejecutar la estrategia intradía.",
        icon: "error",
        confirmButtonText: "Aceptar",
      });
    }
  };

  const loadReturns = async () => {
    try {
      const fn = tipoRetorno === "diario" ? getDailyReturns : getReturns;
      const data = await fn(startDate, endDate);
      setReturnsData(data);
    } catch (err) {
      console.error("Error obteniendo retornos", err);
    }
  };

  useEffect(() => {
    loadDates();
  }, []);

  useEffect(() => {
    if (startDate && endDate) {
      loadReturns();
    }
  }, [startDate, endDate]);

  useEffect(() => {
    if (startDate && endDate) {
      loadReturns();
    }
  }, [startDate, endDate, tipoRetorno]);

  return (
    <div className="space-y-8">
      {/* Header con gradiente */}
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-white/20 rounded-xl">
            <Zap className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-4xl font-bold">Trading de Alta Frecuencia</h2>
            <p className="text-purple-100 text-lg">
              Estrategias intradía con análisis técnico avanzado
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 bg-white/10 rounded-xl p-4">
          <Clock className="w-5 h-5 text-purple-200" />
          <span className="text-purple-100">Estado:</span>
          <span className="font-bold text-white bg-purple-600 px-3 py-1 rounded-full">
            {status || "Listo para ejecutar"}
          </span>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Panel izquierdo */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg border border-purple-100 dark:border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Play className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              <h3 className="text-2xl font-bold text-gray-800 dark:text-white">
                Ejecutar Estrategia
              </h3>
            </div>

            <button
              onClick={handleRunStrategy}
              className="flex items-center gap-3 px-6 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:from-purple-600 hover:to-pink-600 transition-all shadow-lg"
            >
              <Play className="w-5 h-5" />
              Ejecutar Estrategia Intradía
            </button>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg border border-purple-100 dark:border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              <h3 className="text-2xl font-bold text-gray-800 dark:text-white">
                Rendimiento de la Estrategia
              </h3>
            </div>

            {returnsData.length > 0 && (
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={returnsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="cumulative_strategy_return"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    dot={{ fill: "#8b5cf6", strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Panel derecho */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg border border-purple-100 dark:border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Calendar className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              <h3 className="text-xl font-bold text-gray-800 dark:text-white">
                Selección de Fechas
              </h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Fecha de inicio
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Fecha de fin
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
                />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-lg border border-purple-100 dark:border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Download className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              <h3 className="text-xl font-bold text-gray-800 dark:text-white">
                Descargar Datos
              </h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tipo de retorno
                </label>
                <select
                  value={tipoRetorno}
                  onChange={(e) => setTipoRetorno(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-slate-700 dark:text-white"
                >
                  <option value="acumulado">Retorno Acumulado</option>
                  <option value="diario">Retorno Diario</option>
                </select>
              </div>

              {startDate && endDate && (
                <a
                  href={getDownloadLink(startDate, endDate, tipoRetorno)}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all"
                >
                  <Download className="w-4 h-4" />
                  Descargar CSV
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntradayPage;
