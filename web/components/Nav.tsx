"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Executive" },
  { href: "/sales", label: "Sales" },
  { href: "/customers", label: "Customers" },
  { href: "/products", label: "Products & Sellers" },
  { href: "/logistics", label: "Logistics" },
  { href: "/returns", label: "Returns & Payments" },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <nav className="bg-navy text-white px-4 py-3 shadow-md">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center gap-4">
        <div>
          <p className="font-bold text-lg">Pakistan E-commerce Analytics</p>
          <p className="text-xs text-teal-200">Synthetic portfolio data · PKR</p>
        </div>
        <div className="flex flex-wrap gap-2 ml-auto">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`px-3 py-1.5 rounded text-sm ${
                pathname === l.href ? "bg-teal text-white" : "bg-white/10 hover:bg-white/20"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
