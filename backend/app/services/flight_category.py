"""Flight category calculation service."""

from typing import Optional


def calculate_flight_category(
    visibility_mi: Optional[float] = None,
    ceiling_ft: Optional[int] = None,
    ceiling_code: Optional[str] = None
) -> str:
    """
    Calculate flight category based on visibility and ceiling.
    
    Args:
        visibility_mi: Visibility in statute miles
        ceiling_ft: Ceiling height in feet AGL
        ceiling_code: Ceiling code (CLR, SKC, FEW, SCT, BKN, OVC, etc.)
    
    Returns:
        Flight category: VFR, MVFR, IFR, LIFR, or UNK
    """
    
    # Handle missing data
    if visibility_mi is None and ceiling_ft is None:
        return "UNK"
    
    # Determine ceiling category
    ceiling_category = _get_ceiling_category(ceiling_ft, ceiling_code)
    
    # Determine visibility category
    visibility_category = _get_visibility_category(visibility_mi)
    
    # Combine to get flight category
    return _combine_categories(visibility_category, ceiling_category)


def _get_ceiling_category(ceiling_ft: Optional[int], ceiling_code: Optional[str]) -> str:
    """Determine ceiling category."""
    if ceiling_ft is None:
        # If no ceiling height, check code
        if ceiling_code in ["CLR", "SKC"]:
            return "VFR"
        elif ceiling_code in ["FEW", "SCT"]:
            return "VFR"
        else:
            return "UNK"
    
    if ceiling_ft >= 3000:
        return "VFR"
    elif 1000 <= ceiling_ft < 3000:
        # Check if it's overcast or broken
        if ceiling_code in ["BKN", "OVC"]:
            return "MVFR"
        else:
            return "VFR"
    elif 500 <= ceiling_ft < 1000:
        if ceiling_code in ["BKN", "OVC"]:
            return "IFR"
        else:
            return "VFR"
    elif ceiling_ft < 500:
        if ceiling_code in ["BKN", "OVC"]:
            return "LIFR"
        else:
            return "VFR"
    else:
        return "UNK"


def _get_visibility_category(visibility_mi: Optional[float]) -> str:
    """Determine visibility category."""
    if visibility_mi is None:
        return "UNK"
    
    if visibility_mi > 5:
        return "VFR"
    elif 3 <= visibility_mi <= 5:
        return "MVFR"
    elif 1 <= visibility_mi < 3:
        return "IFR"
    elif 0 <= visibility_mi < 1:
        return "LIFR"
    else:
        return "UNK"


def _combine_categories(visibility_category: str, ceiling_category: str) -> str:
    """Combine visibility and ceiling categories to get flight category."""
    
    # If either is unknown, return unknown
    if visibility_category == "UNK" or ceiling_category == "UNK":
        return "UNK"
    
    # Priority order: LIFR > IFR > MVFR > VFR
    categories = [visibility_category, ceiling_category]
    
    if "LIFR" in categories:
        return "LIFR"
    elif "IFR" in categories:
        return "IFR"
    elif "MVFR" in categories:
        return "MVFR"
    else:
        return "VFR"


def get_flight_category_color(category: str) -> str:
    """Get color code for flight category display."""
    colors = {
        "VFR": "#00FF00",    # Green
        "MVFR": "#5555FF",   # Blue
        "IFR": "#FF5555",    # Red
        "LIFR": "#FF00FF",   # Magenta
        "UNK": "#AAAA00"     # Yellow
    }
    return colors.get(category, "#999999")  # Gray for unknown


def get_flight_category_description(category: str) -> str:
    """Get human-readable description of flight category."""
    descriptions = {
        "VFR": "Visual Flight Rules",
        "MVFR": "Marginal Visual Flight Rules",
        "IFR": "Instrument Flight Rules",
        "LIFR": "Low Instrument Flight Rules",
        "UNK": "Unknown"
    }
    return descriptions.get(category, "Unknown")
