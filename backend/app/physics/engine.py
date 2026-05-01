import numpy as np
from pydantic import BaseModel
from typing import Optional


class GripperData(BaseModel):
    mass: float
    inertia_cm: float
    cm_offset: float
    grip_center_offset: float


class PhysicsEngine:
    def __init__(self):
        self.inertia_safety_factor = 0.90
        self.cycle_time_buffer = 1.15

    def calculate_inertia(
        self,
        robot_j_max: float,
        gripper_data: GripperData,
        workpiece_mass: float
    ) -> dict:
        """
        Pillar 1: Inertia-Guard
        Calculates J_total at flange using Parallel Axis Theorem.
        Formula: J = J_cm + m * d^2
        """
        m_g = gripper_data.mass
        j_g = gripper_data.inertia_cm
        d_g = gripper_data.cm_offset

        m_w = workpiece_mass
        d_w = gripper_data.grip_center_offset

        j_total = (j_g + m_g * d_g**2) + (m_w * d_w**2)
        utilization = j_total / robot_j_max
        is_safe = utilization <= self.inertia_safety_factor

        return {
            "calculated_inertia": round(j_total, 4),
            "utilization_percent": round(utilization * 100, 2),
            "status": "GRÜN" if is_safe else "KRITISCH",
            "status_de": "Innerhalb der Spezifikation" if is_safe else "Überschreitung der Spezifikation",
            "message": f"Konfiguration erreicht {round(utilization * 100, 1)}% der Nennkapazität."
        }

    def estimate_cycle_time(
        self,
        distance_m: float,
        max_v: float,
        max_a: float,
        pneumatic_latency: float = 0.05
    ) -> dict:
        """
        Pillar 2: Cycle-Time-Realist
        Trapezoidal velocity profile with 15% safety buffer.
        """
        t_accel = max_v / max_a
        dist_accel = 0.5 * max_a * t_accel**2

        if 2 * dist_accel <= distance_m:
            t_const = (distance_m - 2 * dist_accel) / max_v
            t_total = (2 * t_accel) + t_const
        else:
            t_total = 2 * np.sqrt(distance_m / max_a)

        buffered_time = (t_total + pneumatic_latency) * self.cycle_time_buffer

        return {
            "estimated_seconds": round(buffered_time, 2),
            "assumptions": [
                "Trapezförmiges Geschwindigkeitsprofil",
                f"{int((self.cycle_time_buffer-1)*100)}% Sicherheitspuffer"
            ],
            "status": "INFO"
        }


class InterfaceChecker:
    ISO_PATTERNS = {
        "ISO 9409-1-31.5-4-M5": {"bcd": 31.5, "bolts": 4, "thread": "M5"},
        "ISO 9409-1-50-4-M6": {"bcd": 50.0, "bolts": 4, "thread": "M6"},
        "ISO 9409-1-80-6-M8": {"bcd": 80.0, "bolts": 6, "thread": "M8"}
    }

    def verify_compatibility(
        self,
        robot_flange: str,
        robot_io_current: float,
        robot_protocols: list,
        gripper_flange: str,
        gripper_peak_current: float,
        gripper_protocols: list
    ) -> dict:
        """
        Pillar 3: Interface-Checker
        Three-layer validation: Mechanical, Electrical, Digital
        """
        mech_match = robot_flange == gripper_flange
        elec_match = robot_io_current >= gripper_peak_current
        common_protocols = set(robot_protocols) & set(gripper_protocols)
        protocol_match = len(common_protocols) > 0

        return {
            "mechanical": {
                "status": "PASS" if mech_match else "FAIL",
                "details": f"Flansch: {robot_flange}" if mech_match else "Adapterplatte erforderlich"
            },
            "electrical": {
                "status": "PASS" if elec_match else "FAIL",
                "details": f"Stromreserve: {round(robot_io_current - gripper_peak_current, 2)}A"
            },
            "digital": {
                "status": "PASS" if protocol_match else "FAIL",
                "details": list(common_protocols)[0] if protocol_match else "Kein gemeinsames Protokoll"
            },
            "overall_compatible": mech_match and elec_match and protocol_match
        }


class ValidationEngine:
    def __init__(self):
        self.physics = PhysicsEngine()
        self.interface = InterfaceChecker()

    def run_full_validation(
        self,
        robot: dict,
        gripper: dict,
        workpiece_mass: float,
        distance_m: float
    ) -> dict:
        """
        Run complete validation: Inertia + Cycle Time + Interface Check
        """
        gripper_data = GripperData(
            mass=gripper["mass_kg"],
            inertia_cm=gripper["inertia_cm"],
            cm_offset=gripper["com_offset_z_mm"] / 1000,
            grip_center_offset=gripper["grip_offset_z_mm"] / 1000
        )

        inertia_result = self.physics.calculate_inertia(
            robot["max_inertia_kgm2"],
            gripper_data,
            workpiece_mass
        )

        cycle_result = self.physics.estimate_cycle_time(
            distance_m,
            robot["max_v_ms"],
            robot["max_a_ms2"]
        )

        compatibility = self.interface.verify_compatibility(
            robot["flange_iso_code"],
            robot["io_max_current_a"],
            robot["protocols"],
            gripper["mounting_pattern"],
            gripper["peak_current_a"],
            gripper["protocols"]
        )

        is_valid = (
            inertia_result["status"] == "GRÜN" and
            compatibility["overall_compatible"]
        )

        return {
            "valid": is_valid,
            "inertia": inertia_result,
            "cycle_time": cycle_result,
            "interface": compatibility
        }