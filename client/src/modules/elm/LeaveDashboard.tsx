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
  Table,
  Timeline,
  Alert,
  LoadingOverlay,
  Menu,
  Progress,
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
} from "react-icons/fa";

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

  // Data states
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [myRequests, setMyRequests] = useState<LeaveRequest[]>([]);
  const [substituteInbox, setSubstituteInbox] = useState<LeaveRequest[]>([]);
  const [approvalsInbox, setApprovalsInbox] = useState<LeaveRequest[]>([]);
  const [holidays, setHolidays] = useState<HolidayCalendar[]>([]);
  const [substitutesList, setSubstitutesList] = useState<SubstituteOption[]>([]);
  const [resumptionsList, setResumptionsList] = useState<DutyResumption[]>([]);

  // Modals state
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

  // Application form
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
        title: "Network Error",
        message: "Failed to connect to ELM backend service.",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Handle Application Submit
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

  // Withdraw
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

  // Cancel Approved Leave
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

  // Substitute Response
  const handleSubstituteDecision = async (reqId: number, decision: "accept" | "decline") => {
    try {
      const res = await fetch(`/api/v1/elm/requests/${reqId}/substitute-response/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision }),
      });
      if (res.ok) {
        notifications.show({
          color: decision === "accept" ? "green" : "orange",
          title: `Substitute Request ${decision === "accept" ? "Accepted" : "Declined"}`,
          message: `Your decision has been logged and the workflow advanced.`,
        });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Re-Nominate Substitute
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

  // Extension Submit
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

  // Resumption Submit
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

  // Sanction Action (Approve / Recommend / Reject)
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

  // Approve Duty Resumption
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

  // Helper badge color
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return <Badge color="green" variant="light">Approved</Badge>;
      case "completed":
        return <Badge color="teal" variant="filled">Completed</Badge>;
      case "rejected":
        return <Badge color="red" variant="light">Rejected</Badge>;
      case "cancelled":
        return <Badge color="violet" variant="light">Cancelled</Badge>;
      case "withdrawn":
        return <Badge color="gray" variant="light">Withdrawn</Badge>;
      case "substitute_declined":
        return <Badge color="orange" variant="filled">Substitute Declined</Badge>;
      case "awaiting_substitute":
        return <Badge color="yellow" variant="light">Awaiting Substitute</Badge>;
      case "pending_unit_head":
        return <Badge color="blue" variant="light">Pending Unit Head</Badge>;
      case "pending_higher_sanction":
        return <Badge color="cyan" variant="light">Pending Higher Sanction</Badge>;
      default:
        return <Badge color="gray">{status}</Badge>;
    }
  };

  return (
    <Container size="xl" py="lg">
      <LoadingOverlay visible={loading} />

      {/* Header */}
      <Paper p="md" mb="lg" radius="md" withBorder>
        <Group justify="space-between" align="center">
          <div>
            <Title order={2} c="blue.8">Employee Leave Management (ELM)</Title>
            <Text size="sm" c="dimmed">
              Institutional portal for leave quotas, substitute arrangement, multi-tier sanctions, and duty resumption.
            </Text>
          </div>
          <Group>
            <Button
              leftSection={<FaRedo />}
              variant="default"
              onClick={fetchData}
            >
              Refresh
            </Button>
            <Button
              leftSection={<FaPlus />}
              color="blue"
              onClick={() => setApplyModalOpen(true)}
            >
              Apply for Leave
            </Button>
          </Group>
        </Group>
      </Paper>

      {/* Substitute Alert banner if pending */}
      {substituteInbox.filter((r) => r.substitute_status === "pending").length > 0 && (
        <Alert
          icon={<FaUserCheck />}
          title="Substitute Arrangement Attention Required"
          color="orange"
          mb="lg"
          radius="md"
        >
          You have{" "}
          <strong>
            {substituteInbox.filter((r) => r.substitute_status === "pending").length}
          </strong>{" "}
          pending substitute arrangement request(s) awaiting your consent. Visit the "Substitute Requests" tab to review.
        </Alert>
      )}

      {/* Main Tabs */}
      <Tabs value={activeTab} onChange={setActiveTab} radius="md" variant="outline">
        <Tabs.List mb="md">
          <Tabs.Tab value="overview" leftSection={<FaUmbrellaBeach />}>
            Quotas & Balances
          </Tabs.Tab>
          <Tabs.Tab
            value="my_requests"
            leftSection={<FaFileAlt />}
            rightSection={<Badge size="xs" circle>{myRequests.length}</Badge>}
          >
            My Applications
          </Tabs.Tab>
          <Tabs.Tab
            value="substitute_inbox"
            leftSection={<FaUserCheck />}
            rightSection={
              substituteInbox.filter((r) => r.substitute_status === "pending").length > 0 ? (
                <Badge size="xs" color="orange" circle>
                  {substituteInbox.filter((r) => r.substitute_status === "pending").length}
                </Badge>
              ) : null
            }
          >
            Substitute Requests
          </Tabs.Tab>
          <Tabs.Tab
            value="approvals_inbox"
            leftSection={<FaCalendarCheck />}
            rightSection={<Badge size="xs" color="blue" circle>{approvalsInbox.length}</Badge>}
          >
            Approvals & Sanctions
          </Tabs.Tab>
          <Tabs.Tab
            value="resumptions"
            leftSection={<FaClock />}
            rightSection={<Badge size="xs" color="teal" circle>{resumptionsList.length}</Badge>}
          >
            Duty Resumptions
          </Tabs.Tab>
          <Tabs.Tab value="holidays" leftSection={<FaCalendarAlt />}>
            Academic Holidays
          </Tabs.Tab>
        </Tabs.List>

        {/* Tab 1: Overview & Balances */}
        <Tabs.Panel value="overview">
          <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md" mb="xl">
            {balances.map((b) => {
              const credited = Number(b.credited_days) || 1;
              const used = Number(b.used_days) || 0;
              const bal = Number(b.balance) || 0;
              const percentUsed = Math.min(100, Math.round((used / credited) * 100));

              return (
                <Card key={b.id} withBorder padding="lg" radius="md">
                  <Group justify="space-between" mb="xs">
                    <Text fw={700} size="sm" c="dimmed">
                      {b.leave_type_code} - {b.leave_type_name}
                    </Text>
                    <Badge size="sm" variant="dot" color={bal > 0 ? "teal" : "red"}>
                      {b.year}
                    </Badge>
                  </Group>
                  <Text fz={28} fw={800} c="blue.7" my="xs">
                    {bal}{" "}
                    <Text span size="xs" fw={500} c="dimmed">
                      days left
                    </Text>
                  </Text>
                  <Progress value={percentUsed} color="blue" size="sm" radius="xl" mb="xs" />
                  <Group justify="space-between" mt="xs">
                    <Text size="xs" c="dimmed">
                      Used: <strong>{used}</strong>
                    </Text>
                    <Text size="xs" c="dimmed">
                      Quota: <strong>{credited}</strong>
                    </Text>
                  </Group>
                </Card>
              );
            })}
          </SimpleGrid>

          {/* Quick Institutional Rules Overview Card */}
          <Paper p="lg" withBorder radius="md" bg="gray.0">
            <Title order={4} mb="xs">Key Institutional Leave Rules (ELM)</Title>
            <SimpleGrid cols={{ base: 1, md: 3 }} spacing="md">
              <Paper p="sm" withBorder bg="white" radius="sm">
                <Text fw={600} size="sm" c="blue.8">Casual Leave (CL &le; 8 Days)</Text>
                <Text size="xs" c="dimmed">
                  Intervening Sundays and declared Gazetted Holidays do NOT count against CL balance. Maximum 8 continuous days.
                </Text>
              </Paper>
              <Paper p="sm" withBorder bg="white" radius="sm">
                <Text fw={600} size="sm" c="blue.8">Restricted Holidays (RH = 2 Days)</Text>
                <Text size="xs" c="dimmed">
                  Must be availed as single day on declared festival dates present in the Institutional Holiday Calendar.
                </Text>
              </Paper>
              <Paper p="sm" withBorder bg="white" radius="sm">
                <Text fw={600} size="sm" c="blue.8">Earned & Vacation Leave (EL / VL)</Text>
                <Text size="xs" c="dimmed">
                  Continuous day counting applies. Maximum EL accumulation is 300 days. 50% of unavailed VL rolls over into EL at year end.
                </Text>
              </Paper>
            </SimpleGrid>
          </Paper>
        </Tabs.Panel>

        {/* Tab 2: My Applications */}
        <Tabs.Panel value="my_requests">
          <Paper withBorder radius="md">
            <Table striped highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>ID</Table.Th>
                  <Table.Th>Type</Table.Th>
                  <Table.Th>Dates</Table.Th>
                  <Table.Th>Purpose</Table.Th>
                  <Table.Th>Substitute</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th style={{ textAlign: "right" }}>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {myRequests.length === 0 ? (
                  <Table.Tr>
                    <Table.Td colSpan={7} style={{ textAlign: "center" }} py="xl">
                      <Text c="dimmed">No leave applications found. Click "+ Apply for Leave" to submit one.</Text>
                    </Table.Td>
                  </Table.Tr>
                ) : (
                  myRequests.map((req) => (
                    <Table.Tr key={req.id}>
                      <Table.Td fw={700}>#{req.id}</Table.Td>
                      <Table.Td>
                        <Badge variant="outline">{req.leave_type_code || req.leave_type}</Badge>
                      </Table.Td>
                      <Table.Td>
                        <Text size="sm" fw={600}>
                          {req.start_date} to {req.end_date}
                        </Text>
                        {req.half_day && (
                          <Badge size="xs" color="gray">
                            Half Day ({req.half_day_period})
                          </Badge>
                        )}
                        {req.station_leave && (
                          <Badge size="xs" color="indigo" ml={4}>
                            Station Leave
                          </Badge>
                        )}
                      </Table.Td>
                      <Table.Td maw={200} style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {req.purpose}
                      </Table.Td>
                      <Table.Td>
                        {req.substitute_name ? (
                          <Stack gap={2}>
                            <Text size="xs" fw={600}>{req.substitute_name}</Text>
                            <Badge size="xs" color={req.substitute_status === "accepted" ? "green" : req.substitute_status === "declined" ? "red" : "yellow"}>
                              {req.substitute_status}
                            </Badge>
                          </Stack>
                        ) : (
                          <Text size="xs" c="dimmed">None</Text>
                        )}
                      </Table.Td>
                      <Table.Td>{getStatusBadge(req.status)}</Table.Td>
                      <Table.Td style={{ textAlign: "right" }}>
                        <Group justify="flex-end" gap="xs">
                          {/* Substitute Declined recovery action */}
                          {req.status === "substitute_declined" && (
                            <Button
                              size="xs"
                              color="orange"
                              leftSection={<FaExchangeAlt />}
                              onClick={() => {
                                setSelectedForRenominate(req);
                                setRenominateModalOpen(true);
                              }}
                            >
                              Re-Nominate
                            </Button>
                          )}

                          {/* Approved actions: Cancel, Extend, Duty Resumption */}
                          {req.status === "approved" && (
                            <Menu shadow="md" width={180}>
                              <Menu.Target>
                                <Button size="xs" variant="light" rightSection={<FaEllipsisH />}>
                                  Manage
                                </Button>
                              </Menu.Target>
                              <Menu.Dropdown>
                                <Menu.Item
                                  leftSection={<FaTimes color="red" />}
                                  onClick={() => handleCancel(req.id)}
                                >
                                  Cancel Leave
                                </Menu.Item>
                                <Menu.Item
                                  leftSection={<FaCalendarAlt color="blue" />}
                                  onClick={() => {
                                    setSelectedForExtend(req);
                                    setExtendModalOpen(true);
                                  }}
                                >
                                  Extend Leave
                                </Menu.Item>
                                <Menu.Item
                                  leftSection={<FaClock color="teal" />}
                                  onClick={() => {
                                    setSelectedForResume(req);
                                    setResumptionModalOpen(true);
                                  }}
                                >
                                  Duty Resumption
                                </Menu.Item>
                              </Menu.Dropdown>
                            </Menu>
                          )}

                          {/* Pending withdraw */}
                          {["pending_unit_head", "pending_higher_sanction", "awaiting_substitute"].includes(req.status) && (
                            <Button
                              size="xs"
                              variant="subtle"
                              color="red"
                              onClick={() => handleWithdraw(req.id)}
                            >
                              Withdraw
                            </Button>
                          )}

                          {/* History Timeline */}
                          <ActionIcon
                            variant="subtle"
                            color="gray"
                            onClick={() => {
                              setSelectedRequest(req);
                              setHistoryModalOpen(true);
                            }}
                          >
                            <FaHistory />
                          </ActionIcon>
                        </Group>
                      </Table.Td>
                    </Table.Tr>
                  ))
                )}
              </Table.Tbody>
            </Table>
          </Paper>
        </Tabs.Panel>

        {/* Tab 3: Substitute Requests Inbox */}
        <Tabs.Panel value="substitute_inbox">
          <Paper withBorder radius="md">
            <Table striped highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Request ID</Table.Th>
                  <Table.Th>Applicant</Table.Th>
                  <Table.Th>Type & Dates</Table.Th>
                  <Table.Th>Purpose</Table.Th>
                  <Table.Th>My Consent Status</Table.Th>
                  <Table.Th style={{ textAlign: "right" }}>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {substituteInbox.length === 0 ? (
                  <Table.Tr>
                    <Table.Td colSpan={6} style={{ textAlign: "center" }} py="xl">
                      <Text c="dimmed">No substitute consent requests assigned to you.</Text>
                    </Table.Td>
                  </Table.Tr>
                ) : (
                  substituteInbox.map((req) => (
                    <Table.Tr key={req.id}>
                      <Table.Td fw={700}>#{req.id}</Table.Td>
                      <Table.Td fw={600}>{req.applicant_name || `User #${req.applicant}`}</Table.Td>
                      <Table.Td>
                        <Text size="sm">{req.leave_type_code} ({req.start_date} to {req.end_date})</Text>
                      </Table.Td>
                      <Table.Td>{req.purpose}</Table.Td>
                      <Table.Td>
                        <Badge color={req.substitute_status === "accepted" ? "green" : req.substitute_status === "declined" ? "red" : "orange"}>
                          {req.substitute_status}
                        </Badge>
                      </Table.Td>
                      <Table.Td style={{ textAlign: "right" }}>
                        {req.substitute_status === "pending" && (
                          <Group justify="flex-end" gap="xs">
                            <Button
                              size="xs"
                              color="green"
                              leftSection={<FaCheck />}
                              onClick={() => handleSubstituteDecision(req.id, "accept")}
                            >
                              Accept
                            </Button>
                            <Button
                              size="xs"
                              color="red"
                              variant="outline"
                              leftSection={<FaTimes />}
                              onClick={() => handleSubstituteDecision(req.id, "decline")}
                            >
                              Decline
                            </Button>
                          </Group>
                        )}
                      </Table.Td>
                    </Table.Tr>
                  ))
                )}
              </Table.Tbody>
            </Table>
          </Paper>
        </Tabs.Panel>

        {/* Tab 4: Approvals & Sanctions Inbox */}
        <Tabs.Panel value="approvals_inbox">
          <Paper withBorder radius="md">
            <Table striped highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Request ID</Table.Th>
                  <Table.Th>Applicant</Table.Th>
                  <Table.Th>Category</Table.Th>
                  <Table.Th>Period</Table.Th>
                  <Table.Th>Substitute Status</Table.Th>
                  <Table.Th>Current Status</Table.Th>
                  <Table.Th style={{ textAlign: "right" }}>Sanction Action</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {approvalsInbox.length === 0 ? (
                  <Table.Tr>
                    <Table.Td colSpan={7} style={{ textAlign: "center" }} py="xl">
                      <Text c="dimmed">No pending sanction requests in your approval queue.</Text>
                    </Table.Td>
                  </Table.Tr>
                ) : (
                  approvalsInbox.map((req) => (
                    <Table.Tr key={req.id}>
                      <Table.Td fw={700}>#{req.id}</Table.Td>
                      <Table.Td fw={600}>{req.applicant_name || `User #${req.applicant}`}</Table.Td>
                      <Table.Td><Badge>{req.leave_type_code}</Badge></Table.Td>
                      <Table.Td>{req.start_date} to {req.end_date}</Table.Td>
                      <Table.Td>
                        {req.substitute_name ? (
                          <Badge color="green" size="xs">{req.substitute_name} (Accepted)</Badge>
                        ) : (
                          <Text size="xs" c="dimmed">None required</Text>
                        )}
                      </Table.Td>
                      <Table.Td>{getStatusBadge(req.status)}</Table.Td>
                      <Table.Td style={{ textAlign: "right" }}>
                        <Button
                          size="xs"
                          color="blue"
                          onClick={() => {
                            setSelectedRequest(req);
                            setApprovalModalOpen(true);
                          }}
                        >
                          Review & Action
                        </Button>
                      </Table.Td>
                    </Table.Tr>
                  ))
                )}
              </Table.Tbody>
            </Table>
          </Paper>
        </Tabs.Panel>

        {/* Tab 5: Duty Resumptions */}
        <Tabs.Panel value="resumptions">
          <Paper withBorder radius="md">
            <Table striped highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Leave Req</Table.Th>
                  <Table.Th>Applicant</Table.Th>
                  <Table.Th>Resumption Date</Table.Th>
                  <Table.Th>Type</Table.Th>
                  <Table.Th>Actual Days Availed</Table.Th>
                  <Table.Th>Refunded Days</Table.Th>
                  <Table.Th>Status</Table.Th>
                  <Table.Th style={{ textAlign: "right" }}>Action</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {resumptionsList.length === 0 ? (
                  <Table.Tr>
                    <Table.Td colSpan={8} style={{ textAlign: "center" }} py="xl">
                      <Text c="dimmed">No duty resumptions recorded yet.</Text>
                    </Table.Td>
                  </Table.Tr>
                ) : (
                  resumptionsList.map((dr) => (
                    <Table.Tr key={dr.id}>
                      <Table.Td fw={700}>#{dr.leave_request}</Table.Td>
                      <Table.Td>{dr.applicant_name}</Table.Td>
                      <Table.Td fw={600}>{dr.resumption_date}</Table.Td>
                      <Table.Td>
                        <Badge color={dr.resumption_type === "early" ? "indigo" : dr.resumption_type === "normal" ? "green" : "orange"}>
                          {dr.resumption_type.toUpperCase()}
                        </Badge>
                      </Table.Td>
                      <Table.Td>{dr.actual_days_availed} days</Table.Td>
                      <Table.Td fw={700} c={Number(dr.refunded_days) > 0 ? "teal" : "dimmed"}>
                        {dr.refunded_days} days
                      </Table.Td>
                      <Table.Td>
                        <Badge color={dr.status === "approved" ? "green" : "yellow"}>
                          {dr.status}
                        </Badge>
                      </Table.Td>
                      <Table.Td style={{ textAlign: "right" }}>
                        {dr.status === "submitted" && (
                          <Button
                            size="xs"
                            color="green"
                            onClick={() => handleApproveResumption(dr.id)}
                          >
                            Approve Refund
                          </Button>
                        )}
                      </Table.Td>
                    </Table.Tr>
                  ))
                )}
              </Table.Tbody>
            </Table>
          </Paper>
        </Tabs.Panel>

        {/* Tab 6: Academic Holiday Calendar */}
        <Tabs.Panel value="holidays">
          <Paper withBorder radius="md">
            <Table striped highlightOnHover verticalSpacing="sm">
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Date</Table.Th>
                  <Table.Th>Holiday Name</Table.Th>
                  <Table.Th>Classification</Table.Th>
                  <Table.Th>Academic Year</Table.Th>
                  <Table.Th>Rule Impact</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {holidays.map((h) => (
                  <Table.Tr key={h.id}>
                    <Table.Td fw={700}>{h.date}</Table.Td>
                    <Table.Td fw={600}>{h.name}</Table.Td>
                    <Table.Td>
                      <Badge color={h.holiday_type === "gazetted" ? "blue" : "violet"}>
                        {h.holiday_type === "gazetted" ? "Gazetted Holiday" : "Restricted Holiday (RH)"}
                      </Badge>
                    </Table.Td>
                    <Table.Td>{h.academic_year}</Table.Td>
                    <Table.Td>
                      <Text size="xs">
                        {h.holiday_type === "gazetted"
                          ? "Exempt from Casual Leave debiting (BR-EL-011)"
                          : "Eligible for 1-day RH application (BR-EL-003)"}
                      </Text>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </Paper>
        </Tabs.Panel>
      </Tabs>

      {/* MODAL 1: Apply for Leave */}
      <Modal
        opened={applyModalOpen}
        onClose={() => setApplyModalOpen(false)}
        title={<Title order={3}>Apply for Institutional Leave</Title>}
        size="lg"
        radius="md"
      >
        <form onSubmit={handleApplySubmit}>
          <Stack gap="md">
            <Select
              label="Leave Category"
              required
              data={[
                { value: "CL", label: "Casual Leave (CL &le; 8 continuous days)" },
                { value: "RH", label: "Restricted Holiday (RH 1 day, calendar verified)" },
                { value: "SCL", label: "Special Casual Leave (SCL)" },
                { value: "EL", label: "Earned Leave (EL - continuous counting)" },
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
              label="Nominate Colleague as Substitute (Optional/Required for Teaching/Admin)"
              placeholder="Search faculty or staff colleague..."
              clearable
              data={substitutesList.map((s) => ({
                value: String(s.id),
                label: `${s.display_name} (${s.username} - ${s.discipline || s.kind})`,
              }))}
              value={applyForm.substitute}
              onChange={(val) => setApplyForm((prev) => ({ ...prev, substitute: val || "" }))}
            />

            <Textarea
              label="Purpose / Reason"
              required
              rows={3}
              placeholder="Detailed justification for leave..."
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
        title={<Title order={4}>Workflow History & Audit Trail (#{selectedRequest?.id})</Title>}
        size="md"
        radius="md"
      >
        {selectedRequest && (
          <Timeline active={(selectedRequest.action_logs?.length || 1) - 1} bulletSize={24} lineWidth={2}>
            {selectedRequest.action_logs && selectedRequest.action_logs.length > 0 ? (
              selectedRequest.action_logs.map((log) => (
                <Timeline.Item
                  key={log.id}
                  title={<Text fw={600} size="sm">{log.action.toUpperCase()}</Text>}
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
        title={<Title order={4}>Re-Nominate Substitute Colleague</Title>}
      >
        <Stack gap="md">
          <Text size="sm">
            The previous substitute declined your arrangement. Please select an alternative colleague to cover duties:
          </Text>
          <Select
            label="Replacement Substitute"
            placeholder="Choose colleague..."
            data={substitutesList.map((s) => ({
              value: String(s.id),
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
        title={<Title order={4}>Extend Approved Leave</Title>}
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
        title={<Title order={4}>Report Resumption of Duty</Title>}
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
        title={<Title order={4}>Sanction Authority Decision (#{selectedRequest?.id})</Title>}
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
