export interface LeaveType {
  code: string;
  name: string;
  description: string;
  annual_quota: number;
  is_vacation: boolean;
  max_continuous_days: number;
}

export interface HolidayCalendar {
  id: number;
  date: string;
  name: string;
  holiday_type: 'gazetted' | 'restricted';
  academic_year: number;
  description?: string;
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

export interface DutyResumption {
  id: number;
  leave_request: number;
  resumption_date: string;
  resumption_type: 'normal' | 'early' | 'late';
  prefix_suffix_details?: string;
  actual_days_availed: number;
  refunded_days: number;
  status: 'submitted' | 'approved' | 'rejected';
  remarks?: string;
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
  duty_resumption?: DutyResumption;
  action_logs?: LeaveActionLog[];
  created_at?: string;
}

// Runtime object exports so Vite never encounters an empty ES module
export const LeaveCategories = {
  CL: "CL",
  RH: "RH",
  SCL: "SCL",
  EL: "EL",
  VL: "VL",
  COL: "COL",
} as const;
