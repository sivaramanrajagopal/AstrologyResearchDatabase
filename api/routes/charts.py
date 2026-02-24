"""
Chart endpoints: D1 (Rasi) and D10 (Dasamsa).
"""
from datetime import date, time, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/charts", tags=["charts"])


class BirthDataRequest(BaseModel):
    """Birth data for chart calculation."""
    dob: str = Field(..., description="Date of birth YYYY-MM-DD")
    tob: str = Field(..., description="Time of birth HH:MM or HH:MM:SS")
    place: Optional[str] = Field(None, description="Place of birth (for geocoding)")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    timezone_name: Optional[str] = Field(None, description="e.g. Asia/Kolkata")


def _parse_birth_data(req: BirthDataRequest) -> tuple:
    """Parse request into date, time, lat, lon, timezone. Resolve place if needed."""
    dob = datetime.strptime(req.dob, "%Y-%m-%d").date()
    tob_str = req.tob.strip()
    if len(tob_str) == 5:
        tot = datetime.strptime(tob_str, "%H:%M").time()
    else:
        tot = datetime.strptime(tob_str, "%H:%M:%S").time()

    lat, lon, tz_name = req.latitude, req.longitude, req.timezone_name
    if req.place and (lat is None or lon is None or not tz_name):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from utils.geocoding import get_location_details
        details = get_location_details(req.place)
        if not details:
            raise HTTPException(status_code=400, detail="Could not geocode place")
        lat = details["latitude"]
        lon = details["longitude"]
        tz_name = details.get("timezone_id") or "UTC"
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Provide place or latitude, longitude (and timezone_name)")
    if not tz_name:
        tz_name = "UTC"
    return dob, tot, float(lat), float(lon), tz_name


@router.post("/d1")
def charts_d1(req: BirthDataRequest):
    """
    Calculate D1 (Rasi) chart using Swiss Ephemeris (Lahiri sidereal).
    Returns full planetary positions, houses, yogas, Shadbala, aspects.
    """
    import sys
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if root not in sys.path:
        sys.path.insert(0, root)
    from api.cache import cache_get, cache_set, cache_key_d1

    dob, tot, lat, lon, tz_name = _parse_birth_data(req)
    tob_str = req.tob.strip()[:5] if len(req.tob.strip()) >= 5 else req.tob.strip()
    cache_key = cache_key_d1(None, dob.isoformat(), tob_str, lat, lon)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    from enhanced_swiss_ephemeris import calculate_enhanced_planetary_positions

    result = calculate_enhanced_planetary_positions(
        date_of_birth=dob,
        time_of_birth=tot,
        latitude=lat,
        longitude=lon,
        timezone_name=tz_name,
    )
    if not result:
        raise HTTPException(status_code=500, detail="D1 calculation failed")
    cache_set(cache_key, result)
    return result


@router.post("/d10")
def charts_d10(req: BirthDataRequest):
    """
    Calculate D10 (Dasamsa) chart. Computes D1 first then applies Parasara D10 mapping.
    Returns D10 planetary positions and house cusps.
    """
    import sys
    import os
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if root not in sys.path:
        sys.path.insert(0, root)
    from api.cache import cache_get, cache_set, cache_key_d10
    from enhanced_swiss_ephemeris import calculate_enhanced_planetary_positions
    from services.d10_dasamsa import calculate_d10_chart

    dob, tot, lat, lon, tz_name = _parse_birth_data(req)
    tob_str = req.tob.strip()[:5] if len(req.tob.strip()) >= 5 else req.tob.strip()
    cache_key = cache_key_d10(None, dob.isoformat(), tob_str, lat, lon)
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    d1 = calculate_enhanced_planetary_positions(
        date_of_birth=dob,
        time_of_birth=tot,
        latitude=lat,
        longitude=lon,
        timezone_name=tz_name,
    )
    if not d1:
        raise HTTPException(status_code=500, detail="D1 calculation failed (required for D10)")
    d10 = calculate_d10_chart(d1)
    out = {"d1_metadata": d1.get("_metadata"), "d10": d10}
    cache_set(cache_key, out)
    return out


# South Indian chart: rasi names (0=Mesha .. 11=Meena)
RASIS_SI = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
]

# D1 fixed-sign grid: 4x4 with 2x2 center. Each cell = fixed rasi; planets by sign; Lagna marked in Ascendant's cell.
# STANDARD South Indian fixed-sign layout (traditional Rasi chart)
# Row 0: Meena(11), Mesha(0), Rishaba(1), Mithuna(2)
# Row 1: Kumbha(10), CENTER, CENTER, Kataka(3)
# Row 2: Makara(9), CENTER, CENTER, Simha(4)
# Row 3: Dhanus(8), Vrischika(7), Thula(6), Kanni(5)
# -1 = center, 0-11 = rasi index
D1_FIXED_SIGN_GRID = [
    11, 0, 1, 2,     # Meena, Mesha, Rishaba, Mithuna
    10, -1, -1, 3,   # Kumbha, center, center, Kataka
    9, -1, -1, 4,    # Makara, center, center, Simha
    8, 7, 6, 5,      # Dhanus, Vrischika, Thula, Kanni
]

# Grid layout: 4 rows x 4 columns. Lagna = House 1 at left side, row 1, col 0.
# Traditional South Indian chart layout with 2x2 center and houses around perimeter:
# Row 0: H12, H11, H10, H9
# Row 1: H1 (Lagna), Center (2x2), Center, H8
# Row 2: H2, Center, Center, H7
# Row 3: H3, H4, H5, H6
SOUTH_INDIAN_GRID = [
    12, 11, 10, 9,     # row 0: H12, H11, H10, H9
    1, -1, -1, 8,      # row 1: H1 (Lagna), center, center, H8
    2, -1, -1, 7,      # row 2: H2, center, center, H7
    3, 4, 5, 6,        # row 3: H3, H4, H5, H6
]


def _d1_to_south_indian_fixed_sign(d1: dict) -> tuple:
    """
    D1 chart in South Indian fixed-sign layout.
    4x4 grid: fixed rasi in each cell (Makara, Dhanus, Vrischika, Thula, Kumbha, Kanni, Meena, Simha, Mesha, Rishaba, Mithuna, Kataka).
    Planets placed by sign (longitude // 30). Lagna (ல) marked in Ascendant's sign cell.
    Returns (grid_cells, lagna_rasi). grid_cells has 16 items: 12 sign cells + 4 center cells (2x2).
    """
    if not d1 or not isinstance(d1, dict):
        d1 = {}
    asc = d1.get("Ascendant") if isinstance(d1.get("Ascendant"), dict) else None
    lagna_index = 0
    lagna_rasi = RASIS_SI[0]
    if asc and "longitude" in asc:
        try:
            lagna_index = int(float(asc["longitude"]) % 360 // 30) % 12
            lagna_rasi = asc.get("rasi") or RASIS_SI[lagna_index]
        except (TypeError, ValueError):
            pass
    elif asc and asc.get("rasi"):
        for i, name in enumerate(RASIS_SI):
            if name == asc.get("rasi"):
                lagna_index = i
                lagna_rasi = name
                break

    cells_by_rasi = [{"rasi": RASIS_SI[i], "rasi_index": i, "planets": [], "is_lagna": (i == lagna_index)} for i in range(12)]
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        try:
            lon = float(pdata["longitude"]) % 360
        except (TypeError, ValueError):
            continue
        rasi_index = int(lon // 30) % 12
        cells_by_rasi[rasi_index]["planets"].append({
            "name": pname,
            "retro": bool(pdata.get("retrograde", False)),
        })

    grid_cells = []
    for slot in D1_FIXED_SIGN_GRID:
        if slot == -1:
            grid_cells.append({"type": "center"})
        elif slot == -2:
            grid_cells.append({"type": "empty"})
        else:
            c = cells_by_rasi[slot]
            grid_cells.append({
                "type": "house",
                "rasi": c["rasi"],
                "rasi_index": c["rasi_index"],
                "planets": c["planets"],
                "is_lagna": c["is_lagna"],
            })
    return grid_cells, lagna_rasi


def _chart_to_south_indian_houses(chart: dict) -> tuple:
    """
    Build South Indian chart: 12 houses (equal house from Lagna), Lagna = House 1.
    Returns (grid_cells, lagna_rasi). grid_cells is 16 items for 4x4 grid: house cells, center (2x2).
    Each house has: number, rasi, planets, is_lagna. Planets placed by sign (rasi) in that house.
    Handles empty chart or missing Ascendant by using first planet or House_1.
    """
    if not chart or not isinstance(chart, dict):
        chart = {}
    asc = None
    for k in ("Ascendant", "ascendant"):
        if chart.get(k) and isinstance(chart[k], dict):
            asc = chart[k]
            break
    lagna_index = 0
    lagna_rasi = RASIS_SI[0]
    if asc and "longitude" in asc:
        try:
            lagna_index = int(float(asc["longitude"]) % 360 // 30) % 12
            lagna_rasi = asc.get("rasi") or RASIS_SI[lagna_index]
        except (TypeError, ValueError):
            pass
    elif asc and asc.get("rasi"):
        r = asc.get("rasi")
        for i, name in enumerate(RASIS_SI):
            if name == r:
                lagna_index = i
                lagna_rasi = name
                break
    else:
        for pname, pdata in chart.items():
            if pname.startswith("_"):
                continue
            if isinstance(pdata, dict) and "longitude" in pdata:
                try:
                    lagna_index = int(float(pdata["longitude"]) % 360 // 30) % 12
                    lagna_rasi = pdata.get("rasi") or RASIS_SI[lagna_index]
                except (TypeError, ValueError):
                    pass
                break
        else:
            enh = chart.get("_enhanced") or {}
            houses_enh = enh.get("houses") or {}
            h1 = houses_enh.get("House_1")
            if isinstance(h1, dict) and "longitude" in h1:
                try:
                    lagna_index = int(float(h1["longitude"]) % 360 // 30) % 12
                    lagna_rasi = h1.get("rasi") or RASIS_SI[lagna_index]
                except (TypeError, ValueError):
                    pass

    houses = []
    for n in range(1, 13):
        rasi_idx = (lagna_index + (n - 1)) % 12
        houses.append({
            "number": n,
            "rasi": RASIS_SI[rasi_idx],
            "rasi_index": rasi_idx,
            "planets": [],
            "is_lagna": (n == 1),
        })

    for pname, pdata in chart.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        try:
            lon = float(pdata["longitude"]) % 360
        except (TypeError, ValueError):
            continue
        rasi_index = int(lon // 30) % 12
        for h in houses:
            if h["rasi_index"] == rasi_index:
                h["planets"].append({
                    "name": pname,
                    "retro": bool(pdata.get("retrograde", False)),
                })
                break

    grid_cells = []
    for slot in SOUTH_INDIAN_GRID:
        if slot == -1:
            grid_cells.append({"type": "center"})
        elif slot == -2:
            grid_cells.append({"type": "empty"})
        else:
            grid_cells.append({"type": "house", **houses[slot - 1]})
    return grid_cells, lagna_rasi


def _d1_to_south_indian_houses(d1: dict) -> tuple:
    """Alias for backward compatibility."""
    return _chart_to_south_indian_houses(d1)


@router.get("/d1/south-indian")
def charts_d1_south_indian(chart_id: int):
    """
    Render D1 chart in South Indian style (HTML). Requires chart_id from Supabase.
    """
    import os
    import sys
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if root not in sys.path:
        sys.path.insert(0, root)
    from supabase_config import supabase_manager
    from fastapi.responses import HTMLResponse

    if not supabase_manager:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    row = supabase_manager.get_birth_chart(chart_id)
    if not row:
        raise HTTPException(status_code=404, detail="Chart not found")
    # Build D1 dict from row
    d1 = {}
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]:
        key = p.lower()
        lon = row.get(f"{key}_longitude")
        if lon is None:
            continue
        rasi = row.get(f"{key}_rasi") or ""
        d1[p] = {"longitude": float(lon), "retrograde": row.get(f"{key}_retrograde") or False, "rasi": rasi}
    houses_data = {}
    for i in range(1, 13):
        lon = row.get(f"house_{i}_longitude")
        if lon is not None:
            rasis = [
                "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
                "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
            ]
            houses_data[f"House_{i}"] = {"longitude": float(lon), "rasi": rasis[int(lon // 30) % 12]}
    if houses_data:
        d1["_enhanced"] = {"houses": houses_data}
    houses, lagna_rasi = _chart_to_south_indian_houses(d1)
    lagna_rasi = lagna_rasi or row.get("ascendant_rasi") or ""
    for c in houses:
        if c.get("type") == "center":
            c["title"] = "ராசி [D1]"
            break
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(os.path.join(root, "api", "templates")))
    tpl = env.get_template("d1_south_indian.html")
    html = tpl.render(
        name=row.get("name"),
        dob=row.get("date_of_birth"),
        tob=row.get("time_of_birth"),
        houses=houses,
        lagna_rasi=lagna_rasi,
    )
    return HTMLResponse(html)


@router.get("/interpretation/{chart_id}")
def charts_interpretation(chart_id: int):
    """
    Full interpretation: D1, D9, D10 South Indian style + rules table (✓/✗) + rules score + profession suggestion.
    Same format as the prediction rules applied to the native.
    """
    import os
    import sys
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if root not in sys.path:
        sys.path.insert(0, root)
    from supabase_config import supabase_manager
    from fastapi.responses import HTMLResponse
    from services.d10_dasamsa import calculate_d10_chart
    from services.d9_navamsha import calculate_d9_chart
    from services.career_rules import career_rules
    from api.routes.career import _get_d1_from_db

    if not supabase_manager:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    row = supabase_manager.get_birth_chart(chart_id)
    if not row:
        raise HTTPException(status_code=404, detail="Chart not found")
    d1 = _get_d1_from_db(chart_id)
    d9 = calculate_d9_chart(d1)
    d10 = calculate_d10_chart(d1)

    # Calculate Dasha (planetary periods) for timing analysis
    dasha_current = None
    try:
        from services.dasha_service import calculate_current_dasha

        birth_date = row["date_of_birth"]
        birth_time = row["time_of_birth"][:5] if isinstance(row["time_of_birth"], str) else "12:00"

        dasha_current = calculate_current_dasha(d1, birth_date, birth_time)
    except Exception as e:
        # Log but don't fail
        print(f"Dasha calculation failed: {e}")
        dasha_current = None

    # Calculate Ashtakavarga (BAV/SAV) for strength analysis using local calculator
    bav_sav_full = None
    try:
        from services.ashtakavarga_service import calculate_ashtakavarga_full

        # Calculate Ashtakavarga from D1 chart data
        ashtakavarga_data = calculate_ashtakavarga_full(d1)

        if ashtakavarga_data:
            # Transform to format expected by career_rules
            bav_sav_full = {
                "sav_chart": ashtakavarga_data['sav']['chart'],
                "sav_total": ashtakavarga_data['sav']['total'],
                "bav": ashtakavarga_data['bav'],
            }
    except Exception as e:
        print(f"Error calculating Ashtakavarga: {e}")
        bav_sav_full = None

    result = career_rules(d1, d10, dasha_current=dasha_current, bav_sav_full=bav_sav_full)
    # Use fixed-sign chart layout (signs don't rotate, Lagna marker shows ascendant)
    houses_d1, lagna_rasi_d1 = _d1_to_south_indian_fixed_sign(d1)
    houses_d9, lagna_rasi_d9 = _d1_to_south_indian_fixed_sign(d9)
    houses_d10, lagna_rasi_d10 = _d1_to_south_indian_fixed_sign(d10)
    for c in houses_d1:
        if c.get("type") == "center":
            c["title"] = "ராசி [D1]"
            break
    for c in houses_d9:
        if c.get("type") == "center":
            c["title"] = "நவாம்சம் [D9]"
            break
    for c in houses_d10:
        if c.get("type") == "center":
            c["title"] = "தசாம்சம் [D10]"
            break
    rules_checklist = result.get("rules_checklist", [])
    rules_score = result.get("rules_score", "0/0")

    # Group rules by category for better organization
    try:
        from services.rule_categories import group_rules_by_category
        rules_grouped = group_rules_by_category(rules_checklist)
    except Exception:
        rules_grouped = []
    profession_suggestion = []
    profession_probabilities = []

    # Use V2 profession predictor for accurate profession suggestions
    try:
        from services.profession_predictor_v2 import get_profession_summary_v2
        profession_summary = get_profession_summary_v2(row)
        if profession_summary and 'top_professions' in profession_summary:
            # Get top 5 professions with probabilities
            profession_probabilities = profession_summary['top_professions'][:5]
            profession_suggestion = [p['name'] for p in profession_probabilities]
    except Exception as e:
        # Fallback to old engine if V2 fails
        try:
            from services.rules_engine import ParasaraRulesEngine
            engine = ParasaraRulesEngine()
            ranked = engine.apply_all_rules(d1, d10, {})
            profession_suggestion = [c[0] for c in ranked[:8]] if ranked else []
        except Exception:
            pass
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(os.path.join(root, "api", "templates")))
    tpl = env.get_template("interpretation.html")
    html = tpl.render(
        name=row.get("name"),
        dob=row.get("date_of_birth"),
        tob=row.get("time_of_birth"),
        place=row.get("place_of_birth"),
        houses_d1=houses_d1,
        houses_d9=houses_d9,
        houses_d10=houses_d10,
        lagna_rasi_d1=lagna_rasi_d1 or "",
        lagna_rasi_d9=lagna_rasi_d9 or "",
        lagna_rasi_d10=lagna_rasi_d10 or "",
        rules_checklist=rules_checklist,
        rules_grouped=rules_grouped,
        rules_score=rules_score,
        career_strength=result.get("career_strength", ""),
        profession_suggestion=profession_suggestion,
        profession_probabilities=profession_probabilities,
        chart_summary=result.get("chart_summary", {}),
    )
    return HTMLResponse(html)
