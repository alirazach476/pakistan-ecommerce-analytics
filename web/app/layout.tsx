import type { Metadata } from "next";
import Nav from "@/components/Nav";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pakistan E-commerce Analytics",
  description:
    "End-to-end e-commerce analytics dashboard — synthetic Pakistani marketplace data (portfolio project).",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Nav />
        <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
        <footer className="text-center text-xs text-gray-500 py-6 border-t mt-8">
          Synthetic data for portfolio demonstration · Not real company data · PKR
        </footer>
      </body>
    </html>
  );
}
