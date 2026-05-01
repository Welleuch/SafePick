from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel

from app.physics import ValidationEngine

app = FastAPI(title="PESE API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

validation_engine = ValidationEngine()

ROBOT_DB = [
    {"id": "kuka-kr-3-delta", "brand": "KUKA", "model_name": "KR 3 Delta", "robot_type": "Delta",
     "max_payload_kg": 3.0, "max_inertia_kgm2": 0.05, "flange_iso_code": "ISO 9409-1-31.5-4-M5",
     "max_v_ms": 10.0, "max_a_ms2": 50.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "EtherCAT"],
     "max_reach_mm": 600, "source": "KUKA product specifications (rated 3kg, up to 6kg design)",
     "price_eur": 45000, "delivery_weeks": 8},
    {"id": "fanuc-m-1ia", "brand": "Fanuc", "model_name": "M-1iA/1H", "robot_type": "Delta",
     "max_payload_kg": 1.0, "max_inertia_kgm2": 0.02, "flange_iso_code": "ISO 9409-1-31.5-4-M5",
     "max_v_ms": 8.0, "max_a_ms2": 40.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 400, "source": "Fanuc product specifications (1kg payload, standard delta)",
     "price_eur": 38000, "delivery_weeks": 6},
    {"id": "abb-irb-360", "brand": "ABB", "model_name": "IRB 360-3/1130", "robot_type": "Delta",
     "max_payload_kg": 3.0, "max_inertia_kgm2": 0.055, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 10.0, "max_a_ms2": 50.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "DeviceNet"],
     "max_reach_mm": 1130, "source": "ABB datasheet 3HAC029963 (0.055 kgm² max inertia for 3kg variant)",
     "price_eur": 52000, "delivery_weeks": 10},

    {"id": "epson-gx11b", "brand": "Epson", "model_name": "GX11-B650", "robot_type": "SCARA",
     "max_payload_kg": 11.0, "max_inertia_kgm2": 0.12, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 4.5, "max_a_ms2": 15.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 650, "source": "Epson GX-Series datasheet (11kg max payload, 650mm reach)",
     "price_eur": 32000, "delivery_weeks": 6},
    {"id": "yamaha-yk500xg", "brand": "Yamaha", "model_name": "YK500XG", "robot_type": "SCARA",
     "max_payload_kg": 10.0, "max_inertia_kgm2": 0.10, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 5.0, "max_a_ms2": 15.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "EtherCAT"],
     "max_reach_mm": 500, "source": "Yamaha YK-XG series spec (10kg payload, 500mm reach)",
     "price_eur": 28000, "delivery_weeks": 5},
    {"id": "denso-hm-60", "brand": "Denso", "model_name": "HM-60", "robot_type": "SCARA",
     "max_payload_kg": 10.0, "max_inertia_kgm2": 0.10, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 5.5, "max_a_ms2": 15.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 600, "source": "Denso HM-Series datasheet (10kg payload, 600mm reach)",
     "price_eur": 35000, "delivery_weeks": 8},

    {"id": "kuka-kr-10", "brand": "KUKA", "model_name": "KR 10 R1610", "robot_type": "6-Axis",
     "max_payload_kg": 10.0, "max_inertia_kgm2": 0.20, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 3.0, "max_a_ms2": 10.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 1610, "source": "KUKA KR 10 Sixx spec (10kg payload, 1611mm reach)",
     "price_eur": 55000, "delivery_weeks": 10},
    {"id": "abb-irb-2600", "brand": "ABB", "model_name": "IRB 2600-12/1.65", "robot_type": "6-Axis",
     "max_payload_kg": 12.0, "max_inertia_kgm2": 0.25, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 3.0, "max_a_ms2": 10.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "DeviceNet"],
     "max_reach_mm": 1650, "source": "ABB IRB 2600 spec (12kg payload, 1650mm reach)",
     "price_eur": 62000, "delivery_weeks": 12},
    {"id": "fanuc-m-20ia", "brand": "Fanuc", "model_name": "M-20iA/10L", "robot_type": "6-Axis",
     "max_payload_kg": 10.0, "max_inertia_kgm2": 0.20, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 3.0, "max_a_ms2": 10.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 2009, "source": "Fanuc M-20iA spec (10kg payload, 2009mm reach)",
     "price_eur": 58000, "delivery_weeks": 10},
]

GRIPPER_DB = [
    {"id": "schunk-pgn-plus-p-100", "manufacturer": "Schunk", "model_name": "PGN-plus-P 100",
     "mass_kg": 0.45, "inertia_cm": 0.0001, "com_offset_z_mm": 50, "grip_offset_z_mm": 80,
     "mounting_pattern": "ISO 9409-1-31.5-4-M5", "peak_current_a": 1.5, "protocols": ["Profinet", "EtherCAT"],
     "source": "Schunk catalog (standard parallel gripper, estimated values)",
     "price_eur": 2500, "delivery_weeks": 4},
    {"id": "zimmer-gp400", "manufacturer": "Zimmer", "model_name": "GP400",
     "mass_kg": 0.38, "inertia_cm": 0.00008, "com_offset_z_mm": 45, "grip_offset_z_mm": 70,
     "mounting_pattern": "ISO 9409-1-31.5-4-M5", "peak_current_a": 1.2, "protocols": ["Profinet", "EtherCAT"],
     "source": "Zimmer catalog (estimated values)",
     "price_eur": 2200, "delivery_weeks": 3},
{"id": "festo-hew-16", "manufacturer": "Festo", "model_name": "HEW-16",
      "mass_kg": 0.25, "inertia_cm": 0.00005, "com_offset_z_mm": 40, "grip_offset_z_mm": 60,
      "mounting_pattern": "ISO 9409-1-31.5-4-M5", "peak_current_a": 1.0, "protocols": ["Profinet", "IO-Link"],
      "source": "Festo catalog (estimated values)",
      "price_eur": 1800, "delivery_weeks": 2},
 ]

VISION_SYSTEMS_DB = [
    {"id": "keyence-cv-x200", "brand": "Keyence", "model_name": "CV-X200", "resolution_mpx": 2.0,
     "frame_rate_fps": 120, "processing_latency_ms": 15, "protocols": ["Profinet", "EtherNet/IP"],
     "field_of_view_deg": 45, "min_part_size_mm": 2.0, "lighting_type": "LED",
     "source": "Keyence catalog (estimated)", "price_eur": 8500, "delivery_weeks": 4},
    {"id": "cognex-insight-7200", "brand": "Cognex", "model_name": "In-Sight 7200", "resolution_mpx": 2.0,
     "frame_rate_fps": 100, "processing_latency_ms": 20, "protocols": ["EtherNet/IP", "Profinet"],
     "field_of_view_deg": 40, "min_part_size_mm": 3.0, "lighting_type": "LED",
     "source": "Cognex catalog (estimated)", "price_eur": 7800, "delivery_weeks": 4},
    {"id": "basler-ace-2300", "brand": "Basler", "model_name": "ace 2300", "resolution_mpx": 2.3,
     "frame_rate_fps": 80, "processing_latency_ms": 25, "protocols": ["GigE", "USB3"],
     "field_of_view_deg": 35, "min_part_size_mm": 5.0, "lighting_type": "IR",
     "source": "Basler catalog (estimated)", "price_eur": 5200, "delivery_weeks": 3},
]

SENSORS_DB = [
    {"id": "sick-ild-170", "brand": "SICK", "model_name": "ILD 170-100", "sensor_type": "Laser Distance",
     "detection_range_mm": 100, "response_time_ms": 0.5, "io_type": "PNP", "output_type": "NO",
     "source": "SICK catalog (estimated)", "price_eur": 450, "delivery_weeks": 2},
    {"id": "keyence-il-300", "brand": "Keyence", "model_name": "IL-300BG", "sensor_type": " photoelectric",
     "detection_range_mm": 300, "response_time_ms": 0.1, "io_type": "PNP", "output_type": "NO",
     "source": "Keyence catalog (estimated)", "price_eur": 320, "delivery_weeks": 2},
    {"id": "omron-e3x", "brand": "Omron", "model_name": "E3X-DA41", "sensor_type": "Fiber",
     "detection_range_mm": 150, "response_time_ms": 0.3, "io_type": "NPN", "output_type": "NO",
     "source": "Omron catalog (estimated)", "price_eur": 180, "delivery_weeks": 2},
]

PLC_CONTROLLERS_DB = [
    {"id": "siemens-s7-1500", "brand": "Siemens", "model_name": "CPU 1516-3 PN/DP", "digital_inputs": 32,
     "digital_outputs": 32, "protocols": ["Profinet", "Profibus"], "io_link_master_ports": 16,
     "source": "Siemens catalog", "price_eur": 8500, "delivery_weeks": 6},
    {"id": "beckhoff-cx5020", "brand": "Beckhoff", "model_name": "CX5020-0120-0100", "digital_inputs": 16,
     "digital_outputs": 16, "protocols": ["EtherCAT", "Profinet"], "io_link_master_ports": 8,
     "source": "Beckhoff catalog", "price_eur": 6200, "delivery_weeks": 4},
    {"id": "siemens-s7-1200", "brand": "Siemens", "model_name": "CPU 1214C", "digital_inputs": 14,
     "digital_outputs": 10, "protocols": ["Profinet"], "io_link_master_ports": 4,
     "source": "Siemens catalog", "price_eur": 2800, "delivery_weeks": 4},
]

PNEUMATICS_DB = [
    {"id": "festo-vuvg-10", "brand": "Festo", "model_name": "VUVG-L10-K18-Q", "component_type": "Valve",
     "switching_time_ms": 5, "flow_rate_lpm": 500, "vacuum_compatible": True, "thread_size": "M5",
     "voltage_v": "24VDC", "source": "Festo catalog", "price_eur": 180, "delivery_weeks": 2},
    {"id": "smc-vq7-10", "brand": "SMC", "model_name": "VQ7-10", "component_type": "Valve",
     "switching_time_ms": 7, "flow_rate_lpm": 400, "vacuum_compatible": True, "thread_size": "M5",
     "voltage_v": "24VDC", "source": "SMC catalog", "price_eur": 150, "delivery_weeks": 2},
    {"id": "festo-vrpa", "brand": "Festo", "model_name": "VRPA-D20-F", "component_type": "Venturi",
     "switching_time_ms": 3, "flow_rate_lpm": 100, "vacuum_compatible": True, "thread_size": "G1/8",
     "voltage_v": "24VDC", "source": "Festo catalog", "price_eur": 420, "delivery_weeks": 2},
]

FEEDERS_DB = [
    {"id": "rna-zs-200", "brand": "RNA", "model_name": "ZS 200RC", "feeder_type": "Bowl",
     "max_part_size_mm": 80, "max_feed_rate_ppm": 120, "pick_height_mm": 200,
     "vibration_controllable": True, "voltage": "230VAC", "protocols": ["Profinet"],
     "source": "RNA catalog", "price_eur": 12000, "delivery_weeks": 8},
    {"id": "afag-smt-150", "brand": "Afag", "model_name": "SMT 150", "feeder_type": "Inline",
     "max_part_size_mm": 50, "max_feed_rate_ppm": 200, "pick_height_mm": 150,
     "vibration_controllable": True, "voltage": "24VDC", "protocols": ["Profinet"],
     "source": "Afag catalog", "price_eur": 8500, "delivery_weeks": 6},
]

SAFETY_SYSTEMS_DB = [
    {"id": "sick-s3000", "brand": "SICK", "model_name": "S3000", "safety_type": "Laser Scanner",
     "protected_height_mm": 190, "response_time_ms": 8, "safety_rating": "PLd",
     "protocols": ["Profinet", "Flexi"],
     "source": "SICK catalog", "price_eur": 4200, "delivery_weeks": 4},
    {"id": "keyence-sl-v", "brand": "Keyence", "model_name": "SL-V series", "safety_type": "Light Curtain",
     "protected_height_mm": 300, "response_time_ms": 12, "safety_rating": "PLe",
     "protocols": ["NPN"],
     "source": "Keyence catalog", "price_eur": 3800, "delivery_weeks": 4},
]

SAFETY_HOUSING_DB = [
    {"id": "item-d-30", "brand": "Item", "model_name": "D30", "material": "Aluminum",
     "min_enclosure_m3": 0.5, "profile_type": "D30",
     "glass_type": "Polycarbonate", "price_eur_per_m2": 280,
     "source": "Item catalog",},
    {"id": "bosch-rexroth-fs", "brand": "Bosch Rexroth", "model_name": "FlowShop", "material": "Aluminum",
     "min_enclosure_m3": 0.8, "profile_type": "FS",
     "glass_type": "Laminated", "price_eur_per_m2": 320,
     "source": "Bosch catalog",},
]

class RequirementsRequest(BaseModel):
    workpiece_mass_kg: float
    pick_place_distance_m: float
    picks_per_minute: Optional[float] = None
    max_cycle_time_s: Optional[float] = None


def filter_robots_by_requirements(workpiece_mass: float, distance_m: float, picks_per_minute: Optional[float] = None, max_cycle_time: Optional[float] = None) -> List[dict]:
    valid_robots = []
    for robot in ROBOT_DB:
        gripper_mass_est = 0.3
        total_mass = workpiece_mass + gripper_mass_est
        if total_mass > robot["max_payload_kg"]:
            continue
        required_cycle = max_cycle_time
        if picks_per_minute and picks_per_minute > 0:
            required_cycle = 60.0 / picks_per_minute
        if required_cycle:
            t_accel = robot["max_v_ms"] / robot["max_a_ms2"]
            est_time = (2 * t_accel) + (distance_m / robot["max_v_ms"])
            est_time = est_time * 1.15
            if est_time > required_cycle * 1.2:
                continue
        gripper_inertia = 0.0001
        total_inertia = gripper_inertia + (workpiece_mass * 0.002 * distance_m)
        if total_inertia > robot["max_inertia_kgm2"] * 0.9:
            continue
        valid_robots.append(robot)
    valid_robots.sort(key=lambda r: (r["price_eur"], r["delivery_weeks"]))
    return valid_robots[:3]


@app.get("/api/v1/robots")
def get_robots() -> List[dict]:
    return ROBOT_DB


@app.post("/api/v1/recommend-robots")
def recommend_robots(request: RequirementsRequest):
    recommended = filter_robots_by_requirements(
        request.workpiece_mass_kg,
        request.pick_place_distance_m,
        request.picks_per_minute,
        request.max_cycle_time_s
    )
    return {
        "requirements": {
            "workpiece_mass_kg": request.workpiece_mass_kg,
            "pick_place_distance_m": request.pick_place_distance_m,
            "picks_per_minute": request.picks_per_minute,
            "max_cycle_time_s": request.max_cycle_time_s,
        },
        "recommendations": recommended,
        "information": "Keine Empfehlungen verfuegbar" if not recommended else None
    }


@app.get("/api/v1/grippers")
def get_grippers() -> List[dict]:
    return GRIPPER_DB


class ValidationRequest(BaseModel):
    robot_id: str
    gripper_id: str
    workpiece_mass_kg: float
    target_distance_m: float


@app.post("/api/v1/validate")
def validate(request: ValidationRequest):
    robot = next((r for r in ROBOT_DB if r["id"] == request.robot_id), None)
    gripper = next((g for g in GRIPPER_DB if g["id"] == request.gripper_id), None)
    
    if not robot:
        raise HTTPException(status_code=404, detail=f"Robot {request.robot_id} not found")
    if not gripper:
        raise HTTPException(status_code=404, detail=f"Gripper {request.gripper_id} not found")
    
    result = validation_engine.run_full_validation(
        robot, gripper, request.workpiece_mass_kg, request.target_distance_m
    )
    return {"status": "GRÜN" if result["valid"] else "KRITISCH", **result}


@app.get("/api/v1/vision-systems")
def get_vision_systems() -> List[dict]:
    return VISION_SYSTEMS_DB


@app.get("/api/v1/sensors")
def get_sensors() -> List[dict]:
    return SENSORS_DB


@app.get("/api/v1/plc-controllers")
def get_plc_controllers() -> List[dict]:
    return PLC_CONTROLLERS_DB


class SystemSuggestionRequest(BaseModel):
    workpiece_mass_kg: float
    pick_place_distance_m: float
    picks_per_minute: Optional[float] = None
    operating_angle_deg: int = 180
    operating_direction: str = "front"


@app.post("/api/v1/suggest-systems")
def suggest_systems(request: SystemSuggestionRequest):
    """Auto-suggest TOP 3 compatible 9-part system combinations."""
    suggestions = []
    
    valid_robots = []
    gripper_mass_est = 0.3
    total_mass = request.workpiece_mass_kg + gripper_mass_est
    
    for robot in ROBOT_DB:
        if total_mass > robot["max_payload_kg"]:
            continue
        
        if request.picks_per_minute and request.picks_per_minute > 0:
            required_cycle = 60.0 / request.picks_per_minute
            t_accel = robot["max_v_ms"] / robot["max_a_ms2"]
            est_time = (2 * t_accel) + (request.pick_place_distance_m / robot["max_v_ms"])
            est_time = est_time * 1.15
            if est_time > required_cycle * 1.2:
                continue
        
        gripper_inertia = 0.0001
        total_inertia = gripper_inertia + (request.workpiece_mass_kg * 0.002 * request.pick_place_distance_m)
        if total_inertia > robot["max_inertia_kgm2"] * 0.9:
            continue
            
        valid_robots.append(robot)
    
    # For each valid robot, find compatible grippers and PLCs
    for robot in valid_robots:
        robot_flange = robot.get("flange_iso_code", "")
        robot_protocols = set(robot.get("protocols", []))
        
        for gripper in GRIPPER_DB:
            if gripper.get("mounting_pattern", "") != robot_flange:
                continue
            if gripper.get("peak_current_a", 0) > robot.get("io_max_current_a", 0):
                continue
            
            gripper_protocols = set(gripper.get("protocols", []))
            
            for plc in PLC_CONTROLLERS_DB:
                plc_protocols = set(plc.get("protocols", []))
                common_protocols = robot_protocols & plc_protocols
                
                if not common_protocols:
                    continue
                
                compatible_vision = next((v for v in VISION_SYSTEMS_DB if set(v.get("protocols", [])) & plc_protocols), None)
                compatible_sensor = next((s for s in SENSORS_DB if s.get("io_type")), None)
                compatible_pneumatic = next((p for p in PNEUMATICS_DB if p.get("voltage_v") == "24VDC"), None)
                compatible_feeder = next((f for f in FEEDERS_DB if set(f.get("protocols", [])) & plc_protocols), None)
                compatible_safety = next((s for s in SAFETY_SYSTEMS_DB if set(s.get("protocols", [])) & plc_protocols), None)
                
                housing_size = calc_housing_size(robot.get("max_reach_mm", 500) / 1000, request.operating_angle_deg, request.operating_direction)
                
                total_price = (
                    robot.get("price_eur", 0) + 
                    gripper.get("price_eur", 0) + 
                    plc.get("price_eur", 0) +
                    (compatible_vision.get("price_eur", 0) if compatible_vision else 0) +
                    (compatible_sensor.get("price_eur", 0) if compatible_sensor else 0) +
                    (compatible_pneumatic.get("price_eur", 0) if compatible_pneumatic else 0) +
                    (compatible_feeder.get("price_eur", 0) if compatible_feeder else 0) +
                    (compatible_safety.get("price_eur", 0) if compatible_safety else 0) +
                    housing_size["price_eur"]
                )
                
                suggestions.append({
                    "robot": robot,
                    "gripper": gripper,
                    "plc": plc,
                    "vision": compatible_vision,
                    "sensor": compatible_sensor,
                    "pneumatic": compatible_pneumatic,
                    "feeder": compatible_feeder,
                    "safety_system": compatible_safety,
                    "safety_housing": housing_size,
                    "operating_angle_deg": request.operating_angle_deg,
                    "operating_direction": request.operating_direction,
                    "total_price": total_price,
                    "delivery_weeks": max(
                        robot.get("delivery_weeks", 8),
                        gripper.get("delivery_weeks", 4),
                        plc.get("delivery_weeks", 4),
                        compatible_vision.get("delivery_weeks", 4) if compatible_vision else 4,
                        compatible_feeder.get("delivery_weeks", 4) if compatible_feeder else 4,
                        compatible_safety.get("delivery_weeks", 4) if compatible_safety else 4,
                    ),
                    "compatibility": {
                        "robot_gripper": "PASS",
                        "robot_plc": "PASS",
                        "plc_vision": "PASS" if compatible_vision else "FAIL",
                        "plc_feeder": "PASS" if compatible_feeder else "FAIL",
                        "plc_safety": "PASS" if compatible_safety else "FAIL",
                        "protocols_used": list(common_protocols)
                    }
                })
    
    suggestions.sort(key=lambda s: (s["total_price"], s["delivery_weeks"]))
    return {"suggestions": suggestions[:3]}


def calc_housing_size(robot_reach_m: float, angle_deg: int, direction: str) -> dict:
    """Calculate housing dimensions based on operating area."""
    clearance = 0.5
    
    if angle_deg == 180 and direction == "front":
        width = robot_reach_m + clearance
        depth = robot_reach_m + clearance
        height = 2.0
    elif angle_deg == 360:
        width = (robot_reach_m + clearance) * 2
        depth = (robot_reach_m + clearance) * 2
        height = 2.0
    elif angle_deg == 90:
        width = robot_reach_m + clearance
        depth = robot_reach_m + clearance * 0.3
        height = 2.0
    else:
        width = robot_reach_m + clearance
        depth = robot_reach_m + clearance
        height = 2.0
    
    area_m2 = width * depth
    volume_m3 = width * depth * height
    price_eur = int(area_m2 * 280)
    
    return {
        "brand": "Item",
        "model_name": "D30 Custom",
        "width_m": round(width, 2),
        "depth_m": round(depth, 2),
        "height_m": height,
        "area_m2": round(area_m2, 2),
        "volume_m3": round(volume_m3, 2),
        "price_eur": price_eur,
        "material": "Aluminum",
    }


@app.get("/api/v1/pneumatics")
def get_pneumatics() -> List[dict]:
    return PNEUMATICS_DB


@app.get("/api/v1/feeders")
def get_feeders() -> List[dict]:
    return FEEDERS_DB


@app.get("/api/v1/safety-systems")
def get_safety_systems() -> List[dict]:
    return SAFETY_SYSTEMS_DB


@app.get("/api/v1/safety-housing")
def get_safety_housing() -> List[dict]:
    return SAFETY_HOUSING_DB


@app.get("/api/v1/components")
def get_all_components():
    return {
        "robots": ROBOT_DB,
        "grippers": GRIPPER_DB,
        "vision_systems": VISION_SYSTEMS_DB,
        "sensors": SENSORS_DB,
        "plc_controllers": PLC_CONTROLLERS_DB,
        "pneumatics": PNEUMATICS_DB,
        "feeders": FEEDERS_DB,
        "safety_systems": SAFETY_SYSTEMS_DB,
        "safety_housing": SAFETY_HOUSING_DB,
    }


class ReportRequest(BaseModel):
    robot_id: str
    gripper_id: str
    workpiece_mass_kg: float
    target_distance_m: float
    assumption_confirmed: bool
    project_name: str = "Projekt"
    vision_id: Optional[str] = None
    sensor_id: Optional[str] = None
    pneumatic_id: Optional[str] = None
    feeder_id: Optional[str] = None
    safety_system_id: Optional[str] = None
    operating_angle_deg: int = 180
    operating_direction: str = "front"


@app.post("/api/v1/report")
def generate_report(request: ReportRequest):
    """Generate comprehensive Technical Audit Report - compact version."""
    try:
        from fastapi.responses import Response
        from fpdf import FPDF
        from datetime import datetime
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
    
    try:
        robot = next((r for r in ROBOT_DB if r["id"] == request.robot_id), None)
        gripper = next((g for g in GRIPPER_DB if g["id"] == request.gripper_id), None)
        
        if not robot or not gripper:
            raise HTTPException(status_code=404, detail=f"Robot {request.robot_id} or Gripper {request.gripper_id} not found")
        
        vision = next((v for v in VISION_SYSTEMS_DB if v["id"] == request.vision_id), None) if request.vision_id else None
        sensor = next((s for s in SENSORS_DB if s["id"] == request.sensor_id), None) if request.sensor_id else None
        pneumatic = next((p for p in PNEUMATICS_DB if p["id"] == request.pneumatic_id), None) if request.pneumatic_id else None
        feeder = next((f for f in FEEDERS_DB if f["id"] == request.feeder_id), None) if request.feeder_id else None
        safety = next((s for s in SAFETY_SYSTEMS_DB if s["id"] == request.safety_system_id), None) if request.safety_system_id else None
        
        plc_protocols = robot.get("protocols", [])
        plc = next((p for p in PLC_CONTROLLERS_DB if set(p.get("protocols", [])) & set(plc_protocols)), PLC_CONTROLLERS_DB[0])
        
        robot_reach_m = robot.get("max_reach_mm", 500) / 1000.0
        housing = calc_housing_size(robot_reach_m, request.operating_angle_deg, request.operating_direction)
        
        # ===== PHYSICS CALCULATIONS =====
        gripper_inertia_at_flange = gripper.get("inertia_cm", 0.0001) + gripper.get("mass_kg", 0.3) * (gripper.get("com_offset_z_mm", 50) / 1000) ** 2
        workpiece_inertia_at_flange = request.workpiece_mass_kg * (gripper.get("grip_offset_z_mm", 70) / 1000) ** 2
        total_inertia = gripper_inertia_at_flange + workpiece_inertia_at_flange
        inertia_utilization = (total_inertia / robot.get("max_inertia_kgm2", 0.05)) * 100
        inertia_status = "GRÜN" if inertia_utilization <= 90 else "KRITISCH"
        
        max_v = robot.get("max_v_ms", 10.0)
        max_a = robot.get("max_a_ms2", 50.0)
        t_accel = max_v / max_a
        dist_accel = 0.5 * max_a * t_accel ** 2
        if 2 * dist_accel <= request.target_distance_m:
            t_const = (request.target_distance_m - 2 * dist_accel) / max_v
            cycle_base = (2 * t_accel) + t_const
        else:
            cycle_base = 2 * (request.target_distance_m / max_a) ** 0.5
            t_const = 0
        
        pneumatic_latency = (pneumatic.get("switching_time_ms", 5) / 1000) if pneumatic else 0.05
        vision_latency = (vision.get("processing_latency_ms", 20) / 1000) if vision else 0.02
        sensor_latency = (sensor.get("response_time_ms", 0.5) / 1000) if sensor else 0.0005
        total_latency = pneumatic_latency + vision_latency + sensor_latency
        cycle_time = (cycle_base + total_latency) * 1.15
        picks_per_minute = 60 / cycle_time if cycle_time > 0 else 0
        cycle_status = "GRÜN" if picks_per_minute >= 30 else "KRITISCH"
        
        total_payload = request.workpiece_mass_kg + gripper.get("mass_kg", 0.3)
        payload_utilization = (total_payload / robot.get("max_payload_kg", 3.0)) * 100
        payload_status = "GRÜN" if payload_utilization <= 90 else "KRITISCH"
        
        flange_match = robot.get("flange_iso_code") == gripper.get("mounting_pattern")
        current_match = robot.get("io_max_current_a", 2.0) >= gripper.get("peak_current_a", 1.5)
        protocol_match = len(set(plc_protocols) & set(gripper.get("protocols", []))) > 0
        interface_status = "GRÜN" if (flange_match and current_match and protocol_match) else "KRITISCH"
        
        overall_status = "GRÜN" if inertia_status == "GRÜN" and cycle_status == "GRÜN" and payload_status == "GRÜN" and interface_status == "GRÜN" else "KRITISCH"
        
        total_price = (
            robot.get("price_eur", 0) + gripper.get("price_eur", 0) + plc.get("price_eur", 0) +
            (vision.get("price_eur", 0) if vision else 0) +
            (sensor.get("price_eur", 0) if sensor else 0) +
            (pneumatic.get("price_eur", 0) if pneumatic else 0) +
            (feeder.get("price_eur", 0) if feeder else 0) +
            (safety.get("price_eur", 0) if safety else 0) +
            housing.get("price_eur", 0)
        )
        delivery_weeks = max(
            robot.get("delivery_weeks", 8), gripper.get("delivery_weeks", 4), plc.get("delivery_weeks", 4),
            (vision.get("delivery_weeks", 4) if vision else 4), (feeder.get("delivery_weeks", 4) if feeder else 4),
            (safety.get("delivery_weeks", 4) if safety else 4)
        )
        
        # ===== COMPACT PDF =====
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=10)
        page_width = pdf.w - 20  # page width minus margins (10 on each side)
        
        # === COVER + SUMMARY ===
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 15, "TECHNISCHES AUDIT - " + request.project_name, ln=True, align="C")
        pdf.ln(3)
        
        # Status boxes
        if overall_status == "GRÜN":
            pdf.set_text_color(34, 197, 94)
            pdf.set_font("Helvetica", "B", 28)
            pdf.cell(0, 18, "GRUEN", ln=True, align="C")
        else:
            pdf.set_text_color(239, 68, 68)
            pdf.set_font("Helvetica", "B", 28)
            pdf.cell(0, 18, "KRITISCH", ln=True, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M')}  |  Version: 1.0", ln=True)
        pdf.cell(0, 6, f"Gesamtsystempreis: EUR {total_price:,}  |  Lieferzeit: {delivery_weeks} Wochen", ln=True)
        pdf.cell(0, 6, f"Schätzleistung: {picks_per_minute:.0f} Picks/Min  |  Status: {overall_status}", ln=True)
        pdf.ln(8)
        
        # Status table
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 7, "Layer", 1, 0, "C")
        pdf.cell(40, 7, "Status", 1, 0, "C")
        pdf.cell(40, 7, "Auslastung", 1, 0, "C")
        pdf.cell(40, 7, "Details", 1, 1, "C")
        
        pdf.set_font("Helvetica", "", 9)
        status_layers = [
            ("Mechanik & Inertia", inertia_status, f"{inertia_utilization:.0f}%", f"Traegheit: {total_inertia:.4f} kg·m²"),
            ("Payload", payload_status if payload_utilization <= 90 else "KRITISCH", f"{payload_utilization:.0f}%", f"Last: {total_payload:.2f} kg"),
            ("Taktzeit", cycle_status, f"{cycle_time:.2f}s/Zyklus", f"{picks_per_minute:.0f} Picks/min"),
            ("Schnittstellen", interface_status, "-" if interface_status == "PASS" else "-", "Flansch/Protokoll"),
        ]
        for layer, st, util, det in status_layers:
            pdf.cell(60, 7, layer, 1, 0, "L")
            pdf.cell(40, 7, st, 1, 0, "C")
            pdf.cell(40, 7, util, 1, 0, "C")
            pdf.cell(40, 7, det, 1, 1, "L")
        
        pdf.ln(8)
        
        # === REQUIREMENTS ===
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "1. ANFORDERUNGEN", ln=True)
        pdf.set_font("Helvetica", "", 10)
        
        pdf.cell(50, 7, "Werkstückmasse:", 0, 0, "L")
        pdf.cell(50, 7, f"{request.workpiece_mass_kg} kg", 0, 0, "L")
        pdf.cell(50, 7, "Robot:", 0, 0, "L")
        pdf.cell(0, 7, f"{robot['brand']} {robot['model_name']}", ln=True)
        
        pdf.cell(50, 7, "Pick-Place Distanz:", 0, 0, "L")
        pdf.cell(50, 7, f"{request.target_distance_m} m", 0, 0, "L")
        pdf.cell(50, 7, "Greifer:", 0, 0, "L")
        pdf.cell(0, 7, f"{gripper['manufacturer']} {gripper['model_name']}", ln=True)
        
        pdf.cell(50, 7, "Arbeitsbereich:", 0, 0, "L")
        pdf.cell(50, 7, f"{request.operating_angle_deg}° {request.operating_direction}", 0, 0, "L")
        pdf.cell(50, 7, "PLC:", 0, 0, "L")
        pdf.cell(0, 7, f"{plc['brand']} {plc['model_name']}", ln=True)
        
        pdf.ln(5)
        
        # === ASSUMPTIONS (compact table) ===
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "2. KRITISCHE ANNAHMEN", ln=True)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 6, "Alle Annahmen muessen vor Angebotserstellung validiert werden:", ln=True)
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(15, 6, "ID", 1, 0, "C")
        pdf.cell(110, 6, "Annahme", 1, 0, "L")
        pdf.cell(0, 6, "Konsequenz bei Nichteinhaltung", 1, 1, "L")
        
        assumptions = [
            ("A1", "Werkstueckoberflaeche trocken", "Greiferlosung versagt"),
            ("A2", "Werkstuecktemperatur <= 25°C", "Reibung und Festigkeit aendern sich"),
            ("A3", "Keine explosive Atmosphäre", "ATEX Pruefung erforderlich"),
            ("A4", "Beleuchtung kontrollierbar", "Vision funktioniert nicht"),
            ("A5", "Druckluft 6 bar vorhanden", "Pneumatik versagt"),
            ("A6", "400V AC 16A verfuegbar", "PLC/Safety startet nicht"),
            ("A7", "Erdung geprüft installiert", "EMV Konformitaetsproblem"),
            ("A8", "Sicherheitsrating geprüft", "ISO 10218-1 nicht erfuellt"),
            ("A9", "Wartungszugang gewaehrleistet", "Inspektion nicht moeglich"),
            ("A10", "Not-Halt Kette funktioniert", "Stillstand bei Auslösung"),
            ("A11", "Gehause IP54+", "Staub/Feuchtigkeitsschaden"),
            ("A12", "Geräuschpegel <= 75dB", "Arbeitsplatzrichtlinie verletzt"),
            ("A13", "Keine starken Vibrationen", "Vision Fehler"),
            ("A14", "Ethernet Infrastruktur", "Profinet Kommunikation"),
            ("A15", "Bodenuebertragung stabil", "Positionierfehler"),
        ]
        
        pdf.set_font("Helvetica", "", 7)
        for ann_id, ann_text, ann_conseq in assumptions:
            pdf.cell(15, 5, ann_id, 1, 0, "C")
            pdf.cell(110, 5, ann_text, 1, 0, "L")
            pdf.cell(0, 5, ann_conseq[:45], 1, 1, "L")
        
        pdf.ln(5)
        
        # === PHYSICS - COMPACT RESULTS ===
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "3. PHYSIK ERGEBNISSE", ln=True)
        pdf.ln(2)
        
        # Inertia result
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 7, "Traegheit:", 0, 0, "L")
        pdf.cell(40, 7, f"{total_inertia:.4f} kg·m²", 0, 0, "L")
        pdf.cell(60, 7, "Max:", 0, 0, "L")
        pdf.cell(0, 7, f"{robot.get('max_inertia_kgm2')} kg·m²", ln=True)
        
        pdf.cell(60, 7, "Auslastung:", 0, 0, "L")
        pdf.set_text_color(34, 197, 94) if inertia_utilization <= 90 else pdf.set_text_color(239, 68, 68)
        pdf.cell(40, 7, f"{inertia_utilization:.0f}%", 0, 0, "L")
        pdf.set_text_color(0, 0, 0)
        pdf.cell(60, 7, "Status:", 0, 0, "L")
        pdf.cell(0, 7, inertia_status, ln=True)
        
        pdf.ln(2)
        
        # Cycle time result
        pdf.cell(60, 7, "Taktzeit:", 0, 0, "L")
        pdf.cell(40, 7, f"{cycle_time:.3f} s", 0, 0, "L")
        pdf.cell(60, 7, "Leistung:", 0, 0, "L")
        pdf.cell(0, 7, f"{picks_per_minute:.0f} Picks/min", ln=True)
        
        pdf.cell(60, 7, "Latenz:", 0, 0, "L")
        pdf.cell(40, 7, f"{total_latency*1000:.1f} ms", 0, 0, "L")
        pdf.cell(60, 7, "Status:", 0, 0, "L")
        pdf.set_text_color(34, 197, 94) if cycle_status == "GRÜN" else pdf.set_text_color(239, 68, 68)
        pdf.cell(0, 7, cycle_status, ln=True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.ln(2)
        
        # Payload result
        pdf.cell(60, 7, "Last gesamt:", 0, 0, "L")
        pdf.cell(40, 7, f"{total_payload:.2f} kg", 0, 0, "L")
        pdf.cell(60, 7, "Max:", 0, 0, "L")
        pdf.cell(0, 7, f"{robot.get('max_payload_kg')} kg", ln=True)
        
        pdf.cell(60, 7, "Auslastung:", 0, 0, "L")
        pdf.set_text_color(34, 197, 94) if payload_utilization <= 90 else pdf.set_text_color(239, 68, 68)
        pdf.cell(0, 7, f"{payload_utilization:.0f}%", ln=True)
        pdf.set_text_color(0, 0, 0)
        
        pdf.ln(5)
        
        pdf.ln(5)
        
        # === INTERFACES ===
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "4. SCHNITTSTELLEN", ln=True)
        pdf.set_font("Helvetica", "", 10)
        
        # 3-column layout: label (50) + value (50) + label (50) + value (remaining)
        pdf.cell(50, 7, "Robot:", 0, 0, "L")
        pdf.cell(50, 7, robot.get("flange_iso_code"), 0, 0, "L")
        pdf.cell(50, 7, "Greifer:", 0, 0, "L")
        pdf.cell(0, 7, gripper.get("mounting_pattern"), ln=True)
        
        pdf.cell(50, 7, "Robot I/O:", 0, 0, "L")
        pdf.cell(50, 7, f"{robot.get('io_max_current_a')} A", 0, 0, "L")
        pdf.cell(50, 7, "Greifer Peak:", 0, 0, "L")
        pdf.cell(0, 7, f"{gripper.get('peak_current_a')} A", ln=True)
        
        pdf.cell(50, 7, "Robot Protokoll:", 0, 0, "L")
        pdf.cell(50, 7, ", ".join(robot.get("protocols", [])), 0, 0, "L")
        pdf.cell(50, 7, "Greifer Protokoll:", 0, 0, "L")
        pdf.cell(0, 7, ", ".join(gripper.get("protocols", [])), ln=True)
        
        common_protos = list(set(robot.get("protocols", [])) & set(gripper.get("protocols", [])))
        pdf.cell(50, 7, "Gemeinsam:", 0, 0, "L")
        pdf.set_text_color(34, 197, 94) if common_protos else pdf.set_text_color(239, 68, 68)
        pdf.cell(50, 7, ", ".join(common_protos) if common_protos else "KEINS", ln=True)
        pdf.set_text_color(0, 0, 0)
        
        if vision:
            pdf.cell(50, 7, "Vision:", 0, 0, "L")
            pdf.cell(0, 7, f"{vision['brand']} {vision['model_name']} ({vision.get('processing_latency_ms')}ms)", ln=True)
        
        if pneumatic:
            pdf.cell(50, 7, "Pneumatik:", 0, 0, "L")
            pdf.cell(0, 7, f"{pneumatic['brand']} {pneumatic['model_name']} ({pneumatic.get('voltage_v')})", ln=True)
        
        if sensor:
            pdf.cell(50, 7, "Sensor:", 0, 0, "L")
            pdf.cell(0, 7, f"{sensor['brand']} {sensor['model_name']}", ln=True)
        
        if safety:
            pdf.cell(50, 7, "Safety:", 0, 0, "L")
            pdf.cell(0, 7, f"{safety['brand']} {safety['model_name']} ({safety.get('safety_rating')})", ln=True)
        
        pdf.ln(5)
        
        # === COMPONENT DETAILS ===
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "5. KOMPONENTEN", ln=True)
        pdf.set_font("Helvetica", "B", 9)
        
        components = [
            ("Robot", robot, ["brand", "model_name", "robot_type", "max_payload_kg", "max_inertia_kgm2", "max_reach_mm", "max_v_ms", "protocols", "price_eur", "delivery_weeks"]),
            ("Greifer", gripper, ["manufacturer", "model_name", "mass_kg", "inertia_cm", "com_offset_z_mm", "mounting_pattern", "peak_current_a", "protocols", "price_eur", "delivery_weeks"]),
            ("PLC", plc, ["brand", "model_name", "digital_inputs", "digital_outputs", "protocols", "price_eur", "delivery_weeks"]),
        ]
        
        if vision:
            components.append(("Vision", vision, ["brand", "model_name", "resolution_mpx", "frame_rate_fps", "processing_latency_ms", "protocols", "price_eur", "delivery_weeks"]))
        if sensor:
            components.append(("Sensor", sensor, ["brand", "model_name", "sensor_type", "detection_range_mm", "response_time_ms", "io_type", "price_eur", "delivery_weeks"]))
        if pneumatic:
            components.append(("Pneumatik", pneumatic, ["brand", "model_name", "component_type", "switching_time_ms", "voltage_v", "price_eur", "delivery_weeks"]))
        if feeder:
            components.append(("Feeder", feeder, ["brand", "model_name", "feeder_type", "max_part_size_mm", "max_feed_rate_ppm", "voltage", "price_eur", "delivery_weeks"]))
        if safety:
            components.append(("Sicherheit", safety, ["brand", "model_name", "safety_type", "protected_height_mm", "response_time_ms", "safety_rating", "price_eur", "delivery_weeks"]))
        components.append(("Gehause", housing, ["brand", "model_name", "width_m", "depth_m", "height_m", "area_m2", "material", "price_eur"]))
        
        for comp_name, comp_data, fields in components:
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, f"{comp_name}: {comp_data.get('brand', '')} {comp_data.get('model_name')}", ln=True)
            pdf.set_font("Helvetica", "", 8)
            
            field_labels = {
                "brand": "Marke", "model_name": "Modell", "manufacturer": "Hersteller",
                "robot_type": "Typ", "max_payload_kg": "Max Payload", "max_inertia_kgm2": "Max Inertia",
                "max_reach_mm": "Reichweite", "max_v_ms": "Max Geschw.", "protocols": "Protokolle",
                "price_eur": "Preis", "delivery_weeks": "Lieferzeit",
                "mass_kg": "Masse", "inertia_cm": "Traegheit", "com_offset_z_mm": "Offset Z",
                "mounting_pattern": "Flansch", "peak_current_a": "Strom",
                "digital_inputs": "DI", "digital_outputs": "DO",
                "resolution_mpx": "Aufloesung", "frame_rate_fps": "FPS", "processing_latency_ms": "Latenz",
                "sensor_type": "Typ", "detection_range_mm": "Bereich", "response_time_ms": "Antwort", "io_type": "I/O",
                "component_type": "Typ", "switching_time_ms": "Schaltzeit", "voltage_v": "Spannung",
                "feeder_type": "Typ", "max_part_size_mm": "Max Teil", "max_feed_rate_ppm": "Rate", "voltage": "Versorgung",
                "safety_type": "Sicherheit", "protected_height_mm": "Schutzhoehe", "safety_rating": "Rating",
                "width_m": "Breite", "depth_m": "Tiefe", "height_m": "Hoehe", "area_m2": "Flaeche", "material": "Material"
            }
            
            # 2-column layout: pack pairs of fields
            col1_label_w = 32
            col1_val_w = 52
            col2_label_w = 32
            col2_val_w = 0  # remaining
            
            n_fields = len(fields)
            for i in range(0, n_fields, 2):
                f1 = fields[i]
                f2 = fields[i+1] if i+1 < n_fields else None
                
                # Column 1: field1
                if f1 in comp_data and comp_data[f1] is not None:
                    label1 = field_labels.get(f1, f1)
                    val1 = comp_data[f1]
                    if isinstance(val1, list):
                        val1 = ", ".join(val1)
                    elif isinstance(val1, float):
                        val1 = f"{val1}"
                    elif isinstance(val1, int) and f1 == "price_eur":
                        val1 = f"EUR {val1:,}"
                    pdf.cell(col1_label_w, 5, f"{label1}:", 0, 0, "L")
                    pdf.cell(col1_val_w, 5, str(val1), 0, 0, "L")
                else:
                    pdf.cell(col1_label_w + col1_val_w, 5, "", 0, 0, "L")
                
                # Column 2: field2 (if exists)
                if f2 and f2 in comp_data and comp_data[f2] is not None:
                    label2 = field_labels.get(f2, f2)
                    val2 = comp_data[f2]
                    if isinstance(val2, list):
                        val2 = ", ".join(val2)
                    elif isinstance(val2, float):
                        val2 = f"{val2}"
                    elif isinstance(val2, int) and f2 == "price_eur":
                        val2 = f"EUR {val2:,}"
                    pdf.cell(col2_label_w, 5, f"{label2}:", 0, 0, "L")
                    pdf.cell(col2_val_w, 5, str(val2), ln=True)
                else:
                    pdf.ln(5)
        
        pdf.ln(8)
        
        # === BOM ===
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "6. STUECKLISTE", ln=True)
        
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(10, 7, "#", 1, 0, "C")
        pdf.cell(50, 7, "Komponente", 1, 0, "L")
        pdf.cell(80, 7, "Details", 1, 0, "L")
        pdf.cell(40, 7, "Preis (EUR)", 1, 1, "R")
        
        pdf.set_font("Helvetica", "", 9)
        
        bom_items = [
            ("R", robot, f"{robot['brand']} {robot['model_name']}", robot.get("price_eur", 0)),
            ("G", gripper, f"{gripper['manufacturer']} {gripper['model_name']}", gripper.get("price_eur", 0)),
            ("P", plc, f"{plc['brand']} {plc['model_name']}", plc.get("price_eur", 0)),
        ]
        if vision:
            bom_items.append(("V", vision, f"{vision['brand']} {vision['model_name']}", vision.get("price_eur", 0)))
        if sensor:
            bom_items.append(("S", sensor, f"{sensor['brand']} {sensor['model_name']}", sensor.get("price_eur", 0)))
        if pneumatic:
            bom_items.append(("N", pneumatic, f"{pneumatic['brand']} {pneumatic['model_name']}", pneumatic.get("price_eur", 0)))
        if feeder:
            bom_items.append(("F", feeder, f"{feeder['brand']} {feeder['model_name']}", feeder.get("price_eur", 0)))
        if safety:
            bom_items.append(("Si", safety, f"{safety['brand']} {safety['model_name']}", safety.get("price_eur", 0)))
        bom_items.append(("H", housing, f"{housing.get('model_name')}", housing.get("price_eur", 0)))
        
        grand_total = 0
        for pos, comp, desc, price in bom_items:
            price = price or 0
            grand_total += int(price)
            pdf.cell(10, 7, pos, 1, 0, "C")
            pdf.cell(50, 7, desc[:25], 1, 0, "L")
            pdf.cell(80, 7, str(comp.get('model_name', ''))[:40], 1, 0, "L")
            pdf.cell(40, 7, f"{price:,}", 1, 1, "R")
        
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(140, 8, "GESAMT:", 1, 0, "R")
        pdf.cell(40, 8, f"{grand_total:,} EUR", 1, 1, "R")
        
        pdf.ln(10)
        
        # === DISCLAIMER ===
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "INTERN! Dieses Dokument dient der internen Validierung und stellt keine Empfehlung dar.", ln=True)
        pdf.cell(0, 5, "Alle technischen Daten basieren auf Herstellerangaben. Pruefung vor Angebot erforderlich.", ln=True)
        pdf.cell(0, 5, f"Generiert: {datetime.now().strftime('%d.%m.%Y %H:%M')} - PESE v0.1.0", ln=True)
        
        pdf_bytes = pdf.output(dest="S")
        return Response(content=bytes(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=Technisches_Audit_{request.project_name}.pdf"})
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}\n{traceback.format_exc()}")
