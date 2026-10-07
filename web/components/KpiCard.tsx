type Props = { label: string; value: string };

export default function KpiCard({ label, value }: Props) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-gray-500">{label}</p>
      <p className="text-xl font-semibold text-navy mt-1">{value}</p>
    </div>
  );
}
