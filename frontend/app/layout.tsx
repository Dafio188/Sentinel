import "./globals.css";
import { Sidebar } from "@/components/Sidebar";
import { Toaster } from "sonner";

export const metadata = {
  title: "AIGate — Privacy & Compliance Gateway",
  description: "Local AI Privacy & Compliance Gateway per dati e LLM",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="it">
      <body className="bg-[#0b0c10] text-[#f5f5f7] min-h-screen flex">
        <Sidebar />
        <main className="ml-64 flex-1 p-8 overflow-y-auto">
          {children}
        </main>
        <Toaster position="bottom-right" theme="dark" />
      </body>
    </html>
  );
}
