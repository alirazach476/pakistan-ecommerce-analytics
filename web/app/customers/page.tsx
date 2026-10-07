"use client";

import ChartCard from "@/components/ChartCard";
import { getDashboard } from "@/lib/data";
import { fmtPkr } from "@/lib/format";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function CustomersPage() {
  const d = getDashboard();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Customer Analytics</h1>
      <div className="grid md:grid-cols-2 gap-4">
        <ChartCard title="Customers by Segment">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={d.segments}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="customer_segment" tick={{ fontSize: 10 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="customers" fill="#008080" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Spend by Segment">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={d.segments}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="customer_segment" tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={(v) => `${(v / 1e9).toFixed(1)}B`} />
              <Tooltip formatter={(v: number) => fmtPkr(v)} />
              <Bar dataKey="spend" fill="#0f3460" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <ChartCard title="RFM Segments">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={d.rfm}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="rfm_segment" tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="customers" fill="#4a90a4" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
