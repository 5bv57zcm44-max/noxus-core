import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api } from "../api";
import { bundledCatalog } from "../catalog";
import { useI18n } from "../i18n";
import type { Blueprint, ModuleManifest } from "../types";

const steps = ["industry", "modules", "features", "roles", "workflows", "integrations", "branding", "review", "deploy"] as const;
const industries = [
  { value: "general-business", en: "General Business", ar: "أعمال عامة" },
  { value: "transportation", en: "Transportation", ar: "النقل" },
  { value: "education", en: "Education", ar: "التعليم" },
  { value: "maintenance", en: "Maintenance", ar: "الصيانة" },
  { value: "hotel-operations", en: "Hotel Operations", ar: "تشغيل الفنادق" },
  { value: "professional-services", en: "Professional Services", ar: "الخدمات المهنية" },
  { value: "empty", en: "Start Empty", ar: "بدء فارغ" },
];

async function checksum(value: unknown) {
  const stable = (item: unknown): unknown => {
    if (Array.isArray(item)) return item.map(stable);
    if (item && typeof item === "object") return Object.fromEntries(Object.entries(item).sort(([left], [right]) => left.localeCompare(right)).map(([key, child]) => [key, stable(child)]));
    return item;
  };
  const bytes = new TextEncoder().encode(JSON.stringify(stable(value)));
  return [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))].map((item) => item.toString(16).padStart(2, "0")).join("");
}

export function SolutionBuilder() {
  const { direction, t, text } = useI18n();
  const [step, setStep] = useState(0);
  const [industry, setIndustry] = useState("general-business");
  const [selected, setSelected] = useState(new Set(["noxus_core"]));
  const [accent, setAccent] = useState("#4F46E5");
  const [productName, setProductName] = useState("NOXUS CORE");
  const [defaultDirection, setDefaultDirection] = useState(direction);
  const [deploymentProfile, setDeploymentProfile] = useState<"development" | "production">("production");
  const [filter, setFilter] = useState("");
  const catalogQuery = useQuery({ queryKey: ["catalog"], queryFn: api.catalog, retry: false });
  const catalog = catalogQuery.data?.modules ?? bundledCatalog;
  const visibleCatalog = catalog.filter((item) => `${item.display_name} ${item.name}`.toLowerCase().includes(filter.toLowerCase()));
  const resolution = useMutation({ mutationFn: api.resolve });
  const chosen = useMemo(() => catalog.filter((item) => selected.has(item.name)), [catalog, selected]);
  const toggle = (module: ModuleManifest) => {
    const next = new Set(selected);
    if (next.has(module.name) && module.name !== "noxus_core") next.delete(module.name); else next.add(module.name);
    for (const dependency of module.dependencies.required) next.add(dependency.split(/[<>=!~]/)[0] ?? dependency);
    setSelected(next);
    resolution.mutate([...next]);
  };
  const makeBlueprint = async (): Promise<Blueprint> => {
    const body = {
      schema_version: 1 as const, name: `noxus-${industry}`, industry,
      language: "both" as const, modules: chosen.map((item, index) => ({ name: item.name, version: item.version, features: item.features, install_order: index })),
      roles: [...new Set(chosen.flatMap((item) => item.roles))], workflows: [...new Set(chosen.flatMap((item) => item.workflows))], integrations: [],
      branding: { product_name: productName, accent_color: accent, default_direction: defaultDirection },
      deployment: { environment: deploymentProfile, with_erpnext: selected.has("erpnext"), http_port: 8080 }, generator_version: "1.0.0",
    };
    return { ...body, checksum: await checksum(body) };
  };
  const download = async () => {
    const blueprint = await makeBlueprint();
    const anchor = document.createElement("a");
    anchor.href = URL.createObjectURL(new Blob([JSON.stringify(blueprint, null, 2)], { type: "application/json" }));
    anchor.download = `${blueprint.name}.json`; anchor.click(); URL.revokeObjectURL(anchor.href);
  };
  const apply = useMutation({ mutationFn: async () => api.apply(await makeBlueprint(), crypto.randomUUID()) });
  return <section className="page builder-page">
    <header className="page-head"><div><span className="eyebrow">{step + 1} / 9</span><h1>{t("builder")}</h1><p>{text("Configure a reproducible, checksummed Solution Blueprint.", "كوّن مخطط حل قابلًا لإعادة الإنتاج ومحققًا بالبصمة الرقمية.")}</p></div><span className="health-pill">● {text("Site connected", "الموقع متصل")}</span></header>
    <ol className="steps">{steps.map((label, index) => <li key={label} className={index === step ? "active" : index < step ? "complete" : ""}><button aria-label={`${index + 1}. ${t(label)}`} onClick={() => setStep(index)}><span>{index + 1}</span>{t(label)}</button></li>)}</ol>
    <div className="builder-content">
      {step === 0 && <><h2>{t("selectIndustry")}</h2><div className="choice-grid">{industries.map((item) => <button className={industry === item.value ? "selected" : ""} onClick={() => setIndustry(item.value)} key={item.value}><strong>{text(item.en, item.ar)}</strong><span>{text("Curated modules, roles, and workflows", "وحدات وأدوار ومسارات عمل مختارة")}</span></button>)}</div></>}
      {step === 1 && <><div className="section-head"><div><h2>{t("selectModules")}</h2><p>{catalogQuery.isError ? text("Using the bundled catalog while the site API is unavailable.", "يتم استخدام الدليل المضمّن لأن API الموقع غير متاح.") : text("Catalog loaded from the current site.", "تم تحميل الدليل من الموقع الحالي.")}</p></div><input type="search" value={filter} onChange={(event) => setFilter(event.target.value)} placeholder={text("Filter modules", "تصفية الوحدات")} aria-label={text("Filter modules", "تصفية الوحدات")} /></div><div className="module-table">{visibleCatalog.map((item) => <article key={item.name}><input type="checkbox" checked={selected.has(item.name)} disabled={item.name === "noxus_core"} onChange={() => toggle(item)} aria-label={`${text("Enable", "تفعيل")} ${item.display_name}`} /><div><strong>{item.display_name}</strong><p>{item.description}</p><small>{item.publisher} · {item.version} · {item.license}</small></div><span className="tag">{item.category}</span><span>{item.compatibility_state ?? text("compatible", "متوافق")}</span></article>)}</div>{resolution.isPending && <div className="notice">{text("Resolving dependencies…", "جارٍ حل الاعتماديات…")}</div>}{resolution.data && <div className="notice">{text("Install order", "ترتيب التثبيت")}: {resolution.data.install_order.join(" → ")}{resolution.data.warnings.map((warning) => <p key={warning}>{warning}</p>)}</div>}{resolution.error && <div className="notice error">{resolution.error.message}</div>}</>}
      {step === 2 && <><h2>{t("features")}</h2>{chosen.map((item) => <details open key={item.name}><summary>{item.display_name}</summary><div className="tabs">Features · Fields · Roles · Permissions · Workflows · Automations · APIs · Dependencies · Version history</div><div className="check-grid">{item.features.map((feature) => <label key={feature}><input type="checkbox" defaultChecked />{feature.replaceAll("_", " ")}</label>)}</div></details>)}</>}
      {step === 3 && <ReviewList title={t("roles")} items={[...new Set(chosen.flatMap((item) => item.roles))]} />}
      {step === 4 && <ReviewList title={t("workflows")} items={[...new Set(chosen.flatMap((item) => item.workflows))]} />}
      {step === 5 && <><h2>{t("integrations")}</h2><p>{text("No provider is enabled by default. Credentials are configured after deployment and never included in a blueprint.", "لا يتم تفعيل أي مزود افتراضيًا. تُضبط بيانات الاعتماد بعد النشر ولا تُضمّن في المخطط.")}</p><label className="toggle"><input type="checkbox" checked={selected.has("noxus_ai")} onChange={() => { const ai = catalog.find((item) => item.name === "noxus_ai"); if (ai) toggle(ai); }} /> {text("Enable provider-neutral AI connector", "تفعيل موصل الذكاء الاصطناعي المحايد")}</label></>}
      {step === 6 && <><h2>{t("branding")}</h2><div className="form-grid"><label>{text("Product name", "اسم المنتج")}<input value={productName} onChange={(event) => setProductName(event.target.value)} /></label><label>{text("Accent color", "اللون الرئيسي")}<input type="color" value={accent} onChange={(event) => setAccent(event.target.value.toUpperCase())} /></label><label>{text("Default direction", "الاتجاه الافتراضي")}<select value={defaultDirection} onChange={(event) => setDefaultDirection(event.target.value === "rtl" ? "rtl" : "ltr")}><option value="ltr">LTR</option><option value="rtl">RTL</option></select></label></div></>}
      {step === 7 && <><h2>{t("review")}</h2><dl className="review"><div><dt>{text("Industry", "المجال")}</dt><dd>{text(industries.find((item) => item.value === industry)?.en ?? industry, industries.find((item) => item.value === industry)?.ar ?? industry)}</dd></div><div><dt>{text("Modules", "الوحدات")}</dt><dd>{chosen.map((item) => item.display_name).join(", ")}</dd></div><div><dt>{text("Estimated resources", "الموارد المتوقعة")}</dt><dd>4 CPU · 8 GiB RAM · 30 GiB disk</dd></div><div><dt>{text("Installation plan", "خطة التثبيت")}</dt><dd>{resolution.data?.install_order.join(" → ") ?? chosen.map((item) => item.name).join(" → ")}</dd></div></dl></>}
      {step === 8 && <><h2>{t("deploy")}</h2><label>{text("Deployment profile", "بيئة النشر")}<select value={deploymentProfile} onChange={(event) => setDeploymentProfile(event.target.value === "development" ? "development" : "production")}><option value="production">{text("Production", "إنتاج")}</option><option value="development">{text("Development", "تطوير")}</option></select></label><div className="deploy-options"><button onClick={() => void download()}>{t("generate")}</button><button onClick={() => apply.mutate()} disabled={apply.isPending}>{t("apply")}</button><button onClick={() => navigator.clipboard.writeText("docker compose -f compose.yaml -f compose.production.yaml --profile production up --build --detach")}>{t("docker")}</button></div><pre>docker compose -f compose.yaml -f compose.production.yaml --profile production up --build --detach</pre><p>{text("Community Deploy operates only on the current site or exports self-hosting instructions. Cloud provisioning is unavailable.", "النشر المجتمعي يعمل على الموقع الحالي فقط أو يصدّر تعليمات الاستضافة الذاتية. توفير السحابة غير متاح.")}</p>{apply.data && <div className="notice">{text("Deployment", "عملية النشر")} {apply.data.deployment}: {apply.data.stage}</div>}{apply.error && <div className="notice error">{apply.error.message}</div>}</>}
    </div>
    <footer className="builder-actions"><button disabled={step === 0} onClick={() => setStep((value) => value - 1)}>{t("back")}</button><button disabled={step === 8} onClick={() => setStep((value) => value + 1)}>{t("next")}</button></footer>
  </section>;
}

function ReviewList({ title, items }: { title: string; items: string[] }) {
  const { text } = useI18n();
  return <><h2>{title}</h2><div className="management-list">{items.map((item) => <label key={item}><input type="checkbox" defaultChecked /><strong>{item}</strong><span>{text("Included by selected module", "مضمّن بواسطة الوحدة المحددة")}</span></label>)}</div></>;
}
