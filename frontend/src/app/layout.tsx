import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "AiSOC — AI-Driven Security Operations Center",
  description: "Gen AI Capstone Project | Group 4 | PCCOE Pune",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 ml-[272px] p-8 relative z-10">{children}</main>
      </body>
    </html>
  );
}
