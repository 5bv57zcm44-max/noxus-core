import { type ReactNode, useState } from "react";
import { NavLink } from "react-router";
import { useI18n } from "../i18n";

const navigation = [
  ["overview", "/"], ["builder", "/builder"], ["modules", "/modules"], ["workflows", "/workflows"],
  ["models", "/data-models"], ["integrations", "/integrations"], ["roles", "/roles"], ["reports", "/reports"],
  ["credentials", "/credentials"], ["webhooks", "/webhooks"], ["audit", "/audit"], ["health", "/health"],
  ["marketplace", "/marketplace"], ["deployments", "/deployments"], ["settings", "/settings"],
] as const;

export function Layout({ children }: { children: ReactNode }) {
  const { language, setLanguage, t, text } = useI18n();
  const [palette, setPalette] = useState(false);
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">N</span><span>NOXUS CORE<small>{text("Community", "المجتمعي")}</small></span></div>
      <nav aria-label="Primary">{navigation.map(([label, path]) => <NavLink key={path} to={path} end={path === "/"}>{t(label)}</NavLink>)}</nav>
      <div className="sidebar-foot"><span className="status-dot" />Frappe 16.28.0</div>
    </aside>
    <div className="main-column">
      <header className="topbar">
        <label><span className="sr-only">{t("workspace")}</span><select defaultValue="default"><option value="default">{text("Default workspace", "مساحة العمل الافتراضية")}</option></select></label>
        <label><span className="sr-only">{t("environment")}</span><select defaultValue="development"><option value="development">{text("Development", "تطوير")}</option><option value="production">{text("Production", "إنتاج")}</option></select></label>
        <button className="search" onClick={() => setPalette(true)}>⌕ <span>{t("search")}</span><kbd>Ctrl K</kbd></button>
        <button aria-label={t("notifications")}>○</button><NavLink to="/settings">{t("help")}</NavLink>
        <button onClick={() => setLanguage(language === "en" ? "ar" : "en")}>{language === "en" ? "العربية" : "English"}</button>
        <NavLink to="/profile">{t("profile")}</NavLink>
      </header>
      <main>{children}</main>
    </div>
    {palette && <div className="dialog-backdrop" role="presentation" onMouseDown={() => setPalette(false)}><section className="dialog" role="dialog" aria-modal="true" aria-label="Command palette" onMouseDown={(event) => event.stopPropagation()}><input autoFocus placeholder={t("search")} /><div className="command-list">{navigation.map(([label, path]) => <NavLink key={path} to={path} onClick={() => setPalette(false)}>{t(label)}<span>↵</span></NavLink>)}</div><button onClick={() => setPalette(false)}>Esc</button></section></div>}
  </div>;
}
