import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router";
import { api } from "../api";
import { bundledCatalog } from "../catalog";
import { DynamicView } from "../components/DynamicView";
import { ErrorState, LoadingState } from "../components/States";
import { useI18n } from "../i18n";

export function Overview() {
  const { text } = useI18n();
  const health = useQuery({ queryKey: ["health"], queryFn: () => fetch("/api/v2/method/noxus_core.api.v1.health").then((response) => response.json()), retry: false });
  return <section className="page"><header className="page-head"><div><span className="eyebrow">{text("Current site", "الموقع الحالي")}</span><h1>{text("Operations overview", "نظرة عامة على العمليات")}</h1><p>{text("Module, deployment, and runtime state from the NOXUS control plane.", "حالة الوحدات والنشر والتشغيل من لوحة تحكم NOXUS.")}</p></div><Link className="primary" to="/builder">{text("Build a solution", "إنشاء حل")}</Link></header><div className="metrics"><article><span>{text("Installed modules", "الوحدات المثبتة")}</span><strong>9</strong><small>{text("All compatible", "كلها متوافقة")}</small></article><article><span>{text("Open deployments", "عمليات النشر المفتوحة")}</span><strong>0</strong><small>{text("No blocked jobs", "لا توجد مهام متوقفة")}</small></article><article><span>{text("System health", "صحة النظام")}</span><strong>{health.isError ? text("Offline", "غير متصل") : text("Healthy", "سليم")}</strong><small>{text("Database and Redis", "قاعدة البيانات وRedis")}</small></article><article><span>{text("Audit events", "أحداث التدقيق")}</span><strong>—</strong><small>{text("Permission protected", "محمية بالصلاحيات")}</small></article></div><div className="two-column"><section><h2>{text("Recent deployments", "أحدث عمليات النشر")}</h2><DynamicView doctype="Deployment Record" /></section><section><h2>{text("Runtime posture", "حالة بيئة التشغيل")}</h2><ul className="checks"><li>● {text("Same-origin API routing", "توجيه API على نفس النطاق")}</li><li>● {text("Site hostname allow-list", "قائمة سماح لأسماء المواقع")}</li><li>● {text("Encrypted credentials", "بيانات اعتماد مشفرة")}</li><li>● {text("Signed webhook delivery", "إرسال Webhook موقّع")}</li></ul></section></div></section>;
}

export function Modules() {
  const { text } = useI18n();
  const query = useQuery({ queryKey: ["catalog"], queryFn: api.catalog, retry: false });
  const modules = query.data?.modules ?? bundledCatalog;
  const [view, setView] = useState<"list" | "grid">("list");
  return <section className="page"><header className="page-head"><div><h1>{text("Module catalog", "دليل الوحدات")}</h1><p>{text("Bundled and locally installed modules.", "الوحدات المضمّنة والمثبتة محليًا.")}</p></div><div className="segmented"><button onClick={() => setView("list")} aria-pressed={view === "list"}>{text("List", "قائمة")}</button><button onClick={() => setView("grid")} aria-pressed={view === "grid"}>{text("Grid", "شبكة")}</button></div></header>{query.isLoading ? <LoadingState /> : <div className={`catalog ${view}`}>{modules.map((item) => <article key={item.name}><div><span className="tag">{item.category}</span><h2>{item.display_name}</h2><p>{item.description}</p></div><dl><dt>{text("Version", "الإصدار")}</dt><dd>{item.version}</dd><dt>{text("License", "الترخيص")}</dt><dd>{item.license}</dd><dt>{text("Dependencies", "الاعتماديات")}</dt><dd>{item.dependencies.required.join(", ") || text("None", "لا يوجد")}</dd><dt>{text("Status", "الحالة")}</dt><dd>{text("Compatible", "متوافق")}</dd></dl><Link to={`/modules/${item.name}`}>{text("Open module", "فتح الوحدة")}</Link></article>)}</div>}</section>;
}

const management: Record<string, { title: string; titleAr: string; description: string; descriptionAr: string; doctype: string; mode?: "list" | "kanban" | "calendar" }> = {
  workflows: { title: "Workflow builder", titleAr: "منشئ سير العمل", description: "Inspect template states and permission-bound transitions.", descriptionAr: "راجع حالات القوالب والانتقالات المرتبطة بالصلاحيات.", doctype: "Workflow Template", mode: "kanban" },
  "data-models": { title: "Data models", titleAr: "نماذج البيانات", description: "Metadata-driven views use live Frappe DocType definitions.", descriptionAr: "واجهات ديناميكية تعتمد على تعريفات DocType الفعلية.", doctype: "Noxus Module" },
  integrations: { title: "Integration settings", titleAr: "إعدادات التكامل", description: "Endpoint allow-lists, credentials, and signed webhooks.", descriptionAr: "قوائم السماح وبيانات الاعتماد وWebhooks الموقّعة.", doctype: "Integration Definition" },
  credentials: { title: "API credentials", titleAr: "بيانات اعتماد API", description: "Encrypted provider credentials and expiration metadata.", descriptionAr: "بيانات اعتماد مزودي الخدمة المشفرة وبيانات انتهاء الصلاحية.", doctype: "API Credential" },
  webhooks: { title: "Webhook endpoints", titleAr: "نقاط Webhook", description: "Allow-listed HTTPS endpoints with HMAC signatures.", descriptionAr: "نقاط HTTPS مسموحة بتوقيعات HMAC.", doctype: "Webhook Endpoint" },
  audit: { title: "Immutable audit log", titleAr: "سجل التدقيق غير القابل للتعديل", description: "Permission-protected security and lifecycle events.", descriptionAr: "أحداث أمان ودورة حياة محمية بالصلاحيات.", doctype: "Audit Event" },
  health: { title: "System health", titleAr: "صحة النظام", description: "Database, queue, scheduler, and runtime checks.", descriptionAr: "فحوصات قاعدة البيانات والطوابير والجدولة والتشغيل.", doctype: "System Health Check" },
  roles: { title: "Role permission manager", titleAr: "إدارة الأدوار والصلاحيات", description: "Server-side templates remain the source of truth.", descriptionAr: "تظل قوالب الخادم هي المصدر المعتمد.", doctype: "Role Template" },
  reports: { title: "Report builder", titleAr: "منشئ التقارير", description: "Permission-aware operational reports.", descriptionAr: "تقارير تشغيلية تراعي الصلاحيات.", doctype: "System Health Check" },
  deployments: { title: "Deployment history", titleAr: "سجل النشر", description: "Resumable, idempotent blueprint jobs.", descriptionAr: "مهام مخططات قابلة للاستكمال ولا تتكرر.", doctype: "Deployment Record" },
  settings: { title: "Branding settings", titleAr: "إعدادات الهوية", description: "Product identity and LTR/RTL defaults.", descriptionAr: "هوية المنتج واتجاه العرض الافتراضي.", doctype: "Tenant Branding" },
};

export function ManagementPage({ kind }: { kind: keyof typeof management }) {
  const { text } = useI18n();
  const page = management[kind];
  if (!page) return null;
  return <section className="page"><header className="page-head"><div><h1>{text(page.title, page.titleAr)}</h1><p>{text(page.description, page.descriptionAr)}</p></div></header><DynamicView doctype={page.doctype} {...(page.mode ? { mode: page.mode } : {})} /></section>;
}

export function Marketplace() {
  const { t, text } = useI18n();
  return <section className="page"><header className="page-head"><div><h1>{t("marketplace")}</h1><p>{text("Discover bundled and locally installed community modules.", "استعرض الوحدات المجتمعية المضمّنة والمثبتة محليًا.")}</p></div><button disabled>{t("unavailable")}</button></header><div className="notice">{text("Remote publishing and installation are intentionally unavailable in Community v1.", "النشر والتثبيت عن بُعد غير متاحين عمدًا في الإصدار المجتمعي 1.")}</div><div className="catalog grid">{bundledCatalog.map((item) => <article key={item.name}><h2>{item.display_name}</h2><p>{item.description}</p><span className="tag">{text("Bundled", "مضمّنة")}</span></article>)}</div></section>;
}

export function Profile() {
  const { language, setLanguage, text } = useI18n();
  const user = useQuery({ queryKey: ["user"], queryFn: api.currentUser });
  if (user.isLoading) return <LoadingState />;
  if (user.error) return <ErrorState error={user.error} />;
  return <section className="page"><header className="page-head"><div><h1>{text("User profile", "الملف الشخصي")}</h1><p>{text("Session identity and personal language preference.", "هوية الجلسة وتفضيل اللغة الشخصي.")}</p></div></header><div className="form-view"><label>{text("Email", "البريد الإلكتروني")}<input readOnly value={user.data} /></label><label>{text("Preferred language", "اللغة المفضلة")}<select value={language} onChange={(event) => setLanguage(event.target.value === "ar" ? "ar" : "en")}><option value="en">English</option><option value="ar">العربية</option></select></label></div></section>;
}
