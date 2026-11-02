import React, { useState, useEffect } from "react";
import type { LeaveRequest, LeaveBalance } from "./types";

const LeaveDashboard: React.FC = () => {
  const [leaveBalances, setLeaveBalances] = useState<LeaveBalance[]>([]);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [substituteRequests, setSubstituteRequests] = useState<LeaveRequest[]>([]);
  const [showApplyForm, setShowApplyForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [applyFormValues, setApplyFormValues] = useState({
    leave_type: "CL",
    start_date: "",
    end_date: "",
    half_day: false,
    half_day_period: "forenoon",
    purpose: "",
    station_leave: false,
    station_leave_address: "",
    substitute_id: "",
  });

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [resBalances, resRequests] = await Promise.all([
        fetch("/api/v1/elm/balances/"),
        fetch("/api/v1/elm/requests/"),
      ]);
      if (resBalances.ok) setLeaveBalances(await resBalances.json());
      if (resRequests.ok) {
        const data: LeaveRequest[] = await resRequests.json();
        setLeaveRequests(data);
        setSubstituteRequests(data.filter((r) => r.substitute_status === "pending"));
      }
    } catch (err) {
      console.error("Failed to load leave data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleApplyFormChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;
    setApplyFormValues((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleApplyFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    try {
      const res = await fetch("/api/v1/elm/requests/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(applyFormValues),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to submit leave application");
      }
      setShowApplyForm(false);
      await fetchDashboardData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to submit application");
    }
  };

  const handleWithdrawLeaveRequest = async (requestId: number) => {
    try {
      await fetch(`/api/v1/elm/requests/${requestId}/withdraw/`, { method: "POST" });
      await fetchDashboardData();
    } catch (err) {
      console.error("Failed to withdraw:", err);
    }
  };

  const handleSubstituteResponse = async (requestId: number, decision: "accepted" | "declined") => {
    try {
      await fetch(`/api/v1/elm/requests/${requestId}/substitute-response/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision }),
      });
      await fetchDashboardData();
    } catch (err) {
      console.error("Failed to respond to substitute request:", err);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center border-b pb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Employee Leave Management (ELM)</h1>
          <p className="text-sm text-gray-500">Apply for leaves, track approvals, and manage substitute requests.</p>
        </div>
        <button
          onClick={() => setShowApplyForm(!showApplyForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
        >
          {showApplyForm ? "Cancel" : "+ Apply for Leave"}
        </button>
      </div>

      {loading && <div className="text-sm text-blue-600 font-semibold">Updating dashboard...</div>}

      {errorMsg && (
        <div className="p-4 bg-red-50 text-red-700 rounded border border-red-200">{errorMsg}</div>
      )}

      {/* Leave Balances Grid */}
      <div>
        <h2 className="text-lg font-semibold text-gray-700 mb-3">My Leave Quota & Balances</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {leaveBalances.length === 0 ? (
            <div className="text-sm text-gray-400 col-span-4">No balances recorded for the current year.</div>
          ) : (
            leaveBalances.map((bal) => (
              <div key={bal.id} className="p-4 bg-white border rounded shadow-sm text-center">
                <span className="text-xs uppercase text-gray-400 font-bold tracking-wider">
                  {typeof bal.leave_type === "object" ? bal.leave_type.name : bal.leave_type}
                </span>
                <div className="text-3xl font-extrabold text-blue-600 my-1">{bal.balance}</div>
                <div className="text-xs text-gray-500">Used: {bal.used_days} / Credited: {bal.credited_days}</div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Substitute Requests Pending My Action */}
      {substituteRequests.length > 0 && (
        <div className="p-5 bg-amber-50 border border-amber-200 rounded-lg">
          <h3 className="text-md font-bold text-amber-900 mb-2">Substitute Consent Requests</h3>
          <p className="text-xs text-amber-700 mb-3">Colleagues nominated you to handle responsibilities during their leave:</p>
          <div className="space-y-2">
            {substituteRequests.map((req) => (
              <div key={req.id} className="flex justify-between items-center bg-white p-3 rounded border">
                <div>
                  <span className="font-semibold text-gray-800">Leave Request #{req.id}</span>
                  <span className="text-xs text-gray-500 ml-2">({String(req.start_date)} to {String(req.end_date)})</span>
                  <div className="text-xs text-gray-600">{req.purpose}</div>
                </div>
                <div className="space-x-2">
                  <button
                    onClick={() => handleSubstituteResponse(req.id, "accepted")}
                    className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => handleSubstituteResponse(req.id, "declined")}
                    className="px-3 py-1 bg-red-600 text-white text-xs rounded hover:bg-red-700"
                  >
                    Decline
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Apply Form Modal/Panel */}
      {showApplyForm && (
        <div className="p-6 bg-gray-50 border rounded-lg shadow-sm">
          <h3 className="text-md font-bold text-gray-800 mb-4">New Leave Application</h3>
          <form onSubmit={handleApplyFormSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold mb-1">Leave Category</label>
                <select
                  name="leave_type"
                  value={applyFormValues.leave_type}
                  onChange={handleApplyFormChange}
                  className="w-full border p-2 rounded"
                >
                  <option value="CL">Casual Leave (CL)</option>
                  <option value="RH">Restricted Holiday (RH)</option>
                  <option value="SCL">Special Casual Leave (SCL)</option>
                  <option value="EL">Earned Leave (EL)</option>
                  <option value="VL">Vacation Leave (VL)</option>
                  <option value="COL">Commuted Leave (COL)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold mb-1">Start Date</label>
                <input
                  type="date"
                  name="start_date"
                  value={applyFormValues.start_date}
                  onChange={handleApplyFormChange}
                  required
                  className="w-full border p-2 rounded"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold mb-1">End Date</label>
                <input
                  type="date"
                  name="end_date"
                  value={applyFormValues.end_date}
                  onChange={handleApplyFormChange}
                  required
                  className="w-full border p-2 rounded"
                />
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <label className="flex items-center space-x-2 text-sm cursor-pointer">
                <input
                  type="checkbox"
                  name="half_day"
                  checked={applyFormValues.half_day}
                  onChange={handleApplyFormChange}
                />
                <span>Half-Day Leave</span>
              </label>
              {applyFormValues.half_day && (
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-semibold">Period:</span>
                  <select
                    name="half_day_period"
                    value={applyFormValues.half_day_period}
                    onChange={handleApplyFormChange}
                    className="border p-1 rounded text-sm"
                  >
                    <option value="forenoon">Forenoon (FN)</option>
                    <option value="afternoon">Afternoon (AN)</option>
                  </select>
                </div>
              )}
            </div>

            <div>
              <label className="block text-xs font-semibold mb-1">Purpose / Reason</label>
              <textarea
                name="purpose"
                value={applyFormValues.purpose}
                onChange={handleApplyFormChange}
                required
                rows={2}
                className="w-full border p-2 rounded"
                placeholder="Reason for requesting leave..."
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowApplyForm(false)}
                className="px-4 py-2 border rounded text-gray-600 hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-5 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Submit Application
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Applications Table */}
      <div>
        <h2 className="text-lg font-semibold text-gray-700 mb-3">My Leave History & Requests</h2>
        <div className="overflow-x-auto border rounded bg-white">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50 text-gray-500">
              <tr>
                <th className="px-4 py-3 text-left">ID</th>
                <th className="px-4 py-3 text-left">Type</th>
                <th className="px-4 py-3 text-left">Period</th>
                <th className="px-4 py-3 text-left">Purpose</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {leaveRequests.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-6 text-gray-400">
                    No leave requests found.
                  </td>
                </tr>
              ) : (
                leaveRequests.map((req) => (
                  <tr key={req.id}>
                    <td className="px-4 py-3 font-mono font-medium">#{req.id}</td>
                    <td className="px-4 py-3 font-semibold text-gray-700">{typeof req.leave_type === "object" ? req.leave_type.code : req.leave_type}</td>
                    <td className="px-4 py-3 text-gray-600">
                      {String(req.start_date)} {req.half_day ? `(${req.half_day_period})` : `to ${String(req.end_date)}`}
                    </td>
                    <td className="px-4 py-3 text-gray-600 max-w-xs truncate">{req.purpose}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs rounded font-semibold ${
                        req.status === "approved" ? "bg-green-100 text-green-700" :
                        req.status === "rejected" ? "bg-red-100 text-red-700" :
                        req.status === "withdrawn" ? "bg-gray-100 text-gray-600" :
                        "bg-yellow-100 text-yellow-800"
                      }`}>
                        {req.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {!["approved", "rejected", "withdrawn", "cancelled"].includes(req.status) && (
                        <button
                          onClick={() => handleWithdrawLeaveRequest(req.id)}
                          className="text-xs text-red-600 hover:underline"
                        >
                          Withdraw
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default LeaveDashboard;
