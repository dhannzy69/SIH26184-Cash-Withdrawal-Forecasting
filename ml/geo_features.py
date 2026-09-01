"""
ml/geo_features.py
Geographic distance calculations using the Haversine formula and spatial relationship mapping.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two points on Earth in kilometers
    using the Haversine formula.
    """
    if pd.isna(lat1) or pd.isna(lon1) or pd.isna(lat2) or pd.isna(lon2):
        return 9999.0

    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)

    a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    km = 6371.0 * c
    return float(km)


def extract_geo_features(
    candidate_loc: Dict[str, Any],
    victim_region: str,
    active_account_regions: List[str],
    city_coords_lookup: Dict[str, Dict[str, float]]
) -> Dict[str, float]:
    """
    Extracts spatial distance features between a candidate ATM cluster location
    and the nodes of the active cybercrime case network.
    """
    c_lat = float(candidate_loc["latitude"])
    c_lon = float(candidate_loc["longitude"])
    c_city = str(candidate_loc["city"]).strip().lower()

    # 1. Distance to victim region
    v_coords = city_coords_lookup.get(victim_region.strip(), {})
    if v_coords:
        dist_to_victim = haversine_distance_km(c_lat, c_lon, v_coords["latitude"], v_coords["longitude"])
    else:
        dist_to_victim = 9999.0

    is_same_city_victim = 1.0 if c_city == victim_region.strip().lower() else 0.0

    # 2. Distance to terminal / active mule region
    terminal_region = active_account_regions[-1] if active_account_regions else victim_region
    term_coords = city_coords_lookup.get(terminal_region.strip(), {})
    if term_coords:
        dist_to_current_mule = haversine_distance_km(c_lat, c_lon, term_coords["latitude"], term_coords["longitude"])
    else:
        dist_to_current_mule = 9999.0

    is_same_city_mule = 1.0 if c_city == terminal_region.strip().lower() else 0.0

    # 3. Network-wide distance metrics
    network_distances = []
    for reg in active_account_regions:
        coords = city_coords_lookup.get(reg.strip(), {})
        if coords:
            d = haversine_distance_km(c_lat, c_lon, coords["latitude"], coords["longitude"])
            network_distances.append(d)

    if not network_distances:
        min_dist_network = dist_to_current_mule
        mean_dist_network = dist_to_current_mule
        max_dist_network = dist_to_current_mule
    else:
        min_dist_network = float(min(network_distances))
        mean_dist_network = float(np.mean(network_distances))
        max_dist_network = float(max(network_distances))

    return {
        "dist_candidate_to_victim_km": dist_to_victim,
        "dist_candidate_to_current_mule_km": dist_to_current_mule,
        "min_dist_candidate_to_network_km": min_dist_network,
        "mean_dist_candidate_to_network_km": mean_dist_network,
        "max_dist_candidate_to_network_km": max_dist_network,
        "is_same_city_as_current_mule": is_same_city_mule,
        "is_same_city_as_victim": is_same_city_victim,
    }


if __name__ == "__main__":
    from ml.data_loader import load_raw_data
    _, _, _, locs, _ = load_raw_data()
    coords = locs.set_index("city")[["latitude", "longitude"]].to_dict(orient="index")
    sample_candidate = locs.iloc[0].to_dict()
    geo = extract_geo_features(sample_candidate, "Kochi", ["Kochi", "Hyderabad", "Chennai"], coords)
    print("[STEP 3 - GEO SUCCESS] Geo features for L001 (Bengaluru):", geo)
