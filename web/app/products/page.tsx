"use client";

import ChartCard from "@/components/ChartCard";
import { getDashboard } from "@/lib/data";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from "recharts";

export default function ProductsPage() {
  const d = getDashboard();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy">Product & Seller Analytics</h1>
      <ChartCard title="Top 10 Products by Revenue">
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={d.top_products.slice(0, 10)} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
            <YAxis type="category" dataKey="product_name" width={130} tick={{ fontSize: 9 }} />
            <Tooltip />
            <Bar dataKey="revenue" fill="#008080" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
      <ChartCard title="Seller Revenue vs Return Rate">
        <ResponsiveContainer width="100%" height={360}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" dataKey="seller_revenue" name="Revenue" tickFormatter={(v) => `${(v / 1e6).toFixed(0)}M`} />
            <YAxis type="number" dataKey="seller_return_rate" name="Return Rate" tickFormatter={(v) => `${(v * 100).toFixed(1)}%`} />
            <ZAxis type="number" dataKey="seller_revenue" range={[50, 400]} />
            <Tooltip cursor={{ strokeDasharray: "3 3" }} />
            <Scatter data={d.sellers} fill="#0f3460" />
          </ScatterChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}
