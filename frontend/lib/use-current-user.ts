"use client";

import { useEffect, useState } from "react";

import { CURRENT_USER_STORAGE_KEY, USER_CHANGED_EVENT } from "@/lib/constants";

export function getStoredUserId(): number | null {
  if (typeof window === "undefined") {
    return null;
  }

  const storedValue = window.localStorage.getItem(CURRENT_USER_STORAGE_KEY);
  if (!storedValue) {
    return null;
  }

  const parsedValue = Number(storedValue);
  return Number.isNaN(parsedValue) ? null : parsedValue;
}

export function setStoredUserId(userId: number): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(CURRENT_USER_STORAGE_KEY, String(userId));
  window.dispatchEvent(new Event(USER_CHANGED_EVENT));
}

export function clearStoredUserId(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(CURRENT_USER_STORAGE_KEY);
  window.dispatchEvent(new Event(USER_CHANGED_EVENT));
}

export function useCurrentUserId(): number | null {
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    const syncUserId = () => setUserId(getStoredUserId());

    syncUserId();
    window.addEventListener(USER_CHANGED_EVENT, syncUserId);
    window.addEventListener("focus", syncUserId);

    return () => {
      window.removeEventListener(USER_CHANGED_EVENT, syncUserId);
      window.removeEventListener("focus", syncUserId);
    };
  }, []);

  return userId;
}
