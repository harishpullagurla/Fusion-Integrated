export interface LeaveType {
  code: string;
  name: string;
  description: string;
  annual_quota: string | number;
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
  leave_type: string;
  leave_type_code: string;
  leave_type_name: string;
  year: number;
  credited_days: string | number;
  used_days: string | number;
  balance: string | number;
}

export interface LeaveActionLog {
  id: number;
  leave_request: number;
  actor: string;
  actor_name?: string;
  role_name: string;
  action: string;
  comments: string;
  created_at: string;
}

export interface DutyResumption {
  id: number;
  leave_request: number;
  applicant_name?: string;
  leave_type_code?: string;
  resumption_date: string;
  resumption_type: 'normal' | 'early' | 'late';
  prefix_suffix_details?: string;
  actual_days_availed: string | number;
  refunded_days: string | number;
  status: 'submitted' | 'approved' | 'rejected';
  remarks?: string;
}

export interface LeaveRequest {
  id: number;
  applicant: string | number;
  applicant_name?: string;
  leave_type: string;
  leave_type_code?: string;
  leave_type_name?: string;
  start_date: string;
  end_date: string;
  half_day: boolean;
  half_day_period?: string;
  purpose: string;
  station_leave: boolean;
  station_leave_address?: string;
  substitute?: string | number;
  substitute_name?: string;
  substitute_status: 'pending' | 'accepted' | 'declined';
  status: 'draft' | 'awaiting_substitute' | 'substitute_declined' | 'pending_unit_head' | 'pending_higher_sanction' | 'approved' | 'rejected' | 'withdrawn' | 'cancelled' | 'completed';
  duty_resumption?: DutyResumption;
  action_logs?: LeaveActionLog[];
  created_at?: string;
}

export interface SubstituteOption {
  user_id: number;
  username: string;
  display_name: string;
  kind: string;
  discipline?: string;
}

export const LeaveCategories = {
  CL: "CL",
  RH: "RH",
  SCL: "SCL",
  EL: "EL",
  VL: "VL",
  COL: "COL",
} as const;
