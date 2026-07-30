import type { ModuleManifest } from "./types";

function module(name: string, display_name: string, category: string, required: string[] = [], recommended: string[] = []): ModuleManifest {
  return { name, display_name, category, version: "1.0.0", description: `${display_name} module for a modular NOXUS business system.`, publisher: "NOXUS AI", license: "GPL-3.0-or-later", dependencies: { required, recommended, conflicts: [] }, features: ["records", "permissions", "workflow", "reports", "api"], roles: [`${display_name} Manager`], permissions: [`${name}.read`, `${name}.manage`], workflows: [`${display_name} Workflow`], installation_state: "available", compatibility_state: "compatible" };
}

export const bundledCatalog = [
  module("noxus_core", "NOXUS Core", "core"), module("noxus_crm", "CRM", "business", ["noxus_core>=1.0.0"]),
  module("noxus_inventory", "Inventory", "operations", ["noxus_core>=1.0.0"], ["erpnext"]),
  module("noxus_projects", "Projects", "business", ["noxus_core>=1.0.0"]), module("noxus_support", "Support", "business", ["noxus_core>=1.0.0"]),
  module("noxus_maintenance", "Maintenance", "operations", ["noxus_core>=1.0.0", "noxus_inventory>=1.0.0"], ["erpnext"]),
  module("noxus_transport", "Transport", "operations", ["noxus_core>=1.0.0"], ["noxus_maintenance>=1.0.0"]),
  module("noxus_education", "Education", "operations", ["noxus_core>=1.0.0"]), module("noxus_ai", "AI Connector", "intelligence", ["noxus_core>=1.0.0"]),
];
