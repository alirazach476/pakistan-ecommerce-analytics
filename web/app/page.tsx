"use client";

import ChartCard from "@/components/ChartCard";
import KpiCard from "@/components/KpiCard";
import { getDashboard } from "@/lib/data";
import { fmtNum, fmtPct, fmtPkr } from "@/lib/format";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const COLORS = ["#008080", "#0f3460", "#4a90a4", "#2ecc71", "#e67e22", "#9b59b6"];

export default function ExecutivePage() {
  const d = getDashboard();
  const k = d.kpis;

  const monthly = d.monthly.map((m) => ({
    ...m,
    label: `${m.month_name} ${m.year}`,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy">Executive Overview</h1>
        <p className="text-sm text-gray-600">Generated {new Date(d.generated_at).toLocaleDateString()}</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
        <KpiCard label="Gross Revenue" value={fmtPkr(k.gross_revenue)} />
        <KpiCard label="Net Revenue" value={fmtPkr(k.net_revenue)} />
        <KpiCard label="Orders" value={fmtNum(k.total_orders)} />
        <KpiCard label="Customers" value={fmtNum(k.total_customers)} />
        <KpiCard label="AOV" value={fmtPkr(k.aov)} />
        <KpiCard label="Return Rate" value={fmtPct(k.return_rate)} />
        <KpiCard label="Cancellation" value={fmtPct(k.cancellation_rate)} />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <ChartCard title="Net Revenue Over Time">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
              <YAxis tickFormatter={(v) => `${(v / 1e9).toFixed(1)}B`} />
              <Tooltip formatter={(v: number) => fmtPkr(v)} />
              <Line type="monotone" dataKey="net_revenue" stroke="#008080" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Orders Over Time">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="label" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="orders" stroke="#0f3460" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <ChartCard title="Revenue by Category (Top 10)">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={d.categories.slice(0, 10)} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" tickFormatter={(v) => `${(v / 1e9).toFixed(1)}B`} />
              <YAxis type="category" dataKey="category_name" width={120} tick={{ fontSize: 10 }} />
              <Tooltip formatter={(v: number) => fmtPkr(v)} />
              <Bar dataKey="revenue" fill="#008080" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Revenue by Province">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={d.provinces}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="province" tick={{ fontSize: 10 }} />
              <YAxis tickFormatter={(v) => `${(v / 1e9).toFixed(1)}B`} />
              <Tooltip formatter={(v: number) => fmtPkr(v)} />
              <Bar dataKey="revenue" fill="#0f3460" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Payment Method Distribution">
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
