import { Badge } from "@mantine/core";

/** One status→colour map, so the same status is never two colours. */
const COLORS: Record<string, string> = {
  draft: "gray",
  submitted: "blue",
  under_review: "indigo",
  shortlisted: "violet",
  offer_issued: "orange",
  offer_accepted: "green",
  offer_declined: "gray",
  rejected: "red",
  withdrawn: "gray",
  published: "green",
  closed: "gray",
  cancelled: "violet",
  active: "green",
  // ELM Workflow statuses
  awaiting_substitute: "yellow",
  substitute_declined: "orange",
  pending_unit_head: "blue",
  pending_higher_sanction: "cyan",
  approved: "green",
  completed: "teal",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge color={COLORS[status] ?? "gray"} variant="light" size="sm">
      {status.replace(/_/g, " ")}
    </Badge>
  );
}
