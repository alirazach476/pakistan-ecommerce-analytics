"use client";

import ChartCard from "@/components/ChartCard";
import KpiCard from "@/components/KpiCard";
import { getDashboard } from "@/lib/data";
import { fmtNum, fmtPct } from "@/lib/format";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function LogisticsPage() {
  const d = getDashboard();
  const l = d.logistics;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Logistics</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KpiCard label="Avg Delivery Days" value={Number(l.avg_days).toFixed(1)} />
        <KpiCard label="On-Time Rate" value={fmtPct(l.on_time_rate)} />
        <KpiCard label="Delayed Orders" value={fmtNum(l.delayed_orders)} />
      </div>
      <ChartCard title="Slowest Cities by Avg Delivery Days">
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={d.delivery_cities}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="city" tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="avg_delivery_days" fill="#008080" name="Avg Days" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
