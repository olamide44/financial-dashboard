import clsx from "clsx";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { reapplyChartTheme } from "../lib/chartTheme";

function getInit(): "dark" | "light" {
  const saved = localStorage.getItem("theme");
  if (saved === "light" || saved === "dark") return saved;
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState<"dark"|"light">(getInit());

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "light") {
      root.classList.add("light");
      root.classList.remove("dark");
      (root as any).style.setProperty("color-scheme", "light");
    } else {
      root.classList.add("dark");
      root.classList.remove("light");
      (root as any).style.setProperty("color-scheme", "dark");
    }
    localStorage.setItem("theme", theme);
    reapplyChartTheme();
  }, [theme]);

  return (
    <button
      className={clsx("btn-ghost inline-flex items-center gap-2 px-3 py-2 rounded-xl")}
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      aria-label="Toggle theme"
      title="Toggle theme"
    >
      {theme === "dark" ? <Sun size={16}/> : <Moon size={16}/>}
      <span className="text-sm">{theme === "dark" ? "Light" : "Dark"}</span>
    </button>
  );
}
