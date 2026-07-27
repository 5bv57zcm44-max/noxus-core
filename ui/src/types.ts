export type Direction = "ltr" | "rtl";
export type Language = "en" | "ar";

export interface ModuleManifest {
  name: string;
  display_name: string;
  version: string;
  description: string;
  publisher: string;
  license: string;
  category: string;
  dependencies: { required: string[]; recommended: string[]; conflicts: string[] };
  features: string[];
  roles: string[];
  permissions: string[];
  workflows: string[];
  installation_state?: "available" | "installed";
  compatibility_state?: "compatible" | "incompatible";
}

export interface Blueprint {
  schema_version: 1;
  name: string;
  industry: string;
  language: "english" | "arabic" | "both";
  modules: Array<{ name: string; version: string; features: string[]; install_order: number }>;
  roles: string[];
  workflows: string[];
  integrations: string[];
  branding: { product_name: string; accent_color: string; default_direction: Direction };
  deployment: { environment: "development" | "production"; with_erpnext: boolean; http_port: number };
  generator_version: string;
  checksum: string;
}
