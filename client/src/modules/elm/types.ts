export interface LeaveType {
  code: string;
  name: string;
  description: string;
  annual_quota: number;
  is_vacation: boolean;
  max_continuous_days: number;
}

export interface LeaveBalance {
  id: number;
  user: string;
  leave_type: LeaveType | string;
  year: number;
  credited_days: number;
  used_days: number;
  balance: number;
}

export interface LeaveActionLog {
  id: number;
  leave_request: number;
  actor: string;
  role_name: string;
  action: string;
  comments: string;
  created_at: string;
}

export interface LeaveRequest {
  id: number;
  applicant: string | number;
  leave_type: LeaveType | string;
  start_date: string;
  end_date: string;
  half_day: boolean;
  half_day_period?: string;
  purpose: string;
  station_leave: boolean;
  station_leave_address?: string;
  substitute?: string | number;
  substitute_status: string;
  status: string;
  action_logs?: LeaveActionLog[];
  created_at?: string;
}
