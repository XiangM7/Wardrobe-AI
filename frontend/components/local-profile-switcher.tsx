"use client";

import { useEffect, useState } from "react";

import { getUsers } from "@/lib/api";
import { USER_CHANGED_EVENT } from "@/lib/constants";
import { clearStoredUserId, setStoredUserId, useCurrentUserId } from "@/lib/use-current-user";
import type { User } from "@/lib/types";

export function LocalProfileSwitcher() {
  const currentUserId = useCurrentUserId();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadUsers() {
      try {
        const fetchedUsers = await getUsers();
        if (!cancelled) {
          setUsers(fetchedUsers);
        }
      } catch {
        if (!cancelled) {
          setUsers([]);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadUsers();
    window.addEventListener(USER_CHANGED_EVENT, loadUsers);
    window.addEventListener("focus", loadUsers);

    return () => {
      cancelled = true;
      window.removeEventListener(USER_CHANGED_EVENT, loadUsers);
      window.removeEventListener("focus", loadUsers);
    };
  }, []);

  return (
    <div className="flex flex-col gap-2 md:items-end">
      <label className="text-xs font-semibold uppercase tracking-[0.24em] text-muted">
        Local profile
      </label>
      <div className="flex flex-wrap items-center gap-2">
        <select
          className="rounded-full border border-line bg-white/90 px-4 py-2 text-sm text-ink"
          value={currentUserId ?? ""}
          onChange={(event) => {
            const nextValue = event.target.value;
            if (!nextValue) {
              clearStoredUserId();
              return;
            }
            setStoredUserId(Number(nextValue));
          }}
          disabled={loading}
        >
          <option value="">{loading ? "Loading..." : "Select profile"}</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.name}
            </option>
          ))}
        </select>

        <button type="button" className="secondary-button !px-4 !py-2" onClick={clearStoredUserId}>
          New
        </button>
      </div>
      <p className="text-xs text-muted">
        {users.length > 0 ? `${users.length} local profile${users.length === 1 ? "" : "s"}` : "No saved profiles yet"}
      </p>
    </div>
  );
}
