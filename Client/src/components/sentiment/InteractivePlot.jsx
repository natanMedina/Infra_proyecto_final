import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const InteractivePlot = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey="Date"
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          axisLine={{ stroke: "#374151" }}
        />
        <YAxis
          tick={{ fontSize: 12, fill: "#9CA3AF" }}
          axisLine={{ stroke: "#374151" }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1F2937",
            border: "1px solid #374151",
            borderRadius: "8px",
            color: "#F9FAFB",
          }}
        />
        <Legend wrapperStyle={{ color: "#F9FAFB" }} />
        <Line
          type="monotone"
          dataKey="portfolio_returns"
          name="Portafolio"
          stroke="#10B981"
          strokeWidth={3}
          dot={{ fill: "#10B981", strokeWidth: 2, r: 4, stroke: "#064E3B" }}
          activeDot={{
            r: 6,
            stroke: "#064E3B",
            strokeWidth: 2,
            fill: "#34D399",
          }}
        />
        <Line
          type="monotone"
          dataKey="nasdaq_return"
          name="Nasdaq"
          stroke="#06B6D4"
          strokeWidth={3}
          dot={{ fill: "#06B6D4", strokeWidth: 2, r: 4, stroke: "#164E63" }}
          activeDot={{
            r: 6,
            stroke: "#164E63",
            strokeWidth: 2,
            fill: "#22D3EE",
          }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default InteractivePlot;
