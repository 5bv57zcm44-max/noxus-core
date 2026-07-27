type FrappeResponse<T> = { message: T; exc_type?: string };

function csrfToken(): string {
  return document.cookie.split("; ").find((item) => item.startsWith("csrf_token="))?.split("=")[1] ?? "";
}

export async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    credentials: "include",
    ...init,
    headers: { Accept: "application/json", "Content-Type": "application/json", "X-Frappe-CSRF-Token": csrfToken(), ...init.headers },
  });
  const body = await response.json().catch(() => ({})) as Partial<FrappeResponse<T>> & { data?: T; exception?: string };
  if (!response.ok) throw new Error(body.exception ?? `${response.status} ${response.statusText}`);
  if ("message" in body) return body.message as T;
  if ("data" in body) return body.data as T;
  return body as T;
}

export const api = {
  currentUser: () => request<string>("/api/method/frappe.auth.get_logged_user"),
  login: (usr: string, pwd: string) => request<{ full_name: string }>("/api/method/login", { method: "POST", body: JSON.stringify({ usr, pwd }) }),
  logout: () => request("/api/method/logout", { method: "POST" }),
  catalog: () => request<{ modules: import("./types").ModuleManifest[]; remote_marketplace: { available: boolean; reason: string } }>("/api/v2/method/noxus_core.api.v1.catalog"),
  resolve: (modules: string[]) => request<{ install_order: string[]; warnings: string[] }>("/api/v2/method/noxus_core.api.v1.resolve_modules", { method: "POST", body: JSON.stringify({ request: { modules, platform: { python: "3.14.6", frappe: "16.28.0" } } }) }),
  apply: (blueprint: import("./types").Blueprint, idempotency_key: string) => request<{ deployment: string; stage: string }>("/api/v2/method/noxus_core.api.v1.apply_blueprint", { method: "POST", body: JSON.stringify({ request: { blueprint, idempotency_key } }) }),
  list: <T,>(doctype: string, fields: string[] = ["name", "modified"]) => request<T[]>(`/api/resource/${encodeURIComponent(doctype)}?fields=${encodeURIComponent(JSON.stringify(fields))}&limit_page_length=100`),
  create: <T,>(doctype: string, values: Record<string, unknown>) => request<T>(`/api/resource/${encodeURIComponent(doctype)}`, { method: "POST", body: JSON.stringify(values) }),
  update: <T,>(doctype: string, name: string, values: Record<string, unknown>) => request<T>(`/api/resource/${encodeURIComponent(doctype)}/${encodeURIComponent(name)}`, { method: "PUT", body: JSON.stringify(values) }),
  meta: (doctype: string) => request<{ fields: Array<{ fieldname: string; label: string; fieldtype: string; options?: string; reqd?: number; read_only?: number }> }>(`/api/method/frappe.desk.form.load.getdoctype?doctype=${encodeURIComponent(doctype)}`),
};
