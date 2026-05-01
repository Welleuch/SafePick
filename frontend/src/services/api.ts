import { Robot, Gripper, ValidationResult, VisionSystem, Sensor, PLCController, Pneumatic, Feeder, SafetySystem, SafetyHousing } from '../types';

// Point to backend API.
// In development: http://localhost:8000
// In production: Set VITE_API_URL environment variable to your Cloudflare Worker URL
const API_BASE = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api/v1` 
  : 'http://localhost:8000/api/v1';

export async function getRobots(): Promise<Robot[]> {
  const res = await fetch(`${API_BASE}/robots`);
  return res.json();
}

export async function getGrippers(): Promise<Gripper[]> {
  const res = await fetch(`${API_BASE}/grippers`);
  return res.json();
}

export async function getVisionSystems(): Promise<VisionSystem[]> {
  const res = await fetch(`${API_BASE}/vision-systems`);
  return res.json();
}

export async function getSensors(): Promise<Sensor[]> {
  const res = await fetch(`${API_BASE}/sensors`);
  return res.json();
}

export async function getPLCControllers(): Promise<PLCController[]> {
  const res = await fetch(`${API_BASE}/plc-controllers`);
  return res.json();
}

export async function getPneumatics(): Promise<Pneumatic[]> {
  const res = await fetch(`${API_BASE}/pneumatics`);
  return res.json();
}

export async function getFeeders(): Promise<Feeder[]> {
  const res = await fetch(`${API_BASE}/feeders`);
  return res.json();
}

export async function getSafetySystems(): Promise<SafetySystem[]> {
  const res = await fetch(`${API_BASE}/safety-systems`);
  return res.json();
}

export async function getSafetyHousing(): Promise<SafetyHousing[]> {
  const res = await fetch(`${API_BASE}/safety-housing`);
  return res.json();
}

export async function validate(
  robotId: string,
  gripperId: string,
  workpieceMass: number,
  targetDistance: number,
  assumptionConfirmed: boolean = false
): Promise<ValidationResult> {
  const res = await fetch(`${API_BASE}/validate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      robot_id: robotId,
      gripper_id: gripperId,
      workpiece_mass_kg: workpieceMass,
      target_distance_m: targetDistance,
      assumption_confirmed: assumptionConfirmed,
    }),
  });
  return res.json();
}

export async function downloadReport(
  robotId: string,
  gripperId: string,
  workpieceMass: number,
  targetDistance: number,
  assumptionConfirmed: boolean,
  projectName: string = 'Projekt',
  visionId?: string,
  sensorId?: string,
  pneumaticId?: string,
  feederId?: string,
  safetySystemId?: string,
  operatingAngleDeg: number = 180,
  operatingDirection: string = 'front'
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/report`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      robot_id: robotId,
      gripper_id: gripperId,
      workpiece_mass_kg: workpieceMass,
      target_distance_m: targetDistance,
      assumption_confirmed: assumptionConfirmed,
      project_name: projectName,
      vision_id: visionId,
      sensor_id: sensorId,
      pneumatic_id: pneumaticId,
      feeder_id: feederId,
      safety_system_id: safetySystemId,
      operating_angle_deg: operatingAngleDeg,
      operating_direction: operatingDirection,
    }),
  });

  if (!res.ok) {
    throw new Error('Failed to generate report');
  }

  return res.blob();
}

export interface KnowledgeTip {
  id: number;
  target_type: string;
  target_id: string;
  severity: string;
  tip_text: string;
}

export interface LicenseBundle {
  total: number;
  used: number;
  purchased: string;
}

export async function getKnowledgeTips(): Promise<KnowledgeTip[]> {
  const res = await fetch(`${API_BASE}/knowledge-tips`);
  return res.json();
}

export async function addKnowledgeTip(
  targetType: string,
  targetId: string,
  severity: string,
  tipText: string
): Promise<KnowledgeTip> {
  const res = await fetch(`${API_BASE}/knowledge-tips`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      target_type: targetType,
      target_id: targetId,
      severity: severity,
      tip_text: tipText,
    }),
  });
  return res.json();
}

export async function deleteKnowledgeTip(tipId: number): Promise<void> {
  const res = await fetch(`${API_BASE}/knowledge-tips/${tipId}`, {
    method: 'DELETE',
  });
  return res.json();
}

export async function getLicense(): Promise<LicenseBundle> {
  const res = await fetch(`${API_BASE}/license`);
  return res.json();
}

export interface RobotRecommendation {
  requirements: {
    workpiece_mass_kg: number;
    pick_place_distance_m: number;
    picks_per_minute: number | null;
    max_cycle_time_s: number | null;
  };
  recommendations: Robot[];
  information: string;
}

export async function recommendRobots(
  workpieceMass: number,
  distanceM: number,
  picksPerMinute: number | null = null,
  maxCycleTime: number | null = null
): Promise<RobotRecommendation> {
  const res = await fetch(`${API_BASE}/recommend-robots`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      workpiece_mass_kg: workpieceMass,
      pick_place_distance_m: distanceM,
      picks_per_minute: picksPerMinute,
      max_cycle_time_s: maxCycleTime,
    }),
  });
  return res.json();
}
