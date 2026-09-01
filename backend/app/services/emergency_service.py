INDIAN_EMERGENCY_NUMBERS = {
    "ambulance": "108",
    "national_emergency": "112",
    "women_helpline": "1091"
}


def should_trigger_emergency(triage_level: str, red_flag_level: str) -> bool:
    return triage_level == "emergency" or red_flag_level == "high"


def get_emergency_response(triage_level: str, red_flag_level: str, nearby_hospitals: list = None) -> dict:
    triggered = should_trigger_emergency(triage_level, red_flag_level)

    return {
        "emergency_triggered": triggered,
        "ambulance_number": INDIAN_EMERGENCY_NUMBERS["ambulance"] if triggered else None,
        "national_emergency_number": INDIAN_EMERGENCY_NUMBERS["national_emergency"] if triggered else None,
        "message": (
            "This case has been flagged as a potential emergency. Call 108 (Ambulance) or 112 "
            "(National Emergency) immediately, or proceed to the nearest hospital."
            if triggered else None
        ),
        "nearby_hospitals": nearby_hospitals or []
    }