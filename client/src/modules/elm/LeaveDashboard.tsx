import React, { useState, useEffect } from "react";
import {
  Container,
  Tabs,
  Paper,
  Card,
  Badge,
  Button,
  ActionIcon,
  Modal,
  Select,
  TextInput,
  Textarea,
  Checkbox,
  Group,
  Stack,
  Text,
  Title,
  SimpleGrid,
  Timeline,
  Alert,
  LoadingOverlay,
  Menu,
  ThemeIcon,
  Progress,
  Tooltip,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import {
  FaCalendarAlt,
  FaCalendarCheck,
  FaUserCheck,
  FaHistory,
  FaPlus,
  FaCheck,
  FaTimes,
  FaExchangeAlt,
  FaUmbrellaBeach,
  FaClock,
  FaFileAlt,
  FaRedo,
  FaEllipsisH,
  FaPlaneDeparture,
} from "react-icons/fa";

import { PageHeader } from "../../ui/components/PageHeader";
import { DataTable, type Column } from "../../ui/components/DataTable";
import { StatusBadge } from "../../ui/components/StatusBadge";
import type {
  LeaveRequest,
  LeaveBalance,
  HolidayCalendar,
  SubstituteOption,
  DutyResumption,
} from "./types";

export const LeaveDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string | null>("overview");
  const [loading, setLoading] = useState(false);

  // Core Data
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [myRequests, setMyRequests] = useState<LeaveRequest[]>([]);
  const [substituteInbox, setSubstituteInbox] = useState<LeaveRequest[]>([]);
  const [approvalsInbox, setApprovalsInbox] = useState<LeaveRequest[]>([]);
  const [holidays, setHolidays] = useState<HolidayCalendar[]>([]);
  const [substitutesList, setSubstitutesList] = useState<SubstituteOption[]>([]);
  const [resumptionsList, setResumptionsList] = useState<DutyResumption[]>([]);

  // Modals
  const [applyModalOpen, setApplyModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<LeaveRequest | null>(null);

  const [renominateModalOpen, setRenominateModalOpen] = useState(false);
  const [selectedForRenominate, setSelectedForRenominate] = useState<LeaveRequest | null>(null);
  const [newSubId, setNewSubId] = useState<string | null>(null);

  const [extendModalOpen, setExtendModalOpen] = useState(false);
  const [selectedForExtend, setSelectedForExtend] = useState<LeaveRequest | null>(null);
  const [extendDate, setExtendDate] = useState("");

  const [resumptionModalOpen, setResumptionModalOpen] = useState(false);
  const [selectedForResume, setSelectedForResume] = useState<LeaveRequest | null>(null);
  const [resumptionDate, setResumptionDate] = useState("");
  const [resumptionRemarks, setResumptionRemarks] = useState("");

  const [approvalModalOpen, setApprovalModalOpen] = useState(false);
  const [approvalAction, setApprovalAction] = useState<"approve" | "recommend" | "reject">("approve");
  const [approvalComments, setApprovalComments] = useState("");

  // Application form values
  const [applyForm, setApplyForm] = useState({
    leave_type: "CL",
    start_date: "",
    end_date: "",
    half_day: false,
    half_day_period: "forenoon",
    purpose: "",
    station_leave: false,
    station_leave_address: "",
    substitute: "",
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [
        resBal,
        resMyReqs,
        resSubInbox,
        resApprInbox,
        resHol,
        resSubs,
        resResumptions,
      ] = await Promise.all([
        fetch("/api/v1/elm/balances/"),
        fetch("/api/v1/elm/requests/?scope=my"),
        fetch("/api/v1/elm/requests/?scope=substitute"),
        fetch("/api/v1/elm/requests/?scope=approvals"),
        fetch("/api/v1/elm/holidays/?year=2026"),
        fetch("/api/v1/elm/substitutes/"),
        fetch("/api/v1/elm/resumptions/"),
      ]);

      if (resBal.ok) setBalances(await resBal.json());
      if (resMyReqs.ok) setMyRequests(await resMyReqs.json());
      if (resSubInbox.ok) setSubstituteInbox(await resSubInbox.json());
      if (resApprInbox.ok) setApprovalsInbox(await resApprInbox.json());
      if (resHol.ok) setHolidays(await resHol.json());
      if (resSubs.ok) setSubstitutesList(await resSubs.json());
      if (resResumptions.ok) setResumptionsList(await resResumptions.json());
    } catch (err) {
      console.error("Failed to load ELM data:", err);
      notifications.show({
        color: "red",
        title: "Connection Error",
        message: "Failed to connect to ELM backend service.",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleApplySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        leave_type: applyForm.leave_type,
        start_date: applyForm.start_date,
        end_date: applyForm.end_date,
        half_day: applyForm.half_day,
        purpose: applyForm.purpose,
        station_leave: applyForm.station_leave,
      };
      if (applyForm.half_day) payload.half_day_period = applyForm.half_day_period;
      if (applyForm.station_leave) payload.station_leave_address = applyForm.station_leave_address;
      if (applyForm.substitute) payload.substitute = Number(applyForm.substitute);

      const res = await fetch("/api/v1/elm/requests/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Failed to submit leave application.");
      }

      notifications.show({
        color: "green",
        title: "Application Submitted",
        message: `Leave Request #${data.id} has been submitted successfully.`,
      });
      setApplyModalOpen(false);
      setApplyForm({
        leave_type: "CL",
        start_date: "",
        end_date: "",
        half_day: false,
        half_day_period: "forenoon",
        purpose: "",
        station_leave: false,
        station_leave_address: "",
        substitute: "",
      });
      fetchData();
    } catch (err: any) {
      notifications.show({
        color: "red",
        title: "Validation Error",
        message: err.message || "Failed to submit leave request.",
      });
    }
  };

  const handleWithdraw = async (reqId: number) => {
    try {
      const res = await fetch(`/api/v1/elm/requests/${reqId}/withdraw/`, { method: "POST" });
      if (res.ok) {
        notifications.show({
          color: "gray",
          title: "Request Withdrawn",
          message: `Leave request #${reqId} was withdrawn.`,
        });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCancel = async (reqId: number) => {
    if (!window.confirm("Are you sure you want to cancel this approved leave? Quota will be refunded.")) return;
    try {
      const res = await fetch(`/api/v1/elm/requests/${reqId}/cancel/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comments: "Cancelled by employee prior to start date" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to cancel.");

      notifications.show({
        color: "teal",
        title: "Leave Cancelled",
        message: "Approved leave was cancelled and quota refunded to balance.",
      });
      fetchData();
    } catch (err: any) {
      notifications.show({ color: "red", title: "Cancellation Error", message: err.message });
    }
  };

  const handleSubstituteDecision = async (reqId: number, decision: "accept" | "decline") => {
    try {
      const res = await fetch(`/api/v1/elm/requests/${reqId}/substitute-response/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || `Failed to ${decision} substitute request.`);
      }
      notifications.show({
        color: decision === "accept" ? "green" : "orange",
        title: `Substitute Request ${decision === "accept" ? "Accepted" : "Declined"}`,
        message: `Your response has been recorded.`,
      });
      fetchData();
    } catch (err: any) {
      notifications.show({ color: "red", title: "Substitute Response Error", message: err.message });
    }
  };

  const handleRenominate = async () => {
    if (!selectedForRenominate || !newSubId) return;
    try {
      const res = await fetch(`/api/v1/elm/requests/${selectedForRenominate.id}/renominate-substitute/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_substitute_id: Number(newSubId), comments: "Replacement substitute nominated" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to re-nominate substitute.");

      notifications.show({
        color: "blue",
        title: "Substitute Re-Nominated",
        message: "New substitute requested; awaiting their consent.",
      });
      setRenominateModalOpen(false);
      fetchData();
    } catch (err: any) {
      notifications.show({ color: "red", title: "Error", message: err.message });
    }
  };

  const handleExtendSubmit = async () => {
    if (!selectedForExtend || !extendDate) return;
    try {
      const res = await fetch(`/api/v1/elm/requests/${selectedForExtend.id}/extend/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_end_date: extendDate, comments: "Chained extension request" }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to extend leave.");

      notifications.show({
        color: "indigo",
        title: "Extension Requested",
        message: `End date extended to ${extendDate}; re-submitted for approval.`,
      });
      setExtendModalOpen(false);
      fetchData();
    } catch (err: any) {
      notifications.show({ color: "red", title: "Extension Error", message: err.message });
    }
  };

  const handleResumptionSubmit = async () => {
    if (!selectedForResume || !resumptionDate) return;
    try {
      const res = await fetch(`/api/v1/elm/requests/${selectedForResume.id}/resumption/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resumption_date: resumptionDate, remarks: resumptionRemarks }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to submit duty resumption.");

      notifications.show({
        color: "teal",
        title: "Duty Resumption Logged",
        message: `Resumption submitted (${data.resumption_type}). Refundable: ${data.refunded_days} days.`,
      });
      setResumptionModalOpen(false);
      fetchData();
    } catch (err: any) {
      notifications.show({ color: "red", title: "Resumption Error", message: err.message });
    }
  };

  const handleSanctionAction = async () => {
    if (!selectedRequest) return;
    try {
      const res = await fetch(`/api/v1/elm/requests/${selectedRequest.id}/action/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: approvalAction, role_name: "unit_head", comments: approvalComments }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to process sanction.");

      notifications.show({
        color: approvalAction === "approve" ? "green" : approvalAction === "recommend" ? "blue" : "red",
        title: `Request ${approvalAction.toUpperCase()}`,
        message: `Leave Request #${selectedRequest.id} action recorded.`,
      });
      setApprovalModalOpen(false);
      fetchData();
    } catch (err: any) {
      notifications.show({ color: "red", title: "Sanction Error", message: err.message });
    }
  };

  const handleApproveResumption = async (resId: number) => {
    try {
      const res = await fetch(`/api/v1/elm/resumptions/${resId}/action/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role_name: "admin", comments: "Duty resumption verified and approved." }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to approve resumption.");

      notifications.show({
        color: "green",
        title: "Resumption Approved",
        message: `Duty resumption approved; unconsumed days refunded and leave closed.`,
      });
      fetchData();
    } catch (err: any) {
      notifications.show({ color: "red", title: "Approval Error", message: err.message });
    }
  };

  const pendingSubCount = substituteInbox.filter((r) => r.substitute_status === "pending").length;

  // Strongly-typed column specifications for DataTable
  const myRequestColumns: Column<LeaveRequest>[] = [
    {
      key: "id",
      header: "Request ID",
      render: (r: LeaveRequest) => <Text fw={700} fz="sm" ff="monospace">#{r.id}</Text>,
    },
    {
      key: "type",
      header: "Category",
      render: (r: LeaveRequest) => (
        <Badge variant="outline" color="blue">
          {r.leave_type_code || r.leave_type}
        </Badge>
      ),
    },
    {
      key: "period",
      header: "Dates & Duration",
      render: (r: LeaveRequest) => (
        <Stack gap={2}>
          <Text size="sm" fw={600}>
            {r.start_date} to {r.end_date}
          </Text>
          <Group gap={4}>
            {r.half_day && (
              <Badge size="xs" color="gray">
                Half Day ({r.half_day_period})
              </Badge>
            )}
            {r.station_leave && (
              <Badge size="xs" color="indigo">
                Station Leave
              </Badge>
            )}
          </Group>
        </Stack>
      ),
    },
    {
      key: "purpose",
      header: "Purpose",
      render: (r: LeaveRequest) => (
        <Tooltip label={r.purpose} multiline w={280}>
          <Text size="sm" maw={220} truncate>
            {r.purpose}
          </Text>
        </Tooltip>
      ),
    },
    {
      key: "substitute",
      header: "Substitute",
      render: (r: LeaveRequest) =>
        r.substitute_name ? (
          <Stack gap={2}>
            <Text size="xs" fw={600}>{r.substitute_name}</Text>
            <Badge
              size="xs"
              color={
                r.substitute_status === "accepted"
                  ? "green"
                  : r.substitute_status === "declined"
                  ? "red"
                  : "yellow"
              }
            >
              {r.substitute_status}
            </Badge>
          </Stack>
        ) : (
          <Text size="xs" c="dimmed">None</Text>
        ),
    },
    {
      key: "status",
      header: "Status",
      render: (r: LeaveRequest) => <StatusBadge status={r.status} />,
    },
    {
      key: "actions",
      header: "Actions",
      align: "right",
      render: (r: LeaveRequest) => (
        <Group justify="flex-end" gap="xs">
          {/* Substitute Declined recovery action */}
          {r.status === "substitute_declined" && (
            <Button
              size="xs"
              color="orange"
              leftSection={<FaExchangeAlt size={10} />}
              onClick={() => {
                setSelectedForRenominate(r);
                setRenominateModalOpen(true);
              }}
            >
              Re-Nominate
            </Button>
          )}

          {/* Approved actions: Cancel, Extend, Duty Resumption */}
          {r.status === "approved" && (
            <Menu shadow="md" width={180}>
              <Menu.Target>
                <Button size="xs" variant="light" rightSection={<FaEllipsisH size={10} />}>
                  Manage
                </Button>
              </Menu.Target>
              <Menu.Dropdown>
                <Menu.Item
                  leftSection={<FaTimes size={12} color="red" />}
                  onClick={() => handleCancel(r.id)}
                >
                  Cancel Leave
                </Menu.Item>
                <Menu.Item
                  leftSection={<FaCalendarAlt size={12} color="blue" />}
                  onClick={() => {
                    setSelectedForExtend(r);
                    setExtendModalOpen(true);
                  }}
                >
                  Extend Leave
                </Menu.Item>
                <Menu.Item
                  leftSection={<FaClock size={12} color="teal" />}
                  onClick={() => {
                    setSelectedForResume(r);
                    setResumptionModalOpen(true);
                  }}
                >
                  Duty Resumption
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          )}

          {/* Pending withdraw */}
          {["pending_unit_head", "pending_higher_sanction", "awaiting_substitute"].includes(r.status) && (
            <Button
              size="xs"
              variant="subtle"
              color="red"
              onClick={() => handleWithdraw(r.id)}
            >
              Withdraw
            </Button>
          )}

          {/* History Timeline */}
          <ActionIcon
            variant="subtle"
            color="gray"
            onClick={() => {
              setSelectedRequest(r);
              setHistoryModalOpen(true);
            }}
          >
            <FaHistory size={14} />
          </ActionIcon>
        </Group>
      ),
    },
  ];

  const substituteColumns: Column<LeaveRequest>[] = [
    {
      key: "id",
      header: "Request ID",
      render: (r: LeaveRequest) => <Text fw={700} ff="monospace">#{r.id}</Text>,
    },
    {
      key: "applicant",
      header: "Applicant Colleague",
      render: (r: LeaveRequest) => <Text fw={600} size="sm">{r.applicant_name || `User #${r.applicant}`}</Text>,
    },
    {
      key: "period",
      header: "Dates & Category",
      render: (r: LeaveRequest) => (
        <Text size="sm">
          {r.leave_type_code} ({r.start_date} to {r.end_date})
        </Text>
      ),
    },
    {
      key: "purpose",
      header: "Reason / Purpose",
      render: (r: LeaveRequest) => <Text size="sm">{r.purpose}</Text>,
    },
    {
      key: "status",
      header: "My Decision",
      render: (r: LeaveRequest) => (
        <Badge
          color={
            r.substitute_status === "accepted"
              ? "green"
              : r.substitute_status === "declined"
              ? "red"
              : "orange"
          }
        >
          {r.substitute_status}
        </Badge>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      align: "right",
      render: (r: LeaveRequest) =>
        r.substitute_status === "pending" ? (
          <Group justify="flex-end" gap="xs">
            <Button
              size="xs"
              color="green"
              leftSection={<FaCheck size={10} />}
              onClick={() => handleSubstituteDecision(r.id, "accept")}
            >
              Accept
            </Button>
            <Button
              size="xs"
              color="red"
              variant="outline"
              leftSection={<FaTimes size={10} />}
              onClick={() => handleSubstituteDecision(r.id, "decline")}
            >
              Decline
            </Button>
          </Group>
        ) : null,
    },
  ];

  const approvalColumns: Column<LeaveRequest>[] = [
    {
      key: "id",
      header: "Request ID",
      render: (r: LeaveRequest) => <Text fw={700} ff="monospace">#{r.id}</Text>,
    },
    {
      key: "applicant",
      header: "Applicant",
      render: (r: LeaveRequest) => <Text fw={600} size="sm">{r.applicant_name || `User #${r.applicant}`}</Text>,
    },
    {
      key: "type",
      header: "Category",
      render: (r: LeaveRequest) => <Badge color="blue">{r.leave_type_code}</Badge>,
    },
    {
      key: "dates",
      header: "Requested Period",
      render: (r: LeaveRequest) => (
        <Text size="sm">
          {r.start_date} to {r.end_date}
        </Text>
      ),
    },
    {
      key: "substitute",
      header: "Substitute Arrangement",
      render: (r: LeaveRequest) =>
        r.substitute_name ? (
          <Badge color="green" size="xs">
            {r.substitute_name} (Accepted)
          </Badge>
        ) : (
          <Text size="xs" c="dimmed">Not required</Text>
        ),
    },
    {
      key: "status",
      header: "Current State",
      render: (r: LeaveRequest) => <StatusBadge status={r.status} />,
    },
    {
      key: "actions",
      header: "Review",
      align: "right",
      render: (r: LeaveRequest) => (
        <Button
          size="xs"
          color="blue"
          onClick={() => {
            setSelectedRequest(r);
            setApprovalModalOpen(true);
          }}
        >
          Review & Sanction
        </Button>
      ),
    },
  ];

  const resumptionColumns: Column<DutyResumption>[] = [
    {
      key: "req_id",
      header: "Leave Req",
      render: (dr: DutyResumption) => <Text fw={700} ff="monospace">#{dr.leave_request}</Text>,
    },
    {
      key: "applicant",
      header: "Employee",
      render: (dr: DutyResumption) => <Text size="sm" fw={600}>{dr.applicant_name}</Text>,
    },
    {
      key: "date",
      header: "Resumption Date",
      render: (dr: DutyResumption) => <Text size="sm">{dr.resumption_date}</Text>,
    },
    {
      key: "type",
      header: "Type",
      render: (dr: DutyResumption) => (
        <Badge
          color={
            dr.resumption_type === "early"
              ? "indigo"
              : dr.resumption_type === "normal"
              ? "green"
              : "orange"
          }
        >
          {dr.resumption_type.toUpperCase()}
        </Badge>
      ),
    },
    {
      key: "availed",
      header: "Actual Availed",
      render: (dr: DutyResumption) => <Text size="sm">{dr.actual_days_availed} days</Text>,
    },
    {
      key: "refunded",
      header: "Days Refunded",
      render: (dr: DutyResumption) => (
        <Text fw={700} c={Number(dr.refunded_days) > 0 ? "teal" : "dimmed"} size="sm">
          {dr.refunded_days} days
        </Text>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (dr: DutyResumption) => <StatusBadge status={dr.status} />,
    },
    {
      key: "action",
      header: "Action",
      align: "right",
      render: (dr: DutyResumption) =>
        dr.status === "submitted" ? (
          <Button
            size="xs"
            color="green"
            onClick={() => handleApproveResumption(dr.id)}
          >
            Approve Refund
          </Button>
        ) : null,
    },
  ];

  const holidayColumns: Column<HolidayCalendar>[] = [
    {
      key: "date",
      header: "Holiday Date",
      render: (h: HolidayCalendar) => <Text fw={700} size="sm">{h.date}</Text>,
    },
    {
      key: "name",
      header: "Holiday Name",
      render: (h: HolidayCalendar) => <Text fw={600} size="sm">{h.name}</Text>,
    },
    {
      key: "type",
      header: "Classification",
      render: (h: HolidayCalendar) => (
        <Badge color={h.holiday_type === "gazetted" ? "blue" : "violet"}>
          {h.holiday_type === "gazetted" ? "Gazetted Holiday" : "Restricted Holiday (RH)"}
        </Badge>
      ),
    },
    {
      key: "year",
      header: "Academic Year",
      render: (h: HolidayCalendar) => <Text size="sm">{h.academic_year}</Text>,
    },
    {
      key: "rule",
      header: "Institutional Leave Impact",
      render: (h: HolidayCalendar) => (
        <Text size="xs" c="dimmed">
          {h.holiday_type === "gazetted"
            ? "Exempt from Casual Leave debiting (BR-EL-011)"
            : "Eligible for 1-day RH application (BR-EL-003)"}
        </Text>
      ),
    },
  ];

  return (
    <Container size="xl" py="sm">
      <LoadingOverlay visible={loading} />

      {/* Header */}
      <PageHeader
        title="Leave Management (ELM)"
        subtitle="Manage leave entitlements, workflow approvals, substitute responsibilities, and duty resumptions"
        action={
          <Group>
            <Button
              variant="default"
              leftSection={<FaRedo size={12} />}
              onClick={fetchData}
            >
              Refresh
            </Button>
            <Button
              color="blue"
              leftSection={<FaPlus size={12} />}
              onClick={() => setApplyModalOpen(true)}
            >
              Apply for Leave
            </Button>
          </Group>
        }
      />

      {/* Alert banner if substitute requests are pending */}
      {pendingSubCount > 0 && (
        <Alert
          icon={<FaUserCheck />}
          title="Substitute Arrangement Attention Required"
          color="orange"
          mb="lg"
          radius="md"
        >
          You have <strong>{pendingSubCount}</strong> pending substitute arrangement request(s) awaiting your consent.
          Visit the <strong>Substitute Requests</strong> tab to review.
        </Alert>
      )}

      {/* Main Tabs */}
      <Tabs value={activeTab} onChange={setActiveTab} radius="md" variant="pills" mb="xl">
        <Tabs.List mb="lg">
          <Tabs.Tab value="overview" leftSection={<FaUmbrellaBeach size={14} />}>
            Entitlements & Summary
          </Tabs.Tab>
          <Tabs.Tab
            value="my_requests"
            leftSection={<FaFileAlt size={14} />}
            rightSection={<Badge size="xs" circle>{myRequests.length}</Badge>}
          >
            My Applications
          </Tabs.Tab>
          <Tabs.Tab
            value="substitute_inbox"
            leftSection={<FaUserCheck size={14} />}
            rightSection={pendingSubCount > 0 ? <Badge size="xs" color="orange" circle>{pendingSubCount}</Badge> : null}
          >
            Substitute Requests
          </Tabs.Tab>
          <Tabs.Tab
            value="approvals_inbox"
            leftSection={<FaCalendarCheck size={14} />}
            rightSection={<Badge size="xs" color="blue" circle>{approvalsInbox.length}</Badge>}
          >
            Sanctions Inbox
          </Tabs.Tab>
          <Tabs.Tab
            value="resumptions"
            leftSection={<FaClock size={14} />}
            rightSection={<Badge size="xs" color="teal" circle>{resumptionsList.length}</Badge>}
          >
            Duty Resumptions
          </Tabs.Tab>
          <Tabs.Tab value="holidays" leftSection={<FaCalendarAlt size={14} />}>
            Academic Calendar
          </Tabs.Tab>
        </Tabs.List>

        {/* Tab 1: Entitlements & Summary */}
        <Tabs.Panel value="overview">
          <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md" mb="xl">
            {balances.map((b) => {
              const credited = Number(b.credited_days) || 1;
              const used = Number(b.used_days) || 0;
              const bal = Number(b.balance) || 0;
              const percentUsed = Math.min(100, Math.round((used / credited) * 100));

              let icon = <FaUmbrellaBeach size={20} />;
              let themeColor = "blue";
              let badgeRule = "Standard";

              if (b.leave_type_code === "CL") {
                icon = <FaUmbrellaBeach size={20} />;
                themeColor = "blue";
                badgeRule = "Max 8 continuous days";
              } else if (b.leave_type_code === "RH") {
                icon = <FaCalendarAlt size={20} />;
                themeColor = "violet";
                badgeRule = "Calendar Verified";
              } else if (b.leave_type_code === "EL") {
                icon = <FaClock size={20} />;
                themeColor = "teal";
                badgeRule = "300 Days Statutory Cap";
              } else if (b.leave_type_code === "VL") {
                icon = <FaPlaneDeparture size={20} />;
                themeColor = "orange";
                badgeRule = "50% Rollover to EL";
              }

              return (
                <Card key={b.id} padding="lg" radius="md" withBorder shadow="sm">
                  <Group justify="space-between" align="flex-start" mb="xs">
                    <div>
                      <Text fw={700} size="sm" c="dimmed">
                        {b.leave_type_code}
                      </Text>
                      <Text fw={600} size="xs" c="dark.3">
                        {b.leave_type_name}
                      </Text>
                    </div>
                    <ThemeIcon color={themeColor} variant="light" size={40} radius="md">
                      {icon}
                    </ThemeIcon>
                  </Group>

                  <Group align="baseline" gap="xs" my="xs">
                    <Text fz={32} fw={800} c={`${themeColor}.7`}>
                      {bal}
                    </Text>
                    <Text size="xs" fw={500} c="dimmed">
                      days remaining
                    </Text>
                  </Group>

                  <Progress value={percentUsed} color={themeColor} size="sm" radius="xl" mb="xs" />

                  <Group justify="space-between" mt="xs">
                    <Text size="xs" c="dimmed">
                      Used: <strong>{used}</strong>
                    </Text>
                    <Text size="xs" c="dimmed">
                      Quota: <strong>{credited}</strong>
                    </Text>
                  </Group>

                  <Badge size="xs" variant="outline" color={themeColor} mt="md">
                    {badgeRule}
                  </Badge>
                </Card>
              );
            })}
          </SimpleGrid>

          {/* Quick Institutional Rules Overview Card */}
          <Paper p="xl" withBorder radius="md" bg="gray.0">
            <Group justify="space-between" mb="md">
              <Title order={4}>Institutional Leave Guidelines (ELM)</Title>
              <Badge color="blue" variant="light">Academic Rules</Badge>
            </Group>
            <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
              <Paper p="md" withBorder bg="white" radius="md">
                <Text fw={600} size="sm" c="blue.8" mb={4}>Casual Leave (CL &le; 8 Days)</Text>
                <Text size="xs" c="dimmed">
                  Sundays and declared Gazetted Holidays do not count against the Casual Leave balance. Maximum span of continuous leave is 8 days.
                </Text>
              </Paper>
              <Paper p="md" withBorder bg="white" radius="md">
                <Text fw={600} size="sm" c="violet.8" mb={4}>Restricted Holiday (RH = 2 Days)</Text>
                <Text size="xs" c="dimmed">
                  Single-day festival leave that must exist as an approved date in the Academic Holiday Calendar.
                </Text>
              </Paper>
              <Paper p="md" withBorder bg="white" radius="md">
                <Text fw={600} size="sm" c="teal.8" mb={4}>Earned & Vacation Leave (EL / VL)</Text>
                <Text size="xs" c="dimmed">
                  Continuous calendar day debiting applies. Up to 300 days of EL can accumulate. 50% of unavailed Vacation Leave rolls over into EL at year end.
                </Text>
              </Paper>
            </SimpleGrid>
          </Paper>
        </Tabs.Panel>

        {/* Tab 2: My Applications */}
        <Tabs.Panel value="my_requests">
          <Card padding="lg">
            <DataTable<LeaveRequest>
              rows={myRequests}
              loading={loading}
              rowKey={(r: LeaveRequest) => r.id}
              minWidth={950}
              empty={{
                icon: FaFileAlt,
                title: "No leave applications",
                description: "You have not submitted any leave applications for the current academic session.",
              }}
              columns={myRequestColumns}
            />
          </Card>
        </Tabs.Panel>

        {/* Tab 3: Substitute Requests Inbox */}
        <Tabs.Panel value="substitute_inbox">
          <Card padding="lg">
            <DataTable<LeaveRequest>
              rows={substituteInbox}
              loading={loading}
              rowKey={(r: LeaveRequest) => r.id}
              minWidth={850}
              empty={{
                icon: FaUserCheck,
                title: "No substitute requests",
                description: "You have not been nominated as a substitute for any pending leave applications.",
              }}
              columns={substituteColumns}
            />
          </Card>
        </Tabs.Panel>

        {/* Tab 4: Approvals & Sanctions Inbox */}
        <Tabs.Panel value="approvals_inbox">
          <Card padding="lg">
            <DataTable<LeaveRequest>
              rows={approvalsInbox}
              loading={loading}
              rowKey={(r: LeaveRequest) => r.id}
              minWidth={900}
              empty={{
                icon: FaCalendarCheck,
                title: "Queue empty",
                description: "There are no leave requests pending your sanction review.",
              }}
              columns={approvalColumns}
            />
          </Card>
        </Tabs.Panel>

        {/* Tab 5: Duty Resumptions */}
        <Tabs.Panel value="resumptions">
          <Card padding="lg">
            <DataTable<DutyResumption>
              rows={resumptionsList}
              loading={loading}
              rowKey={(dr: DutyResumption) => dr.id}
              minWidth={850}
              empty={{
                icon: FaClock,
                title: "No duty resumptions",
                description: "No duty resumption reports have been logged in the system.",
              }}
              columns={resumptionColumns}
            />
          </Card>
        </Tabs.Panel>

        {/* Tab 6: Academic Calendar */}
        <Tabs.Panel value="holidays">
          <Card padding="lg">
            <DataTable<HolidayCalendar>
              rows={holidays}
              loading={loading}
              rowKey={(h: HolidayCalendar) => h.id}
              minWidth={800}
              empty={{
                icon: FaCalendarAlt,
                title: "Calendar empty",
                description: "No institutional holidays recorded for the current academic session.",
              }}
              columns={holidayColumns}
            />
          </Card>
        </Tabs.Panel>
      </Tabs>

      {/* MODAL 1: Apply for Leave */}
      <Modal
        opened={applyModalOpen}
        onClose={() => setApplyModalOpen(false)}
        title="Apply for Institutional Leave"
        size="lg"
        radius="md"
      >
        <form onSubmit={handleApplySubmit}>
          <Stack gap="md">
            <Select
              label="Leave Category"
              description="Choose institutional leave category to debit"
              required
              data={[
                { value: "CL", label: "Casual Leave (CL &le; 8 continuous days)" },
                { value: "RH", label: "Restricted Holiday (RH 1 day, calendar verified)" },
                { value: "SCL", label: "Special Casual Leave (SCL)" },
                { value: "EL", label: "Earned Leave (EL - continuous calendar days)" },
                { value: "VL", label: "Vacation Leave (VL)" },
                { value: "COL", label: "Commuted Leave (COL)" },
              ]}
              value={applyForm.leave_type}
              onChange={(val) => setApplyForm((prev) => ({ ...prev, leave_type: val || "CL" }))}
            />

            <SimpleGrid cols={2} spacing="md">
              <TextInput
                label="Start Date"
                type="date"
                required
                value={applyForm.start_date}
                onChange={(e) => setApplyForm((prev) => ({ ...prev, start_date: e.target.value }))}
              />
              <TextInput
                label="End Date"
                type="date"
                required
                value={applyForm.end_date}
                onChange={(e) => setApplyForm((prev) => ({ ...prev, end_date: e.target.value }))}
              />
            </SimpleGrid>

            <Group align="center">
              <Checkbox
                label="Half-Day Leave"
                checked={applyForm.half_day}
                onChange={(e) => setApplyForm((prev) => ({ ...prev, half_day: e.currentTarget.checked }))}
              />
              {applyForm.half_day && (
                <Select
                  size="xs"
                  data={[
                    { value: "forenoon", label: "Forenoon (FN)" },
                    { value: "afternoon", label: "Afternoon (AN)" },
                  ]}
                  value={applyForm.half_day_period}
                  onChange={(val) => setApplyForm((prev) => ({ ...prev, half_day_period: val || "forenoon" }))}
                />
              )}
            </Group>

            <Checkbox
              label="Station Leave Permission (Leaving Headquarters)"
              description="Required if traveling outside station during leave"
              checked={applyForm.station_leave}
              onChange={(e) => setApplyForm((prev) => ({ ...prev, station_leave: e.currentTarget.checked }))}
            />

            {applyForm.station_leave && (
              <TextInput
                label="Station Leave Contact Address & Phone *"
                required={applyForm.station_leave}
                placeholder="Residential/transit address and phone while out of station"
                value={applyForm.station_leave_address}
                onChange={(e) => setApplyForm((prev) => ({ ...prev, station_leave_address: e.target.value }))}
              />
            )}

            <Select
              label="Nominate Colleague as Substitute"
              description="Colleague covering academic/administrative responsibilities"
              placeholder="Search faculty or staff colleague..."
              clearable
              searchable
              data={substitutesList.map((s) => ({
                value: String(s.user_id),
                label: `${s.display_name} (${s.username} - ${s.discipline || s.kind})`,
              }))}
              value={applyForm.substitute}
              onChange={(val) => setApplyForm((prev) => ({ ...prev, substitute: val || "" }))}
            />

            <Textarea
              label="Reason / Purpose"
              required
              rows={3}
              placeholder="Institutional justification or personal reason..."
              value={applyForm.purpose}
              onChange={(e) => setApplyForm((prev) => ({ ...prev, purpose: e.target.value }))}
            />

            <Group justify="flex-end" mt="md">
              <Button variant="default" onClick={() => setApplyModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" color="blue">
                Submit Leave Application
              </Button>
            </Group>
          </Stack>
        </form>
      </Modal>

      {/* MODAL 2: Audit History Timeline */}
      <Modal
        opened={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
        title={`Workflow History & Audit Trail (#${selectedRequest?.id})`}
        size="md"
        radius="md"
      >
        {selectedRequest && (
          <Timeline active={(selectedRequest.action_logs?.length || 1) - 1} bulletSize={24} lineWidth={2}>
            {selectedRequest.action_logs && selectedRequest.action_logs.length > 0 ? (
              selectedRequest.action_logs.map((log) => (
                <Timeline.Item
                  key={log.id}
                  title={<Text fw={600} size="sm">{log.action.replace(/_/g, " ").toUpperCase()}</Text>}
                  bullet={<FaCheck size={12} />}
                >
                  <Text size="xs" c="dimmed">
                    By: <strong>{log.actor_name || log.actor}</strong> ({log.role_name}) &bull;{" "}
                    {new Date(log.created_at).toLocaleString()}
                  </Text>
                  {log.comments && (
                    <Text size="xs" mt={4} c="gray.7">
                      Remarks: "{log.comments}"
                    </Text>
                  )}
                </Timeline.Item>
              ))
            ) : (
              <Timeline.Item title="Application Logged">
                <Text size="xs" c="dimmed">Initial submission.</Text>
              </Timeline.Item>
            )}
          </Timeline>
        )}
      </Modal>

      {/* MODAL 3: Re-Nominate Substitute */}
      <Modal
        opened={renominateModalOpen}
        onClose={() => setRenominateModalOpen(false)}
        title="Re-Nominate Substitute Colleague"
      >
        <Stack gap="md">
          <Text size="sm">
            The previous substitute declined your arrangement. Please select an alternative colleague to cover duties:
          </Text>
          <Select
            label="Replacement Substitute"
            placeholder="Choose colleague..."
            searchable
            data={substitutesList.map((s) => ({
              value: String(s.user_id),
              label: `${s.display_name} (${s.discipline || s.kind})`,
            }))}
            value={newSubId}
            onChange={setNewSubId}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setRenominateModalOpen(false)}>Cancel</Button>
            <Button color="blue" onClick={handleRenominate}>Submit Re-Nomination</Button>
          </Group>
        </Stack>
      </Modal>

      {/* MODAL 4: Extend Leave */}
      <Modal
        opened={extendModalOpen}
        onClose={() => setExtendModalOpen(false)}
        title="Extend Approved Leave"
      >
        <Stack gap="md">
          <Text size="sm">
            Current leave ends on <strong>{selectedForExtend?.end_date}</strong>. Specify a new continuous end date:
          </Text>
          <TextInput
            label="New End Date"
            type="date"
            required
            value={extendDate}
            onChange={(e) => setExtendDate(e.target.value)}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setExtendModalOpen(false)}>Cancel</Button>
            <Button color="indigo" onClick={handleExtendSubmit}>Submit Extension</Button>
          </Group>
        </Stack>
      </Modal>

      {/* MODAL 5: Duty Resumption */}
      <Modal
        opened={resumptionModalOpen}
        onClose={() => setResumptionModalOpen(false)}
        title="Report Resumption of Duty"
      >
        <Stack gap="md">
          <Text size="sm">
            Approved period was from <strong>{selectedForResume?.start_date}</strong> to{" "}
            <strong>{selectedForResume?.end_date}</strong>.
          </Text>
          <TextInput
            label="Actual Duty Resumption Date"
            type="date"
            required
            value={resumptionDate}
            onChange={(e) => setResumptionDate(e.target.value)}
          />
          <Textarea
            label="Remarks / Prefix-Suffix Details"
            placeholder="Specify reason if returning early or late..."
            value={resumptionRemarks}
            onChange={(e) => setResumptionRemarks(e.target.value)}
          />
          <Group justify="flex-end">
            <Button variant="default" onClick={() => setResumptionModalOpen(false)}>Cancel</Button>
            <Button color="teal" onClick={handleResumptionSubmit}>Submit Duty Resumption</Button>
          </Group>
        </Stack>
      </Modal>

      {/* MODAL 6: Sanction Action Modal */}
      <Modal
        opened={approvalModalOpen}
        onClose={() => setApprovalModalOpen(false)}
        title={`Sanction Authority Decision (#${selectedRequest?.id})`}
      >
        <Stack gap="md">
          <Text size="sm">
            Applicant: <strong>{selectedRequest?.applicant_name}</strong> | Category:{" "}
            <strong>{selectedRequest?.leave_type_code}</strong> | Dates:{" "}
            <strong>{selectedRequest?.start_date} to {selectedRequest?.end_date}</strong>
          </Text>
          <Text size="xs" c="dimmed">Purpose: "{selectedRequest?.purpose}"</Text>

          <Select
            label="Sanction Action"
            data={[
              { value: "approve", label: "Approve Leave (Debit Quota)" },
              { value: "recommend", label: "Recommend & Forward to Higher Authority" },
              { value: "reject", label: "Reject Leave Request" },
            ]}
            value={approvalAction}
            onChange={(val: any) => setApprovalAction(val)}
          />

          <Textarea
            label="Sanction Remarks / Comments"
            placeholder="Official comments..."
            value={approvalComments}
            onChange={(e) => setApprovalComments(e.target.value)}
          />

          <Group justify="flex-end">
            <Button variant="default" onClick={() => setApprovalModalOpen(false)}>Cancel</Button>
            <Button
              color={approvalAction === "approve" ? "green" : approvalAction === "recommend" ? "blue" : "red"}
              onClick={handleSanctionAction}
            >
              Confirm Action
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
};

export default LeaveDashboard;
