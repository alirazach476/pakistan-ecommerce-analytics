"use client";

import ChartCard from "@/components/ChartCard";
import { getDashboard } from "@/lib/data";
import { fmtPkr } from "@/lib/format";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function SalesPage() {
  const d = getDashboard();
  const monthly = d.monthly.map((m) => ({ ...m, label: `${m.month_name} ${m.year}` }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Sales Analytics</h1>
      <div className="grid md:grid-cols-2 gap-4">
        <ChartCard title="Monthly Net Revenue">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" tick={{ fontSize: 9 }} interval={2} />
              <YAxis tickFormatter={(v) => `${(v / 1e9).toFixed(1)}B`} />
              <Tooltip formatter={(v: number) => fmtPkr(v)} />
              <Bar dataKey="net_revenue" fill="#008080" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Monthly Orders">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" tick={{ fontSize: 9 }} interval={2} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="orders" fill="#0f3460" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <ChartCard title="Top 15 Products by Revenue">
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={d.top_products} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
            <YAxis type="category" dataKey="product_name" width={140} tick={{ fontSize: 9 }} />
            <Tooltip formatter={(v: number) => fmtPkr(v)} />
            <Bar dataKey="revenue" fill="#4a90a4" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
      <ChartCard title="Net Revenue Growth % (MoM)">
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={monthly}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" tick={{ fontSize: 9 }} interval={2} />
            <YAxis tickFormatter={(v) => `${v?.toFixed(0)}%`} />
            <Tooltip formatter={(v: number) => `${v?.toFixed(1)}%`} />
            <Line type="monotone" dataKey="growth_pct" stroke="#e67e22" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
