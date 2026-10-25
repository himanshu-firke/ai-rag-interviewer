"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export default function HeroSection({ avatarList }) {
  const { isLoggedIn } = useAuth();

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Grid pattern */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,.6) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.6) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
        }}
      />

      {/* Ambient glow */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 w-[800px] h-[600px] rounded-full bg-blue-500/10 blur-[120px]" />
        <div className="absolute top-1/3 -right-32 w-[400px] h-[400px] rounded-full bg-cyan-500/8 blur-[100px]" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[300px] rounded-full bg-indigo-600/8 blur-[100px]" />
      </div>

      <div className="relative z-10 w-full max-w-5xl mx-auto px-6 pt-32 pb-24 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-1.5 text-sm font-medium text-blue-300 mb-8">
          <Sparkles className="h-3.5 w-3.5" />
          Powered by RAG Intelligence
        </div>

        {/* Headline */}
        <h1 className="text-4xl sm:text-5xl md:text-7xl font-extrabold leading-[1.08] tracking-tight text-white mb-6">
          Hire Smarter with{" "}
          <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-500 bg-clip-text text-transparent">
            AI-Driven
          </span>
          <br className="hidden sm:block" />
          Technical Interviews
        </h1>

        {/* Subtext */}
        <p className="mx-auto max-w-2xl text-lg md:text-xl leading-relaxed text-slate-400 mb-12">
          Generate dynamic coding challenges directly from your company&apos;s
          knowledge base. Evaluate candidates with AI precision and make
          data-driven hiring decisions — in minutes, not weeks.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Link href={isLoggedIn ? "/upload" : "/login"}>
            <Button
              size="lg"
              className="h-12 rounded-full bg-blue-600 px-8 text-base font-semibold text-white shadow-lg shadow-blue-600/25 transition-all hover:-translate-y-0.5 hover:bg-blue-500 hover:shadow-blue-500/40"
            >
              {isLoggedIn ? "Start Screening" : "Get Started Free"}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="#how-it-works">
            <Button
              variant="outline"
              size="lg"
              className="h-12 rounded-full border-slate-700 px-8 text-base font-semibold text-slate-300 transition-all hover:border-slate-500 hover:bg-white/5 hover:text-white"
            >
              See How It Works
            </Button>
          </Link>
        </div>

      </div>
    </section>
  );
}
