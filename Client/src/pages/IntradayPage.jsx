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
  const [minDate, setMinDate] = useState("");
  const [maxDate, setMaxDate] = useState("");

  const loadDates = async () => {
    try {
      const res = await getAvailableDates();
      setDates(res);

      // Establecer rango de fechas disponibles
      if (res.length > 0) {
        setMinDate(res[0]);
        setMaxDate(res[res.length - 1]);

        // Establecer fechas por defecto (últimos 30 días disponibles)
        const lastDate = new Date(res[res.length - 1]);
        const startDate = new Date(lastDate);
        startDate.setDate(startDate.getDate() - 30);

        const startDateStr = startDate.toISOString().split("T")[0];
        const endDateStr = lastDate.toISOString().split("T")[0];

        setStartDate(startDateStr);
        setEndDate(endDateStr);
      }
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

      // Procesar datos para mejorar visualización
      const processedData = data.map((item) => ({
        ...item,
        // Limitar valores extremos para mejor visualización
        cumulative_strategy_return: Math.max(
          -50,
          Math.min(200, item.cumulative_strategy_return || 0)
        ),
        strategy_return: Math.max(-20, Math.min(20, item.strategy_return || 0)),
      }));

      setReturnsData(processedData);
    } catch (err) {
      console.error("Error obteniendo retornos", err);
      setReturnsData([]);
    }
  };

  const handleDateChange = (field, value) => {
    const selectedDate = new Date(value);
    const minDateObj = new Date(minDate);
    const maxDateObj = new Date(maxDate);

    if (field === "startDate") {
      if (selectedDate < minDateObj || selectedDate > maxDateObj) {
        Swal.fire({
          title: "Fecha fuera de rango",
          text: `Seleccione una fecha entre ${minDate} y ${maxDate}`,
          icon: "warning",
          confirmButtonText: "Aceptar",
        });
        return;
      }
      setStartDate(value);
    } else {
      if (selectedDate < minDateObj || selectedDate > maxDateObj) {
        Swal.fire({
          title: "Fecha fuera de rango",
          text: `Seleccione una fecha entre ${minDate} y ${maxDate}`,
          icon: "warning",
          confirmButtonText: "Aceptar",
        });
        return;
      }
      setEndDate(value);
    }
  };

  useEffect(() => {
    loadDates();
  }, []);

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
          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Play className="w-6 h-6 text-purple-400" />
              <h3 className="text-2xl font-bold text-white">
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

          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-6 h-6 text-purple-400" />
              <h3 className="text-2xl font-bold text-white">
                Rendimiento de la Estrategia
              </h3>
            </div>

            {returnsData.length > 0 && (
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={returnsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis
                    domain={tipoRetorno === "diario" ? [-20, 20] : [-50, 200]}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip
                    formatter={(value) => [`${value.toFixed(2)}%`, "Retorno"]}
                    labelFormatter={(label) => `Fecha: ${label}`}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey={
                      tipoRetorno === "diario"
                        ? "strategy_return"
                        : "cumulative_strategy_return"
                    }
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    dot={{
                      fill: "#ffffff",
                      stroke: "#8b5cf6",
                      strokeWidth: 2,
                      r: 3,
                      opacity: 0.8,
                    }}
                    activeDot={{
                      fill: "#ffffff",
                      stroke: "#8b5cf6",
                      strokeWidth: 3,
                      r: 5,
                    }}
                    name={
                      tipoRetorno === "diario"
                        ? "Retorno Diario"
                        : "Retorno Acumulado"
                    }
                  />
                </LineChart>
              </ResponsiveContainer>
            )}

            {returnsData.length === 0 && startDate && endDate && (
              <div className="text-center py-8 text-gray-400">
                <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>
                  No hay datos disponibles para el rango de fechas seleccionado
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Panel derecho */}
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Calendar className="w-6 h-6 text-purple-400" />
              <h3 className="text-xl font-bold text-white">
                Selección de Fechas
              </h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Fecha de inicio
                </label>
                <input
                  type="date"
                  value={startDate}
                  min={minDate}
                  max={maxDate}
                  onChange={(e) =>
                    handleDateChange("startDate", e.target.value)
                  }
                  className="w-full px-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-slate-700 text-white"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Rango disponible: {minDate} - {maxDate}
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Fecha de fin
                </label>
                <input
                  type="date"
                  value={endDate}
                  min={minDate}
                  max={maxDate}
                  onChange={(e) => handleDateChange("endDate", e.target.value)}
                  className="w-full px-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-slate-700 text-white"
                />
              </div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Download className="w-6 h-6 text-purple-400" />
              <h3 className="text-xl font-bold text-white">Descargar Datos</h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tipo de retorno
                </label>
                <select
                  value={tipoRetorno}
                  onChange={(e) => setTipoRetorno(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-slate-700 text-white"
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
