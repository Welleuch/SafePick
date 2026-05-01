"""
SafePick Python Worker for Cloudflare
Ported from FastAPI backend
"""

import json
from typing import Optional, List
from workers import WorkerEntrypoint, Request, Response
from pydantic import BaseModel


# ==================== DATABASE (In-Memory) ====================

ROBOT_DB = [
    {"id": "kuka-kr-3-delta", "brand": "KUKA", "model_name": "KR 3 Delta", "robot_type": "Delta",
     "max_payload_kg": 3.0, "max_inertia_kgm2": 0.05, "flange_iso_code": "ISO 9409-1-31.5-4-M5",
     "max_v_ms": 10.0, "max_a_ms2": 50.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "EtherCAT"],
     "max_reach_mm": 600, "source": "KUKA product specifications", "price_eur": 45000, "delivery_weeks": 8},
    {"id": "fanuc-m-1ia", "brand": "Fanuc", "model_name": "M-1iA/1H", "robot_type": "Delta",
     "max_payload_kg": 1.0, "max_inertia_kgm2": 0.02, "flange_iso_code": "ISO 9409-1-31.5-4-M5",
     "max_v_ms": 8.0, "max_a_ms2": 40.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 400, "source": "Fanuc product specifications", "price_eur": 38000, "delivery_weeks": 6},
    {"id": "abb-irb-360", "brand": "ABB", "model_name": "IRB 360-3/1130", "robot_type": "Delta",
     "max_payload_kg": 3.0, "max_inertia_kgm2": 0.055, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 10.0, "max_a_ms2": 50.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "DeviceNet"],
     "max_reach_mm": 1130, "source": "ABB datasheet", "price_eur": 52000, "delivery_weeks": 10},
    {"id": "epson-gx11b", "brand": "Epson", "model_name": "GX11-B650", "robot_type": "SCARA",
     "max_payload_kg": 11.0, "max_inertia_kgm2": 0.12, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 4.5, "max_a_ms2": 15.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 650, "source": "Epson GX-Series datasheet", "price_eur": 32000, "delivery_weeks": 6},
    {"id": "yamaha-yk500xg", "brand": "Yamaha", "model_name": "YK500XG", "robot_type": "SCARA",
     "max_payload_kg": 10.0, "max_inertia_kgm2": 0.10, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 5.0, "max_a_ms2": 15.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "EtherCAT"],
     "max_reach_mm": 500, "source": "Yamaha YK-XG series spec", "price_eur": 28000, "delivery_weeks": 5},
    {"id": "denso-hm-60", "brand": "Denso", "model_name": "HM-60", "robot_type": "SCARA",
     "max_payload_kg": 10.0, "max_inertia_kgm2": 0.10, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 5.5, "max_a_ms2": 15.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 600, "source": "Denso HM-Series datasheet", "price_eur": 35000, "delivery_weeks": 8},
    {"id": "kuka-kr-10", "brand": "KUKA", "model_name": "KR 10 R1610", "robot_type": "6-Axis",
     "max_payload_kg": 10.0, "max_inertia_kgm2": 0.20, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 3.0, "max_a_ms2": 10.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 1610, "source": "KUKA KR 10 Sixx spec", "price_eur": 55000, "delivery_weeks": 10},
    {"id": "abb-irb-2600", "brand": "ABB", "model_name": "IRB 2600-12/1.65", "robot_type": "6-Axis",
     "max_payload_kg": 12.0, "max_inertia_kgm2": 0.25, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 3.0, "max_a_ms2": 10.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "DeviceNet"],
     "max_reach_mm": 1650, "source": "ABB IRB 2600 spec", "price_eur": 62000, "delivery_weeks": 12},
    {"id": "fanuc-m-20ia", "brand": "Fanuc", "model_name": "M-20iA/10L", "robot_type": "6-Axis",
     "max_payload_kg": 10.0, "max_inertia_kgm2": 0.20, "flange_iso_code": "ISO 9409-1-50-4-M6",
     "max_v_ms": 3.0, "max_a_ms2": 10.0, "io_max_current_a": 2.0, "protocols": ["Profinet", "Ethernet/IP"],
     "max_reach_mm": 2009, "source": "Fanuc M-20iA spec", "price_eur": 58000, "delivery_weeks": 10},
]

GRIPPER_DB = [
    {"id": "schunk-pgn-plus-p-100", "manufacturer": "Schunk", "model_name": "PGN-plus-P 100",
     "mass_kg": 0.45, "inertia_cm": 0.0001, "com_offset_z_mm": 50, "grip_offset_z_mm": 80,
     "mounting_pattern": "ISO 9409-1-31.5-4-M5", "peak_current_a": 1.5, "protocols": ["Profinet", "EtherCAT"],
     "source": "Schunk catalog", "price_eur": 2500, "delivery_weeks": 4},
    {"id": "zimmer-gp400", "manufacturer": "Zimmer", "model_name": "GP400",
     "mass_kg": 0.38, "inertia_cm": 0.00008, "com_offset_z_mm": 45, "grip_offset_z_mm": 70,
     "mounting_pattern": "ISO 9409-1-31.5-4-M5", "peak_current_a": 1.2, "protocols": ["Profinet", "EtherCAT"],
     "source": "Zimmer catalog", "price_eur": 2200, "delivery_weeks": 3},
    {"id": "festo-hew-16", "manufacturer": "Festo", "model_name": "HEW-16",
     "mass_kg": 0.25, "inertia_cm": 0.00005, "com_offset_z_mm": 40, "grip_offset_z_mm": 60,
     "mounting_pattern": "ISO 9409-1-31.5-4-M5", "peak_current_a": 1.0, "protocols": ["Profinet", "IO-Link"],
     "source": "Festo catalog", "price_eur": 1800, "delivery_weeks": 2},
]

VISION_SYSTEMS_DB = [
    {"id": "keyence-cv-x200", "brand": "Keyence", "model_name": "CV-X200", "resolution_mpx": 2.0,
     "frame_rate_fps": 120, "processing_latency_ms": 15, "protocols": ["Profinet", "EtherNet/IP"],
     "field_of_view_deg": 45, "min_part_size_mm": 2.0, "lighting_type": "LED",
     "source": "Keyence catalog", "price_eur": 8500, "delivery_weeks": 4},
    {"id": "cognex-insight-7200", "brand": "Cognex", "model_name": "In-Sight 7200", "resolution_mpx": 2.0,
     "frame_rate_fps": 100, "processing_latency_ms": 20, "protocols": ["EtherNet/IP", "Profinet"],
     "field_of_view_deg": 40, "min_part_size_mm": 3.0, "lighting_type": "LED",
     "source": "Cognex catalog", "price_eur": 7800, "delivery_weeks": 4},
    {"id": "basler-ace-2300", "brand": "Basler", "model_name": "ace 2300", "resolution_mpx": 2.3,
     "frame_rate_fps": 80, "processing_latency_ms": 25, "protocols": ["GigE", "USB3"],
     "field_of_view_deg": 35, "min_part_size_mm": 5.0, "lighting_type": "IR",
     "source": "Basler catalog", "price_eur": 5200, "delivery_weeks": 3},
]

SENSORS_DB = [
    {"id": "sick-ild-170", "brand": "SICK", "model_name": "ILD 170-100", "sensor_type": "Laser Distance",
     "detection_range_mm": 100, "response_time_ms": 0.5, "io_type": "PNP", "output_type": "NO",
     "source": "SICK catalog", "price_eur": 450, "delivery_weeks": 2},
    {"id": "keyence-il-300", "brand": "Keyence", "model_name": "IL-300BG", "sensor_type": "photoelectric",
     "detection_range_mm": 300, "response_time_ms": 0.1, "io_type": "PNP", "output_type": "NO",
     "source": "Keyence catalog", "price_eur": 320, "delivery_weeks": 2},
]

PLC_CONTROLLERS_DB = [
    {"id": "siemens-s7-1500", "brand": "Siemens", "model_name": "CPU 1516-3 PN/DP", "digital_inputs": 32,
     "digital_outputs": 32, "protocols": ["Profinet", "Profibus"], "io_link_master_ports": 16,
     "source": "Siemens catalog", "price_eur": 8500, "delivery_weeks": 6},
    {"id": "beckhoff-cx5020", "brand": "Beckhoff", "model_name": "CX5020-0120-0100", "digital_inputs": 16,
     "digital_outputs": 16, "protocols": ["EtherCAT", "Profinet"], "io_link_master_ports": 8,
     "source": "Beckhoff catalog", "price_eur": 6200, "delivery_weeks": 4},
]

FEEDERS_DB = [
    {"id": "rna-zs-200", "brand": "RNA", "model_name": "ZS 200RC", "feeder_type": "Bowl",
     "max_part_size_mm": 80, "max_feed_rate_ppm": 120, "pick_height_mm": 200,
     "vibration_controllable": True, "voltage": "230VAC", "protocols": ["Profinet"],
     "source": "RNA catalog", "price_eur": 12000, "delivery_weeks": 8},
]

SAFETY_SYSTEMS_DB = [
    {"id": "sick-s3000", "brand": "SICK", "model_name": "S3000", "safety_type": "Laser Scanner",
     "protected_height_mm": 190, "response_time_ms": 8, "safety_rating": "PLd",
     "protocols": ["Profinet", "Flexi"],
     "source": "SICK catalog", "price_eur": 4200, "delivery_weeks": 4},
]

SAFETY_HOUSING_DB = [
    {"id": "item-d-30", "brand": "Item", "model_name": "D30", "material": "Aluminum",
     "min_enclosure_m3": 0.5, "profile_type": "D30",
     "glass_type": "Polycarbonate", "price_eur_per_m2": 280,
     "source": "Item catalog"},
]


# ==================== PHYSICS ENGINE ====================

class ValidationEngine:
    """Physics validation engine for SafePick"""
    
    def run_full_validation(self, robot, gripper, workpiece_mass_kg, target_distance_m):
        # Inertia calculation
        gripper_inertia = gripper.get("inertia_cm", 0.0001) + gripper.get("mass_kg", 0.3) * (gripper.get("com_offset_z_mm", 50) / 1000) ** 2
        workpiece_inertia = workpiece_mass_kg * (gripper.get("grip_offset_z_mm", 70) / 1000) ** 2
        total_inertia = gripper_inertia + workpiece_inertia
        
        max_inertia = robot.get("max_inertia_kgm2", 0.05)
        inertia_utilization = (total_inertia / max_inertia) * 100 if max_inertia > 0 else 0
        inertia_status = "GRÜN" if inertia_utilization <= 90 else "KRITISCH"
        
        # Cycle time calculation
        max_v = robot.get("max_v_ms", 10.0)
        max_a = robot.get("max_a_ms2", 50.0)
        
        t_accel = max_v / max_a if max_a > 0 else 0
        dist_accel = 0.5 * max_a * t_accel ** 2
        
        if 2 * dist_accel <= target_distance_m:
            t_const = (target_distance_m - 2 * dist_accel) / max_v if max_v > 0 else 0
            cycle_base = (2 * t_accel) + t_const
        else:
            cycle_base = 2 * (target_distance_m / max_a) ** 0.5 if max_a > 0 else 0
            t_const = 0
        
        # Add latency buffer (15%)
        cycle_time = cycle_base * 1.15
        picks_per_minute = 60 / cycle_time if cycle_time > 0 else 0
        cycle_status = "GRÜN" if picks_per_minute >= 30 else "KRITISCH"
        
        # Payload check
        total_payload = workpiece_mass_kg + gripper.get("mass_kg", 0.3)
        max_payload = robot.get("max_payload_kg", 3.0)
        payload_utilization = (total_payload / max_payload) * 100 if max_payload > 0 else 0
        payload_status = "GRÜN" if payload_utilization <= 90 else "KRITISCH"
        
        # Interface check
        flange_match = robot.get("flange_iso_code") == gripper.get("mounting_pattern")
        current_match = robot.get("io_max_current_a", 2.0) >= gripper.get("peak_current_a", 1.5)
        
        interface_status = "GRÜN" if (flange_match and current_match) else "KRITISCH"
        
        # Overall status
        valid = inertia_status == "GRÜN" and cycle_status == "GRÜN" and payload_status == "GRÜN" and interface_status == "GRÜN"
        
        return {
            "valid": valid,
            "inertia": {
                "total_kgm2": round(total_inertia, 6),
                "max_kgm2": max_inertia,
                "utilization_pct": round(inertia_utilization, 1),
                "status": inertia_status
            },
            "cycle_time": {
                "seconds": round(cycle_time, 3),
                "picks_per_minute": round(picks_per_minute, 1),
                "status": cycle_status
            },
            "payload": {
                "total_kg": round(total_payload, 2),
                "max_kg": max_payload,
                "utilization_pct": round(payload_utilization, 1),
                "status": payload_status
            },
            "interface": {
                "flange_match": flange_match,
                "current_match": current_match,
                "status": interface_status
            }
        }


# ==================== ROUTING ====================

validation_engine = ValidationEngine()


def parse_json_body(request: Request) -> dict:
    """Parse JSON from request body"""
    import js
    body = request.text()
    return json.loads(body)


def filter_robots_by_requirements(workpiece_mass: float, distance_m: float, 
                                   picks_per_minute: Optional[float] = None, 
                                   max_cycle_time: Optional[float] = None) -> List[dict]:
    """Filter robots based on requirements"""
    valid_robots = []
    for robot in ROBOT_DB:
        gripper_mass_est = 0.3
        total_mass = workpiece_mass + gripper_mass_est
        if total_mass > robot["max_payload_kg"]:
            continue
        if picks_per_minute and picks_per_minute > 0:
            required_cycle = 60.0 / picks_per_minute
            t_accel = robot["max_v_ms"] / robot["max_a_ms2"]
            est_time = (2 * t_accel) + (distance_m / robot["max_v_ms"])
            est_time = est_time * 1.15
            if est_time > required_cycle * 1.2:
                continue
        valid_robots.append(robot)
    valid_robots.sort(key=lambda r: (r["price_eur"], r["delivery_weeks"]))
    return valid_robots[:3]


class Default(WorkerEntrypoint):
    async def fetch(self, request: Request):
        # CORS headers
        cors_headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        
        # Handle OPTIONS preflight
        if request.method == "OPTIONS":
            return Response(None, headers=cors_headers)
        
        # Parse path
        path = request.path
        method = request.method
        
        # Health check
        if path == "/health" or path == "/":
            return Response(
                json.dumps({"status": "ok", "service": "SafePick Worker"}),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        # API Routes
        if path == "/api/v1/robots" and method == "GET":
            return Response(
                json.dumps(ROBOT_DB),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        if path == "/api/v1/grippers" and method == "GET":
            return Response(
                json.dumps(GRIPPER_DB),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        if path == "/api/v1/vision-systems" and method == "GET":
            return Response(
                json.dumps(VISION_SYSTEMS_DB),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        if path == "/api/v1/sensors" and method == "GET":
            return Response(
                json.dumps(SENSORS_DB),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        if path == "/api/v1/plc-controllers" and method == "GET":
            return Response(
                json.dumps(PLC_CONTROLLERS_DB),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        if path == "/api/v1/pneumatics" and method == "GET":
            return Response(
                json.dumps([]),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        if path == "/api/v1/feeders" and method == "GET":
            return Response(
                json.dumps(FEEDERS_DB),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        if path == "/api/v1/safety-systems" and method == "GET":
            return Response(
                json.dumps(SAFETY_SYSTEMS_DB),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        if path == "/api/v1/safety-housing" and method == "GET":
            return Response(
                json.dumps(SAFETY_HOUSING_DB),
                headers={**cors_headers, "Content-Type": "application/json"}
            )
        
        # POST /api/v1/validate
        if path == "/api/v1/validate" and method == "POST":
            try:
                body = parse_json_body(request)
                robot_id = body.get("robot_id")
                gripper_id = body.get("gripper_id")
                workpiece_mass_kg = body.get("workpiece_mass_kg", 0)
                target_distance_m = body.get("target_distance_m", 0)
                
                robot = next((r for r in ROBOT_DB if r["id"] == robot_id), None)
                gripper = next((g for g in GRIPPER_DB if g["id"] == gripper_id), None)
                
                if not robot or not gripper:
                    return Response(
                        json.dumps({"error": "Robot or Gripper not found"}),
                        status=404,
                        headers={**cors_headers, "Content-Type": "application/json"}
                    )
                
                result = validation_engine.run_full_validation(
                    robot, gripper, workpiece_mass_kg, target_distance_m
                )
                
                response = {"status": "GRÜN" if result["valid"] else "KRITISCH", **result}
                
                return Response(
                    json.dumps(response),
                    headers={**cors_headers, "Content-Type": "application/json"}
                )
            except Exception as e:
                return Response(
                    json.dumps({"error": str(e)}),
                    status=500,
                    headers={**cors_headers, "Content-Type": "application/json"}
                )
        
        # POST /api/v1/recommend-robots
        if path == "/api/v1/recommend-robots" and method == "POST":
            try:
                body = parse_json_body(request)
                workpiece_mass_kg = body.get("workpiece_mass_kg", 0)
                pick_place_distance_m = body.get("pick_place_distance_m", 0)
                picks_per_minute = body.get("picks_per_minute")
                max_cycle_time_s = body.get("max_cycle_time_s")
                
                recommended = filter_robots_by_requirements(
                    workpiece_mass_kg,
                    pick_place_distance_m,
                    picks_per_minute,
                    max_cycle_time_s
                )
                
                return Response(
                    json.dumps({
                        "requirements": {
                            "workpiece_mass_kg": workpiece_mass_kg,
                            "pick_place_distance_m": pick_place_distance_m,
                            "picks_per_minute": picks_per_minute,
                            "max_cycle_time_s": max_cycle_time_s,
                        },
                        "recommendations": recommended
                    }),
                    headers={**cors_headers, "Content-Type": "application/json"}
                )
            except Exception as e:
                return Response(
                    json.dumps({"error": str(e)}),
                    status=500,
                    headers={**cors_headers, "Content-Type": "application/json"}
                )
        
        # POST /api/v1/suggest-systems (9-category system suggestions)
        if path == "/api/v1/suggest-systems" and method == "POST":
            try:
                body = parse_json_body(request)
                workpiece_mass_kg = body.get("workpiece_mass_kg", 0)
                pick_place_distance_m = body.get("pick_place_distance_m", 0)
                picks_per_minute = body.get("picks_per_minute")
                operating_angle_deg = body.get("operating_angle_deg", 180)
                operating_direction = body.get("operating_direction", "front")
                
                suggestions = []
                gripper_mass_est = 0.3
                total_mass = workpiece_mass_kg + gripper_mass_est
                
                for robot in ROBOT_DB:
                    if total_mass > robot["max_payload_kg"]:
                        continue
                    
                    if picks_per_minute and picks_per_minute > 0:
                        required_cycle = 60.0 / picks_per_minute
                        t_accel = robot["max_v_ms"] / robot["max_a_ms2"]
                        est_time = (2 * t_accel) + (pick_place_distance_m / robot["max_v_ms"])
                        est_time = est_time * 1.15
                        if est_time > required_cycle * 1.2:
                            continue
                    
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
                            compatible_feeder = next((f for f in FEEDERS_DB if set(f.get("protocols", [])) & plc_protocols), None)
                            compatible_safety = next((s for s in SAFETY_SYSTEMS_DB if set(s.get("protocols", [])) & plc_protocols), None)
                            
                            total_price = (
                                robot.get("price_eur", 0) + 
                                gripper.get("price_eur", 0) + 
                                plc.get("price_eur", 0) +
                                (compatible_vision.get("price_eur", 0) if compatible_vision else 0) +
                                (compatible_sensor.get("price_eur", 0) if compatible_sensor else 0) +
                                (compatible_feeder.get("price_eur", 0) if compatible_feeder else 0) +
                                (compatible_safety.get("price_eur", 0) if compatible_safety else 0)
                            )
                            
                            suggestions.append({
                                "robot": robot,
                                "gripper": gripper,
                                "plc": plc,
                                "vision": compatible_vision,
                                "sensor": compatible_sensor,
                                "feeder": compatible_feeder,
                                "safety_system": compatible_safety,
                                "total_price": total_price,
                                "delivery_weeks": max(
                                    robot.get("delivery_weeks", 8),
                                    gripper.get("delivery_weeks", 4),
                                    plc.get("delivery_weeks", 4),
                                    compatible_vision.get("delivery_weeks", 4) if compatible_vision else 4,
                                    compatible_safety.get("delivery_weeks", 4) if compatible_safety else 4,
                                ),
                            })
                
                suggestions.sort(key=lambda s: (s["total_price"], s["delivery_weeks"]))
                
                return Response(
                    json.dumps({"suggestions": suggestions[:3]}),
                    headers={**cors_headers, "Content-Type": "application/json"}
                )
            except Exception as e:
                return Response(
                    json.dumps({"error": str(e)}),
                    status=500,
                    headers={**cors_headers, "Content-Type": "application/json"}
                )
        
        # 404 for unknown routes
        return Response(
            json.dumps({"error": "Not found"}),
            status=404,
            headers={**cors_headers, "Content-Type": "application/json"}
        )


# Entry point for the worker
app = WorkerEntrypoint(Default)