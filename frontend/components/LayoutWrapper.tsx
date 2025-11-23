"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import Sidebar from "@/components/Sidebar";

function DevOverlaySuppressor() {
  useEffect(() => {
    if (typeof document === "undefined" || !document.body) {
      return;
    }
    const selectors = [
      "[data-nextjs-devtools]",
      "[data-nextjs-devtools-panel]",
      "[data-nextjs-devtools-floating-toolbar]",
      "#nextjs-devtools",
      "#nextjs-devtools-badge",
      "#__next-dev-server-indicator-root",
      "#__next-build-watcher",
      "#__next-dev-overlay",
    ];

    const hideOverlay = () => {
      selectors.forEach((selector) => {
        document.querySelectorAll(selector).forEach((element) => {
          if (element instanceof HTMLElement) {
            element.style.display = "none";
          }
        });
      });

      const devToolButtons = document.querySelectorAll('button[aria-label="Next.js Tools"], button[aria-label="Open Next.js utilities"]');
      devToolButtons.forEach((button) => {
        if (button instanceof HTMLElement) {
          button.style.display = "none";
        }
      });
    };

    hideOverlay();
    const observer = new MutationObserver(hideOverlay);
    observer.observe(document.body, { childList: true, subtree: true });

    return () => observer.disconnect();
  }, []);

  return null;
}

export default function LayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";

  return (
    <>
      <DevOverlaySuppressor />
      {isLoginPage ? (
        <>{children}</>
      ) : (
        <div className="flex h-screen overflow-hidden">
          <Sidebar />
          <main className="ml-[280px] flex-1 bg-black overflow-auto">
            {children}
          </main>
        </div>
      )}
    </>
  );
}

