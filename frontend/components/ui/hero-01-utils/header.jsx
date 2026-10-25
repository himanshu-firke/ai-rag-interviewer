"use client";

import * as React from "react";
import Link from "next/link";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuLink,
} from "@/components/ui/navigation-menu";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

export default function Header({ navigationData }) {
  const [scrolled, setScrolled] = React.useState(false);
  const { isLoggedIn } = useAuth();

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        scrolled
          ? "bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm"
          : "bg-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between px-6 h-16">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-blue-600 text-white text-xs font-extrabold">
            AI
          </span>
          <span
            className={cn(
              "text-base font-bold tracking-tight transition-colors",
              scrolled ? "text-slate-900" : "text-white"
            )}
          >
            InterviewAI
          </span>
        </Link>

        {/* Desktop nav */}
        <NavigationMenu className="hidden md:flex">
          <NavigationMenuList className="gap-1">
            {navigationData.map((item) => (
              <NavigationMenuItem key={item.title}>
                <NavigationMenuLink asChild>
                  <Link
                    href={item.href}
                    className={cn(
                      "inline-flex h-9 items-center justify-center rounded-full px-4 text-sm font-medium transition-colors",
                      item.isActive
                        ? scrolled
                          ? "bg-slate-100 text-slate-900"
                          : "bg-white/15 text-white"
                        : scrolled
                          ? "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                          : "text-slate-300 hover:text-white hover:bg-white/10"
                    )}
                  >
                    {item.title}
                  </Link>
                </NavigationMenuLink>
              </NavigationMenuItem>
            ))}
          </NavigationMenuList>
        </NavigationMenu>

        {/* Desktop CTA */}
        <div className="hidden md:flex items-center gap-3">
          <Link href={isLoggedIn ? "/upload" : "/login"}>
            <Button
              size="sm"
              className="rounded-full bg-blue-600 hover:bg-blue-500 text-white font-semibold px-5"
            >
              {isLoggedIn ? "Dashboard" : "Get Started"}
            </Button>
          </Link>
        </div>

        {/* Mobile menu */}
        <Sheet>
          <SheetTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className={cn(
                "md:hidden",
                scrolled
                  ? "text-slate-900 hover:bg-slate-100"
                  : "text-white hover:bg-white/10"
              )}
            >
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="right" className="w-72">
            <SheetTitle className="sr-only">Navigation</SheetTitle>
            <nav className="flex flex-col gap-2 mt-8">
              {navigationData.map((item) => (
                <Link
                  key={item.title}
                  href={item.href}
                  className={cn(
                    "px-4 py-2.5 rounded-lg text-sm font-medium transition-colors",
                    item.isActive
                      ? "bg-slate-100 text-slate-900"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  )}
                >
                  {item.title}
                </Link>
              ))}
              <div className="border-t border-slate-200 mt-4 pt-4">
                <Link href={isLoggedIn ? "/upload" : "/login"}>
                  <Button className="w-full rounded-full bg-blue-600 hover:bg-blue-500 text-white font-semibold">
                    {isLoggedIn ? "Dashboard" : "Get Started"}
                  </Button>
                </Link>
              </div>
            </nav>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  );
}
