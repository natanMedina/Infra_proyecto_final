import { useEffect, useState } from "react";
import { getStats } from "../../api/sentimentAPI";

const StatsSummary = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getStats()
      .then((res) => setStats(res.data))
      .catch((err) => console.error("Error al obtener estadísticas:", err));
  }, []);

  if (!stats)
    return (
      <p className="text-gray-500 dark:text-gray-400">
        Cargando estadísticas...
      </p>
    );

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
      <div className="bg-gradient-to-r from-emerald-500/10 to-emerald-600/10 p-4 rounded-xl border border-emerald-500/20">
        <h3 className="font-bold text-emerald-400 mb-3 text-lg">Portafolio</h3>
        <div className="space-y-2">
          <p className="text-gray-300">
            Media:{" "}
            <span className="font-mono text-emerald-300 font-bold">
              {stats.portfolio_mean.toFixed(4)}
            </span>
          </p>
          <p className="text-gray-300">
            Desviación estándar:{" "}
            <span className="font-mono text-emerald-300 font-bold">
              {stats.portfolio_std.toFixed(4)}
            </span>
          </p>
        </div>
      </div>

      <div className="bg-gradient-to-r from-teal-500/10 to-teal-600/10 p-4 rounded-xl border border-teal-500/20">
        <h3 className="font-bold text-teal-400 mb-3 text-lg">Nasdaq</h3>
        <div className="space-y-2">
          <p className="text-gray-300">
            Media:{" "}
            <span className="font-mono text-teal-300 font-bold">
              {stats.nasdaq_mean.toFixed(4)}
            </span>
          </p>
          <p className="text-gray-300">
            Desviación estándar:{" "}
            <span className="font-mono text-teal-300 font-bold">
              {stats.nasdaq_std.toFixed(4)}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default StatsSummary;
