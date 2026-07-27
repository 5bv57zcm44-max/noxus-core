import { QueryClient, QueryClientProvider, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from "react-router";
import { api } from "./api";
import { Layout } from "./components/Layout";
import { LoadingState } from "./components/States";
import { I18nProvider, useI18n } from "./i18n";
import { ManagementPage, Marketplace, Modules, Overview, Profile } from "./pages/Pages";
import { SolutionBuilder } from "./pages/SolutionBuilder";

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 30_000, retry: 1 } } });

function Login() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { text } = useI18n();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useMutation({ mutationFn: () => api.login(email, password), onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ["current-user"] }); navigate("/"); } });
  const submit = (event: FormEvent) => { event.preventDefault(); login.mutate(); };
  return <main className="login-page"><section><div className="brand"><span className="brand-mark">N</span><span>NOXUS CORE<small>{text("Community", "المجتمعي")}</small></span></div><h1>{text("Sign in to your workspace", "تسجيل الدخول إلى مساحة العمل")}</h1><p>{text("Use your Frappe site account. Credentials stay on this origin.", "استخدم حساب موقع Frappe. تظل بيانات الدخول على نفس النطاق.")}</p><form onSubmit={submit}><label>{text("Email", "البريد الإلكتروني")}<input type="email" autoComplete="username" required value={email} onChange={(event) => setEmail(event.target.value)} /></label><label>{text("Password", "كلمة المرور")}<input type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} /></label>{login.error && <div className="notice error" role="alert">{login.error.message}</div>}<button className="primary" disabled={login.isPending}>{login.isPending ? text("Signing in…", "جارٍ تسجيل الدخول…") : text("Sign in", "تسجيل الدخول")}</button></form></section></main>;
}

function NotFound() {
  const { text } = useI18n();
  return <section className="state"><strong>404</strong><h1>{text("Page not found", "الصفحة غير موجودة")}</h1><a href="/noxus/">{text("Return to overview", "العودة إلى النظرة العامة")}</a></section>;
}

function ProtectedApplication() {
  const session = useQuery({ queryKey: ["current-user"], queryFn: api.currentUser, retry: false });
  if (session.isLoading) return <LoadingState />;
  if (session.isError || session.data === "Guest") return <Navigate to="/login" replace />;
  return <Layout><Routes>
    <Route index element={<Overview />} />
    <Route path="builder" element={<SolutionBuilder />} />
    <Route path="modules" element={<Modules />} />
    <Route path="modules/:module" element={<ManagementPage kind="data-models" />} />
    <Route path="workflows" element={<ManagementPage kind="workflows" />} />
    <Route path="data-models" element={<ManagementPage kind="data-models" />} />
    <Route path="integrations" element={<ManagementPage kind="integrations" />} />
    <Route path="credentials" element={<ManagementPage kind="credentials" />} />
    <Route path="webhooks" element={<ManagementPage kind="webhooks" />} />
    <Route path="audit" element={<ManagementPage kind="audit" />} />
    <Route path="health" element={<ManagementPage kind="health" />} />
    <Route path="roles" element={<ManagementPage kind="roles" />} />
    <Route path="reports" element={<ManagementPage kind="reports" />} />
    <Route path="marketplace" element={<Marketplace />} />
    <Route path="deployments" element={<ManagementPage kind="deployments" />} />
    <Route path="settings" element={<ManagementPage kind="settings" />} />
    <Route path="profile" element={<Profile />} />
    <Route path="home" element={<Navigate to="/" replace />} />
    <Route path="*" element={<NotFound />} />
  </Routes></Layout>;
}

function RoutedApp() {
  return <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="*" element={<ProtectedApplication />} />
  </Routes>;
}

export default function App() {
  return <QueryClientProvider client={queryClient}><I18nProvider><BrowserRouter basename="/noxus"><RoutedApp /></BrowserRouter></I18nProvider></QueryClientProvider>;
}
