#!/usr/bin/env python3
"""Script to add sample data to the AirPuff database."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.airport import Airport
from app.models.weather import WeatherObservation
from app.models.user import User
from app.models.route import Route, RouteAirport
from datetime import datetime, timezone
import random

def add_sample_data():
    """Add sample airports, weather data, and routes."""
    db = SessionLocal()
    
    try:
        # Create a sample user
        user = User(
            email="test@airpuff.com",
            name="Test User",
            provider="test",
            provider_id="test123",
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user.email}")
        
        # Sample airports
        airports_data = [
            {
                "icao": "KSFO",
                "name": "San Francisco International Airport",
                "latitude": 37.6213,
                "longitude": -122.3790,
                "elevation_ft": 13,
                "atis_phone": "650-821-7731",
                "tower_phone": "650-821-7732",
                "city": "San Francisco",
                "state": "CA",
                "country": "USA"
            },
            {
                "icao": "KLAX",
                "name": "Los Angeles International Airport",
                "latitude": 33.9425,
                "longitude": -118.4081,
                "elevation_ft": 125,
                "atis_phone": "310-646-5252",
                "tower_phone": "310-646-5253",
                "city": "Los Angeles",
                "state": "CA",
                "country": "USA"
            },
            {
                "icao": "KJFK",
                "name": "John F. Kennedy International Airport",
                "latitude": 40.6413,
                "longitude": -73.7781,
                "elevation_ft": 13,
                "atis_phone": "718-244-4444",
                "tower_phone": "718-244-4445",
                "city": "New York",
                "state": "NY",
                "country": "USA"
            },
            {
                "icao": "KORD",
                "name": "Chicago O'Hare International Airport",
                "latitude": 41.9786,
                "longitude": -87.9048,
                "elevation_ft": 672,
                "atis_phone": "773-686-2200",
                "tower_phone": "773-686-2201",
                "city": "Chicago",
                "state": "IL",
                "country": "USA"
            },
            {
                "icao": "KDFW",
                "name": "Dallas/Fort Worth International Airport",
                "latitude": 32.8968,
                "longitude": -97.0380,
                "elevation_ft": 607,
                "atis_phone": "972-574-6000",
                "tower_phone": "972-574-6001",
                "city": "Dallas",
                "state": "TX",
                "country": "USA"
            }
        ]
        
        # Add airports
        airports = []
        for airport_data in airports_data:
            airport = Airport(**airport_data)
            db.add(airport)
            airports.append(airport)
        
        db.commit()
        print(f"Created {len(airports)} airports")
        
        # Add sample weather observations
        weather_categories = ["VFR", "MVFR", "IFR", "LIFR"]
        for airport in airports:
            for i in range(5):  # 5 observations per airport
                weather = WeatherObservation(
                    airport_id=airport.id,
                    time=datetime.now(timezone.utc).replace(hour=datetime.now().hour - i),
                    flight_category=random.choice(weather_categories),
                    temperature_f=random.randint(20, 80),
                    temperature_c=round((random.randint(20, 80) - 32) * 5/9, 1),
                    dewpoint_f=random.randint(10, 60),
                    dewpoint_c=round((random.randint(10, 60) - 32) * 5/9, 1),
                    wind_dir_deg=random.randint(0, 360),
                    wind_speed_kts=random.randint(5, 25),
                    wind_speed_mph=random.randint(6, 29),
                    visibility_mi=round(random.uniform(1.0, 10.0), 1),
                    visibility_m=round(random.uniform(1609, 16093), 0),
                    ceiling_ft=random.randint(1000, 10000),
                    ceiling_code=random.choice(["FEW", "SCT", "BKN", "OVC"]),
                    altimeter_hg=round(random.uniform(29.80, 30.20), 2),
                    altimeter_mb=round(random.uniform(1008, 1023), 1),
                    raw_metar=f"{airport.icao} {datetime.now().strftime('%d%H%M')}Z AUTO {random.randint(0, 360):03d}{random.randint(5, 25):02d}KT {random.uniform(1.0, 10.0):.0f}SM {random.choice(['FEW', 'SCT', 'BKN', 'OVC'])}{random.randint(1000, 10000):04d} A{random.randint(2980, 3020):04d}",
                    metar_type="METAR",
                    auto_station="AUTO"
                )
                db.add(weather)
        
        db.commit()
        print(f"Created weather observations for all airports")
        
        # Create sample routes
        route1 = Route(
            name="West Coast Commute",
            description="Regular flight route along the west coast",
            user_id=user.id,
            is_public=True,
            is_favorite=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(route1)
        db.commit()
        db.refresh(route1)
        
        # Add airports to route
        route_airports_data = [
            (airports[0].id, 0),  # KSFO
            (airports[1].id, 1),  # KLAX
        ]
        
        for airport_id, order in route_airports_data:
            route_airport = RouteAirport(
                route_id=route1.id,
                airport_id=airport_id,
                order=order,
                is_waypoint=False
            )
            db.add(route_airport)
        
        # Create second route
        route2 = Route(
            name="Cross Country",
            description="Transcontinental flight route",
            user_id=user.id,
            is_public=False,
            is_favorite=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(route2)
        db.commit()
        db.refresh(route2)
        
        # Add airports to second route
        route_airports_data2 = [
            (airports[0].id, 0),  # KSFO
            (airports[2].id, 1),  # KJFK
            (airports[3].id, 2),  # KORD
        ]
        
        for airport_id, order in route_airports_data2:
            route_airport = RouteAirport(
                route_id=route2.id,
                airport_id=airport_id,
                order=order,
                is_waypoint=False
            )
            db.add(route_airport)
        
        db.commit()
        print(f"Created 2 sample routes")
        
        print("\n✅ Sample data added successfully!")
        print(f"   - 1 user")
        print(f"   - {len(airports)} airports")
        print(f"   - Weather observations for all airports")
        print(f"   - 2 routes")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_sample_data()
