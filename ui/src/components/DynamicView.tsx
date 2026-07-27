import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { api } from "../api";
import { useI18n } from "../i18n";
import { EmptyState, ErrorState, LoadingState } from "./States";

type Mode = "list" | "kanban" | "calendar" | "form";
export function DynamicView({ doctype, mode = "list" }: { doctype: string; mode?: Mode }) {
  const { text } = useI18n();
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const [creating, setCreating] = useState(false);
  const [draft, setDraft] = useState<Record<string, unknown>>({});
  const isCreating = creating || (mode === "form" && !selected);
  const metadata = useQuery({ queryKey: ["meta", doctype], queryFn: () => api.meta(doctype) });
  const fields = useMemo(() => metadata.data?.fields.filter((field) => !["Section Break", "Column Break", "HTML"].includes(field.fieldtype)).slice(0, 8) ?? [], [metadata.data]);
  const records = useQuery({ queryKey: ["records", doctype, fields], queryFn: () => api.list<Record<string, unknown>>(doctype, ["name", ...fields.map((field) => field.fieldname)]) , enabled: fields.length > 0 });
  const save = useMutation({
    mutationFn: () => isCreating ? api.create(doctype, draft) : api.update(doctype, String(selected?.name), draft),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["records", doctype] });
      setSelected(null); setCreating(false); setDraft({});
    },
  });
  if (metadata.isLoading || records.isLoading) return <LoadingState />;
  if (metadata.error || records.error) return <ErrorState error={(metadata.error ?? records.error) as Error} retry={() => void Promise.all([metadata.refetch(), records.refetch()])} />;
  const openRecord = (record: Record<string, unknown>) => { setSelected(record); setDraft(record); setCreating(false); };
  const newRecord = () => { setSelected({}); setDraft({}); setCreating(true); };
  if (isCreating || selected) return <section className="form-view"><button onClick={() => { setSelected(null); setCreating(false); }}>← {text("Records", "السجلات")}</button><h2>{isCreating ? text(`New ${doctype}`, `سجل ${doctype} جديد`) : doctype}</h2>{fields.filter((field) => !field.read_only).map((field) => <label key={field.fieldname}>{field.label}<input required={Boolean(field.reqd)} value={String(draft[field.fieldname] ?? "")} onChange={(event) => setDraft((value) => ({ ...value, [field.fieldname]: event.target.value }))} /></label>)}{save.error && <div className="notice error" role="alert">{save.error.message}</div>}<button className="primary" onClick={() => save.mutate()} disabled={save.isPending}>{save.isPending ? text("Saving…", "جارٍ الحفظ…") : text("Save", "حفظ")}</button></section>;
  if (!records.data?.length) return <EmptyState action={<button onClick={newRecord}>{text("Create record", "إنشاء سجل")}</button>} />;
  if (mode === "kanban") return <><button className="primary" onClick={newRecord}>{text("Create record", "إنشاء سجل")}</button><div className="kanban">{[{ value: "Open", ar: "مفتوح" }, { value: "In Progress", ar: "قيد التنفيذ" }, { value: "Complete", ar: "مكتمل" }].map((status) => <section key={status.value}><h3>{text(status.value, status.ar)}</h3>{records.data.filter((record) => record.status === status.value).map((record) => <button key={String(record.name)} onClick={() => openRecord(record)}>{String(record.title ?? record.subject ?? record.name)}</button>)}</section>)}</div></>;
  if (mode === "calendar") return <><button className="primary" onClick={newRecord}>{text("Create record", "إنشاء سجل")}</button><div className="calendar">{records.data.map((record) => <button key={String(record.name)} onClick={() => openRecord(record)}><time>{String(record.starts_at ?? record.due_date ?? text("Unscheduled", "غير مجدول"))}</time><strong>{String(record.title ?? record.name)}</strong></button>)}</div></>;
  return <><button className="primary" onClick={newRecord}>{text("Create record", "إنشاء سجل")}</button><div className="table-wrap"><table><thead><tr>{fields.map((field) => <th key={field.fieldname}>{field.label}</th>)}</tr></thead><tbody>{records.data.map((record) => <tr key={String(record.name)} onClick={() => openRecord(record)} onKeyDown={(event) => { if (event.key === "Enter") openRecord(record); }} tabIndex={0}>{fields.map((field) => <td key={field.fieldname}>{String(record[field.fieldname] ?? "—")}</td>)}</tr>)}</tbody></table></div></>;
}
