import React, { useState, useEffect } from "react";
import { getComparisonData } from "../api/sentimentAPI";
import {
  getComparisonIntradayData,
  getDownloadProgress as getIntradailyDownloadProgress,
} from "../api/intradayAPI";
import { getDownloadSentimentProgress } from "../api/sentimentAPI";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import Swal from "sweetalert2";
import { BarChart3, Cpu, Clock, Zap, TrendingUp, Activity } from "lucide-react";

const BenchMarkingPage = () => {
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [selectedApp, setSelectedApp] = useState("sentiment");

  const fetchComparisonData = async () => {
    setLoading(true);
    setError(null);
    try {
      let data;

      const localData = localStorage.getItem(`comparisonData_${selectedApp}`);
      if (localData) {
        setComparisonData(JSON.parse(localData));
        setLoading(false);
        return;
      }

      if (selectedApp === "sentiment") {
        data = await getComparisonData();
      } else {
        data = await getComparisonIntradayData();
      }

      localStorage.setItem(
        `comparisonData_${selectedApp}`,
        JSON.stringify(data)
      );
      setComparisonData(data);

      Swal.fire({
        title: "¡Datos obtenidos correctamente!",
        text: "La comparación de rendimiento se ha cargado con éxito",
        icon: "success",
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#10b981",
      });
    } catch (error) {
      console.error("Error al obtener la comparación de rendimiento:", error);
      setError("Hubo un error al obtener los datos.");
      Swal.fire({
        title: "¡Error!",
        text: "Hubo un problema al obtener los datos de la comparación",
        icon: "error",
        confirmButtonText: "Aceptar",
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchDownloadProgress = async () => {
    try {
      if (selectedApp === "sentiment") {
        const response = await getDownloadSentimentProgress();
        setDownloadProgress(response.progress);
      } else {
        const response = await getIntradailyDownloadProgress();
        setDownloadProgress(response.progress);
      }
    } catch (error) {
      console.error("Error obteniendo el progreso de descarga:", error);
    }
  };

  useEffect(() => {
    if (loading) {
      const interval = setInterval(fetchDownloadProgress, 1000); // Actualiza cada 1 segundo
      return () => clearInterval(interval); // Limpia el intervalo cuando se detiene la carga
    }
  }, [loading]);

  const handleRecalculate = () => {
    localStorage.removeItem(`comparisonData_${selectedApp}`);
    fetchComparisonData();
  };

  const chartData = comparisonData
    ? [
        {
          name: "Secuencial",
          tiempo: comparisonData.secuencial.tiempo,
          cpu: comparisonData.secuencial.cpu,
        },
        {
          name: "Paralelo",
          tiempo: comparisonData.paralelo.tiempo,
          cpu: comparisonData.paralelo.cpu,
        },
      ]
    : [];

  return (
    <div className="space-y-8">
      {/* Header con gradiente */}
      <div className="bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-white/20 rounded-xl">
            <BarChart3 className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-4xl font-bold">Análisis de Rendimiento</h2>
            <p className="text-orange-100 text-lg">
              Comparación de estrategias secuencial vs paralelo
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 bg-white/10 rounded-xl p-4">
          <Activity className="w-5 h-5 text-orange-200" />
          <span className="text-orange-100">Progreso:</span>
          <span className="font-bold text-white bg-orange-600 px-3 py-1 rounded-full">
            {downloadProgress}%
          </span>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Panel izquierdo */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Zap className="w-6 h-6 text-orange-400" />
              <h3 className="text-2xl font-bold text-white">
                Configuración de Prueba
              </h3>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Seleccionar Aplicación
                </label>
                <select
                  value={selectedApp}
                  onChange={(e) => setSelectedApp(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent bg-slate-700 text-white"
                >
                  <option value="sentiment">Análisis de Sentimiento</option>
                  <option value="intraday">Trading Intradía</option>
                </select>
              </div>

              <button
                onClick={fetchComparisonData}
                disabled={loading}
                className="flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-xl font-semibold hover:from-orange-600 hover:to-red-600 transition-all shadow-lg disabled:opacity-50"
              >
                <TrendingUp className="w-5 h-5" />
                {loading ? "Ejecutando..." : "Ejecutar Benchmark"}
              </button>

              <button
                onClick={handleRecalculate}
                className="flex items-center gap-3 px-6 py-3 bg-gray-500 text-white rounded-xl font-semibold hover:bg-gray-600 transition-all"
              >
                <Activity className="w-5 h-5" />
                Recalcular Datos
              </button>
            </div>
          </div>

          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-6 h-6 text-orange-400" />
              <h3 className="text-2xl font-bold text-white">
                Resultados de Rendimiento
              </h3>
            </div>

            {comparisonData && (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="tiempo" fill="#f97316" name="Tiempo (s)" />
                  <Bar dataKey="cpu" fill="#ef4444" name="CPU (%)" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Panel derecho */}
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Clock className="w-6 h-6 text-orange-400" />
              <h3 className="text-xl font-bold text-white">
                Métricas de Tiempo
              </h3>
            </div>

            {comparisonData && (
              <div className="space-y-4">
                <div className="bg-orange-900/20 p-4 rounded-lg">
                  <h4 className="font-semibold text-orange-200">Secuencial</h4>
                  <p className="text-2xl font-bold text-orange-400">
                    {comparisonData.secuencial.tiempo}s
                  </p>
                </div>

                <div className="bg-red-900/20 p-4 rounded-lg">
                  <h4 className="font-semibold text-red-200">Paralelo</h4>
                  <p className="text-2xl font-bold text-red-400">
                    {comparisonData.paralelo.tiempo}s
                  </p>
                </div>

                <div className="bg-green-900/20 p-4 rounded-lg">
                  <h4 className="font-semibold text-green-200">Mejora</h4>
                  <p className="text-2xl font-bold text-green-400">
                    {(
                      ((comparisonData.secuencial.tiempo -
                        comparisonData.paralelo.tiempo) /
                        comparisonData.secuencial.tiempo) *
                      100
                    ).toFixed(1)}
                    %
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Cpu className="w-6 h-6 text-orange-400" />
              <h3 className="text-xl font-bold text-white">Uso de CPU</h3>
            </div>

            {comparisonData && (
              <div className="space-y-4">
                <div className="bg-orange-900/20 p-4 rounded-lg">
                  <h4 className="font-semibold text-orange-200">Secuencial</h4>
                  <p className="text-2xl font-bold text-orange-400">
                    {comparisonData.secuencial.cpu}%
                  </p>
                </div>

                <div className="bg-red-900/20 p-4 rounded-lg">
                  <h4 className="font-semibold text-red-200">Paralelo</h4>
                  <p className="text-2xl font-bold text-red-400">
                    {comparisonData.paralelo.cpu}%
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BenchMarkingPage;
