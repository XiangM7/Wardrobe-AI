"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useCurrentUserId } from "@/lib/use-current-user";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/onboarding", label: "Onboarding" },
  { href: "/closet", label: "Closet" },
  { href: "/recommend", label: "Today Outfit" },
  { href: "/history", label: "History" },
];

export function NavBar() {
  const pathname = usePathname();
  const currentUserId = useCurrentUserId();

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-[rgba(247,241,231,0.85)] backdrop-blur">
      <div className="page-wrap flex flex-col gap-4 py-4 md:flex-row md:items-center md:justify-between">
        <div>
          <Link href="/" className="font-display text-3xl tracking-tight text-ink">
            Wardrobe AI
          </Link>
          <p className="mt-1 text-sm text-muted">
            Personalized daily outfits built from your own closet.
          </p>
        </div>

        <div className="flex flex-col gap-3 md:items-end">
          <nav className="flex flex-wrap gap-2">
            {navItems.map((item) => {
              const active =
                item.href === "/" ? pathname === item.href : pathname.startsWith(item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                    active ? "bg-ink text-white" : "bg-white/80 text-ink hover:bg-white"
                  }`}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="status-pill">
            {currentUserId ? `Local profile: User #${currentUserId}` : "No local profile selected yet"}
          </div>
        </div>
      </div>
    </header>
  );
}
