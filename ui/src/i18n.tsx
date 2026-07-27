import { createContext, type ReactNode, useContext, useEffect, useMemo, useState } from "react";
import type { Direction, Language } from "./types";

const messages = {
  en: {
    overview: "Overview", builder: "Solution Builder", modules: "Modules", workflows: "Workflows",
    models: "Data Models", integrations: "Integrations", roles: "Users & Roles", reports: "Reports",
    credentials: "Credentials", webhooks: "Webhooks", audit: "Audit", health: "Health",
    marketplace: "Marketplace", deployments: "Deployments", settings: "Settings", workspace: "Workspace",
    environment: "Environment", search: "Global search", notifications: "Notifications", help: "Help",
    profile: "Profile", next: "Next", back: "Back", save: "Save", loading: "Loading", retry: "Retry",
    empty: "No records yet", denied: "You do not have permission to view this resource.", unavailable: "Unavailable in Community v1",
    industry: "Industry", features: "Features", branding: "Branding", review: "Review", deploy: "Deploy",
    selectIndustry: "Choose an industry template", selectModules: "Choose compatible modules",
    generate: "Download blueprint", apply: "Apply to current site", docker: "Docker commands",
  },
  ar: {
    overview: "نظرة عامة", builder: "منشئ الحلول", modules: "الوحدات", workflows: "سير العمل",
    models: "نماذج البيانات", integrations: "التكاملات", roles: "المستخدمون والأدوار", reports: "التقارير",
    credentials: "بيانات الاعتماد", webhooks: "خطافات الويب", audit: "التدقيق", health: "الصحة",
    marketplace: "السوق", deployments: "عمليات النشر", settings: "الإعدادات", workspace: "مساحة العمل",
    environment: "البيئة", search: "بحث شامل", notifications: "الإشعارات", help: "المساعدة",
    profile: "الملف الشخصي", next: "التالي", back: "السابق", save: "حفظ", loading: "جارٍ التحميل", retry: "إعادة المحاولة",
    empty: "لا توجد سجلات بعد", denied: "ليس لديك إذن لعرض هذا المورد.", unavailable: "غير متاح في الإصدار المجتمعي 1",
    industry: "المجال", features: "الميزات", branding: "الهوية", review: "المراجعة", deploy: "النشر",
    selectIndustry: "اختر قالب المجال", selectModules: "اختر الوحدات المتوافقة",
    generate: "تنزيل المخطط", apply: "تطبيق على الموقع الحالي", docker: "أوامر دوكر",
  },
} as const;

type MessageKey = keyof typeof messages.en;
interface I18nValue {
  language: Language;
  direction: Direction;
  setLanguage: (value: Language) => void;
  t: (key: MessageKey) => string;
  text: (english: string, arabic: string) => string;
}
const I18n = createContext<I18nValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() => localStorage.getItem("noxus-language") === "ar" ? "ar" : "en");
  const direction: Direction = language === "ar" ? "rtl" : "ltr";
  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = direction;
    localStorage.setItem("noxus-language", language);
  }, [language, direction]);
  const value = useMemo(() => ({
    language,
    direction,
    setLanguage,
    t: (key: MessageKey) => messages[language][key],
    text: (english: string, arabic: string) => language === "ar" ? arabic : english,
  }), [language, direction]);
  return <I18n.Provider value={value}>{children}</I18n.Provider>;
}

export function useI18n() {
  const value = useContext(I18n);
  if (!value) throw new Error("I18nProvider is required");
  return value;
}
