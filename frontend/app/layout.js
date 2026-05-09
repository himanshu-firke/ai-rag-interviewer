import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import NavBar from "@/components/NavBar";

export const metadata = {
  title: "AI Interview Screening System | PGAGI",
  description: "AI-powered role-based candidate screening system with RAG pipeline.",
  keywords: "AI interview, screening, RAG, machine learning, candidate assessment",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <NavBar />
          <main>{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
