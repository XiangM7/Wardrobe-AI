"use client";

import Link from "next/link";
import { useState } from "react";

import { seedDemoCloset } from "@/lib/api";
import { setStoredUserId } from "@/lib/use-current-user";

export function LandingActions() {
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleLoadDemo = async () => {
    setLoadingDemo(true);
    setError("");
    setMessage("");

    try {
      const payload = await seedDemoCloset();
      setStoredUserId(payload.user.id);
      setMessage(`${payload.message} ${payload.clothing_count} demo items are ready.`);
    } catch (demoError) {
      setError(demoError instanceof Error ? demoError.message : "Unable to load the demo closet.");
    } finally {
      setLoadingDemo(false);
    }
  };

  return (
    <div className="mt-8">
      <div className="flex flex-wrap gap-3">
        <Link href="/onboarding" className="primary-button">
          Start onboarding
        </Link>
        <Link href="/recommend" className="secondary-button">
          View today outfit
        </Link>
        <button type="button" className="secondary-button" onClick={handleLoadDemo} disabled={loadingDemo}>
          {loadingDemo ? "Loading demo..." : "Load demo closet"}
        </button>
      </div>

      {message ? <p className="mt-4 text-sm font-semibold text-[#1e5a4b]">{message}</p> : null}
      {error ? <p className="mt-4 text-sm font-semibold text-[#8a1f1f]">{error}</p> : null}
    </div>
  );
}
