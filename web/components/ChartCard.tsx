import { ReactNode } from "react";

type Props = { title: string; children: ReactNode; className?: string };

export default function ChartCard({ title, children, className = "" }: Props) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 shadow-sm ${className}`}>
      <h3 className="font-semibold text-navy mb-3">{title}</h3>
      {children}
    </div>
  );
}
