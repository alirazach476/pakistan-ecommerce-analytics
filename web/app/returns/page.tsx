"use client";

import ChartCard from "@/components/ChartCard";
import { getDashboard } from "@/lib/data";
import { fmtPkr } from "@/lib/format";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const COLORS = ["#008080", "#0f3460", "#4a90a4", "#2ecc71", "#e67e22", "#9b59b6", "#e74c3c"];

export default function ReturnsPage() {
  const d = getDashboard();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Returns & Payments</h1>
      <div className="grid md:grid-cols-2 gap-4">
        <ChartCard title="Returns by Reason">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={d.returns}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="return_reason" tick={{ fontSize: 9 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="returns" fill="#008080" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Refund Amount by Reason">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={d.returns}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="return_reason" tick={{ fontSize: 9 }} />
              <YAxis tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
              <Tooltip formatter={(v: number) => fmtPkr(v)} />
              <Bar dataKey="refund_amount" fill="#0f3460" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <ChartCard title="Payment Method Usage">
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={d.payments} dataKey="transactions" nameKey="payment_method" cx="50%" cy="50%" outerRadius={100} label>
              {d.payments.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
