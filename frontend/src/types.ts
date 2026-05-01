export interface Robot {
  id: string;
  brand: string;
  model_name: string;
  robot_type?: string;
  max_payload_kg: number;
  max_inertia_kgm2: number;
  flange_iso_code: string;
  max_v_ms: number;
  max_a_ms2: number;
  io_max_current_a: number;
  protocols: string[];
  source?: string;
  price_eur?: number;
  delivery_weeks?: number;
}

export interface Gripper {
  id: string;
  manufacturer: string;
  model_name: string;
  mass_kg: number;
  inertia_cm: number;
  com_offset_z_mm: number;
  grip_offset_z_mm: number;
  mounting_pattern: string;
  peak_current_a: number;
  protocols: string[];
  source?: string;
  price_eur?: number;
  delivery_weeks?: number;
}

export interface VisionSystem {
  id: string;
  brand: string;
  model_name: string;
  resolution_mpx: number;
  frame_rate_fps: number;
  processing_latency_ms: number;
  protocols: string[];
  field_of_view_deg: number;
  min_part_size_mm: number;
  lighting_type: string;
  source?: string;
  price_eur?: number;
  delivery_weeks?: number;
}

export interface Sensor {
  id: string;
  brand: string;
  model_name: string;
  sensor_type: string;
  detection_range_mm: number;
  response_time_ms: number;
  io_type: string;
  output_type: string;
  source?: string;
  price_eur?: number;
  delivery_weeks?: number;
}

export interface PLCController {
  id: string;
  brand: string;
  model_name: string;
  digital_inputs: number;
  digital_outputs: number;
  protocols: string[];
  io_link_master_ports: number;
  source?: string;
  price_eur?: number;
  delivery_weeks?: number;
}

export interface Pneumatic {
  id: string;
  brand: string;
  model_name: string;
  component_type: string;
  switching_time_ms: number;
  flow_rate_lpm: number;
  vacuum_compatible: boolean;
  thread_size: string;
  voltage_v: string;
  source?: string;
  price_eur?: number;
  delivery_weeks?: number;
}

export interface Feeder {
  id: string;
  brand: string;
  model_name: string;
  feeder_type: string;
  max_part_size_mm: number;
  max_feed_rate_ppm: number;
  pick_height_mm: number;
  vibration_controllable: boolean;
  voltage: string;
  protocols: string[];
  source?: string;
  price_eur?: number;
  delivery_weeks?: number;
}

export interface SafetySystem {
  id: string;
  brand: string;
  model_name: string;
  safety_type: string;
  protected_height_mm: number;
  response_time_ms: number;
  safety_rating: string;
  protocols: string[];
  source?: string;
  price_eur?: number;
  delivery_weeks?: number;
}

export interface SafetyHousing {
  id: string;
  brand: string;
  model_name: string;
  material: string;
  min_enclosure_m3: number;
  profile_type: string;
  glass_type: string;
  price_eur_per_m2: number;
  source?: string;
}

export interface ValidationResult {
  valid: boolean;
  inertia: {
    calculated_inertia: number;
    utilization_percent: number;
    status: string;
    status_de: string;
    message: string;
  };
  cycle_time: {
    estimated_seconds: number;
    assumptions: string[];
    status: string;
  };
  interface: {
    mechanical: { status: string; details: string };
    electrical: { status: string; details: string };
    digital: { status: string; details: string };
    overall_compatible: boolean;
  };
  assumption_confirmed?: boolean;
  warning?: string;
}