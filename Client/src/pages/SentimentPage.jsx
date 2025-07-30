import { useEffect, useState } from "react";
import StatsSummary from "../components/sentiment/StatsSummary";
import FilteredReturns from "../components/sentiment/FilteredReturns";
import InteractivePlot from "../components/sentiment/InteractivePlot";
import RecalculateForm from "../components/sentiment/RecalculateForm";
import { TrendingUp, BarChart3, Target, Users } from "lucide-react";

const SentimentPage = () => {
  const [criterioActivo, setCriterioActivo] = useState(() => {
    return localStorage.getItem("criterioActivo") || "engagement_ratio";
  });

  useEffect(() => {
    localStorage.setItem("criterioActivo", criterioActivo);
  }, [criterioActivo]);

  return (
    <div className="space-y-8">
      {/* Header con gradiente */}
      <div className="bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center gap-4 mb-4">
          <div className="p-3 bg-white/20 rounded-xl">
            <TrendingUp className="w-8 h-8" />
          </div>
          <div>
            <h2 className="text-4xl font-bold">Análisis de Mercado Social</h2>
            <p className="text-emerald-100 text-lg">
              Estrategias basadas en sentimiento de redes sociales
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 bg-white/10 rounded-xl p-4">
          <Target className="w-5 h-5 text-emerald-200" />
          <span className="text-emerald-100">Criterio de selección:</span>
          <span className="font-bold text-white bg-emerald-600 px-3 py-1 rounded-full">
            {criterioActivo.replace("_", " ").toUpperCase()}
          </span>
        </div>
      </div>

      {/* Contenido principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Panel izquierdo */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-6 h-6 text-emerald-400" />
              <h3 className="text-2xl font-bold text-white">
                Configuración de Estrategia
              </h3>
            </div>
            <RecalculateForm
              onSuccess={() => {}}
              onCriterioChange={(nuevoCriterio) =>
                setCriterioActivo(nuevoCriterio)
              }
            />
          </div>

          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Target className="w-6 h-6 text-emerald-400" />
              <h3 className="text-2xl font-bold text-white">
                Filtros Avanzados
              </h3>
            </div>
            <FilteredReturns />
          </div>
        </div>

        {/* Panel derecho */}
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Users className="w-6 h-6 text-emerald-400" />
              <h3 className="text-xl font-bold text-white">Métricas Clave</h3>
            </div>
            <StatsSummary />
          </div>

          <div className="bg-slate-800 rounded-2xl p-6 shadow-lg border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <TrendingUp className="w-6 h-6 text-emerald-400" />
              <h3 className="text-xl font-bold text-white">
                Evolución del Portafolio
              </h3>
            </div>
            <InteractivePlot />
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentPage;
