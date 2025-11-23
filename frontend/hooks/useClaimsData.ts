"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Claim } from "@/types/claim";

interface ClaimsCachePayload {
  data: Claim[];
  timestamp: number;
}

interface UseClaimsDataOptions {
  pollInterval?: number;
  limit?: number;
  enabled?: boolean;
}

const CACHE_KEY = "riskchainClaimsCache";
const CACHE_SIGNAL_KEY = "riskchainClaimsCacheSignal";
const CLAIM_SUBMITTED_KEY = "claimSubmitted";
const CACHE_TTL_MS = 30_000; // 30 seconds of fresh cache

export function useClaimsData(options: UseClaimsDataOptions = {}) {
  const { pollInterval = 10_000, limit = 100, enabled = true } = options;
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const readCache = useCallback((): ClaimsCachePayload | null => {
    if (typeof window === "undefined") {
      return null;
    }
    const cached = sessionStorage.getItem(CACHE_KEY);
    if (!cached) {
      return null;
    }
    try {
      return JSON.parse(cached) as ClaimsCachePayload;
    } catch {
      sessionStorage.removeItem(CACHE_KEY);
      return null;
    }
  }, []);

  const hydrateFromCache = useCallback(
    (respectTTL = true) => {
      const cached = readCache();
      if (!cached) {
        return false;
      }
      if (respectTTL && Date.now() - cached.timestamp > CACHE_TTL_MS) {
        return false;
      }
      setClaims(cached.data);
      setLoading(false);
      return true;
    },
    [readCache]
  );

  const writeCache = useCallback((data: Claim[]) => {
    if (typeof window === "undefined") {
      return;
    }
    const payload: ClaimsCachePayload = {
      data,
      timestamp: Date.now(),
    };
    sessionStorage.setItem(CACHE_KEY, JSON.stringify(payload));
    try {
      localStorage.setItem(CACHE_SIGNAL_KEY, Date.now().toString());
    } catch {
      // Best-effort cache signal
    }
  }, []);

  const fetchClaims = useCallback(
    async (showLoading = false) => {
      if (!enabled) {
        return;
      }

      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;

      if (showLoading) {
        setLoading(true);
      }

      try {
        const response = await fetch(
          `http://localhost:8000/api/claims?limit=${limit}`,
          { signal: controller.signal }
        );
        if (!response.ok) {
          throw new Error("Failed to fetch claims");
        }
        const data: Claim[] = await response.json();
        setClaims(data);
        setError(null);
        writeCache(data);
      } catch (err) {
        if ((err as Error).name === "AbortError") {
          return;
        }
        const message =
          err instanceof Error ? err.message : "Failed to load claims";
        setError(message);
        console.error("Error fetching claims:", err);
      } finally {
        if (showLoading) {
          setLoading(false);
        }
      }
    },
    [enabled, limit, writeCache]
  );

  const syncClaimSubmission = useCallback(() => {
    if (typeof window === "undefined") {
      return;
    }
    const flag = localStorage.getItem(CLAIM_SUBMITTED_KEY);
    if (flag) {
      localStorage.removeItem(CLAIM_SUBMITTED_KEY);
      fetchClaims(true);
    }
  }, [fetchClaims]);

  useEffect(() => {
    if (!enabled) {
      controllerRef.current?.abort();
      setLoading(false);
      return;
    }

    const hadFreshCache = hydrateFromCache();
    fetchClaims(!hadFreshCache);

    const interval = setInterval(() => {
      fetchClaims(false);
    }, pollInterval);

    return () => {
      clearInterval(interval);
      controllerRef.current?.abort();
    };
  }, [enabled, fetchClaims, hydrateFromCache, pollInterval]);

  useEffect(() => {
    if (typeof window === "undefined" || !enabled) {
      return;
    }

    const handleStorage = (event: StorageEvent) => {
      if (event.key === CACHE_SIGNAL_KEY) {
        hydrateFromCache(false);
      }
      if (event.key === CLAIM_SUBMITTED_KEY && event.newValue) {
        syncClaimSubmission();
      }
    };

    window.addEventListener("storage", handleStorage);
    const submissionInterval = setInterval(syncClaimSubmission, 2000);

    return () => {
      window.removeEventListener("storage", handleStorage);
      clearInterval(submissionInterval);
    };
  }, [enabled, hydrateFromCache, syncClaimSubmission]);

  const refresh = useCallback(() => {
    fetchClaims(true);
  }, [fetchClaims]);

  return {
    claims,
    loading,
    error,
    refresh,
  };
}

