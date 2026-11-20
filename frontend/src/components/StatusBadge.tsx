import { ROTULO_STATUS } from "../lib/format";

export default function StatusBadge({ status }: { status: string }) {
  return <span className={`badge badge-${status.toLowerCase().replace(/_/g, "-")}`}>{ROTULO_STATUS[status] ?? status}</span>;
}
