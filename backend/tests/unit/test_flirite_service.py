from app.services.flirite_service import parse_fli_rite_response, parse_metar_data


def test_parse_metar_data_normalizes_weather_payload():
    payload = {
        "icao": "KSFO",
        "observed": "2026-06-26T12:00:00Z",
        "temperature": {"celsius": 20.0, "fahrenheit": 68.0},
        "dewpoint": {"celsius": 15.0, "fahrenheit": 59.0},
        "wind": {"degrees": 270, "speed_kts": 10, "speed_mph": 11},
        "visibility": {"miles": 10.0, "meters": 16093},
        "ceiling": {"feet_agl": 12000, "code": "CLR"},
        "barometer": {"hg": 29.92, "mb": 1013.2},
        "flight_category": "VFR",
        "raw_text": "KSFO 261200Z 27010KT 10SM CLR 20/15 A2992",
    }

    parsed = parse_metar_data(payload)

    assert parsed is not None
    assert parsed["icao"] == "KSFO"
    assert parsed["flight_category"] == "VFR"
    assert parsed["temperature_f"] == 68.0
    assert parsed["wind_speed_kts"] == 10
    assert parsed["raw_metar"] == payload["raw_text"]


def test_parse_fli_rite_response_accepts_flat_or_wrapped_payloads():
    payload = {
        "data": [
            {"icao": "KSFO", "observed": "2026-06-26T12:00:00Z", "flight_category": "VFR"},
            {"icao": "KLAX", "observed": "2026-06-26T12:05:00Z", "flight_category": "MVFR"},
        ]
    }

    parsed = parse_fli_rite_response(payload)

    assert len(parsed) == 2
    assert parsed[0]["icao"] == "KSFO"
    assert parsed[1]["icao"] == "KLAX"
