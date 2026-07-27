import type { ReactNode } from "react";
import { useI18n } from "../i18n";

export function LoadingState() {
  const { t } = useI18n();
  return <div className="state" role="status"><span className="spinner" aria-hidden="true" />{t("loading")}</div>;
}
export function EmptyState({ action }: { action?: ReactNode }) {
  const { t } = useI18n();
  return <div className="state"><strong>{t("empty")}</strong>{action}</div>;
}
export function ErrorState({ error, retry }: { error: Error; retry?: () => void }) {
  const { t } = useI18n();
  return <div className="state error" role="alert"><strong>{error.message}</strong>{retry && <button onClick={retry}>{t("retry")}</button>}</div>;
}
export function PermissionDenied() {
  const { t } = useI18n();
  return <div className="state error" role="alert"><strong>403</strong><span>{t("denied")}</span></div>;
}
