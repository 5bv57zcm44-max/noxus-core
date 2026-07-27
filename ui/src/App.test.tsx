import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

beforeEach(() => {
  history.replaceState({}, "", "/noxus/builder");
  localStorage.clear();
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    if (String(input).includes("frappe.auth.get_logged_user")) {
      return { ok: true, status: 200, statusText: "OK", json: async () => ({ message: "Administrator" }) };
    }
    return { ok: false, status: 503, statusText: "Unavailable", json: async () => ({ exception: "offline" }) };
  }));
});

describe("Solution Builder", () => {
  it("renders all nine real steps and the bundled catalog fallback", async () => {
    render(<App />);
    expect(await screen.findByRole("heading", { name: "Solution Builder" })).toBeInTheDocument();
    expect(screen.getAllByRole("listitem")).toHaveLength(9);
    fireEvent.click(screen.getByRole("button", { name: "2. Modules" }));
    expect(await screen.findByText("NOXUS Core")).toBeInTheDocument();
    expect(await screen.findByText(/bundled catalog/)).toBeInTheDocument();
  });

  it("switches the document to Arabic RTL at runtime", async () => {
    render(<App />);
    await screen.findByRole("heading", { name: "Solution Builder" });
    fireEvent.click(screen.getByRole("button", { name: "العربية" }));
    expect(document.documentElement).toHaveAttribute("dir", "rtl");
    expect(document.documentElement).toHaveAttribute("lang", "ar");
    expect(screen.getByRole("heading", { name: "منشئ الحلول" })).toBeInTheDocument();
  });
});
