/**
 * Simple authentication utility for employee portal
 */

export const isAuthenticated = (): boolean => {
  if (typeof window === "undefined") return false;
  return sessionStorage.getItem("isAuthenticated") === "true";
};

export const getUserEmail = (): string | null => {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem("userEmail");
};

export const logout = (): void => {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem("isAuthenticated");
  sessionStorage.removeItem("userEmail");
};

