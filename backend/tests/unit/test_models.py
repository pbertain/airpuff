# Unit Tests for AirPuff Models

import pytest
from datetime import datetime
from app.models.airport import Airport
from app.models.weather import WeatherObservation
from app.models.user import User

class TestAirportModel:
    """Test cases for Airport model."""
    
    def test_airport_creation(self, sample_airport):
        """Test creating an airport with valid data."""
        airport = Airport(**sample_airport)
        assert airport.icao == "KSFO"
        assert airport.name == "San Francisco International Airport"
        assert airport.city == "San Francisco"
        assert airport.state == "CA"
        assert airport.country == "USA"
        assert airport.latitude == 37.6213
        assert airport.longitude == -122.3790
        assert airport.elevation_ft == 13
    
    def test_airport_icao_validation(self):
        """Test ICAO code validation."""
        # Valid ICAO code
        airport = Airport(icao="KSFO", name="Test Airport", city="Test", state="CA", country="USA")
        assert airport.icao == "KSFO"
        
        # Invalid ICAO code (too short)
        with pytest.raises(ValueError):
            Airport(icao="KSF", name="Test Airport", city="Test", state="CA", country="USA")
        
        # Invalid ICAO code (too long)
        with pytest.raises(ValueError):
            Airport(icao="KSFOO", name="Test Airport", city="Test", state="CA", country="USA")
    
    def test_airport_coordinates_validation(self):
        """Test coordinate validation."""
        # Valid coordinates
        airport = Airport(
            icao="KSFO", 
            name="Test Airport", 
            city="Test", 
            state="CA", 
            country="USA",
            latitude=37.6213,
            longitude=-122.3790
        )
        assert airport.latitude == 37.6213
        assert airport.longitude == -122.3790
        
        # Invalid latitude (out of range)
        with pytest.raises(ValueError):
            Airport(
                icao="KSFO", 
                name="Test Airport", 
                city="Test", 
                state="CA", 
                country="USA",
                latitude=91.0,  # Invalid latitude
                longitude=-122.3790
            )
        
        # Invalid longitude (out of range)
        with pytest.raises(ValueError):
            Airport(
                icao="KSFO", 
                name="Test Airport", 
                city="Test", 
                state="CA", 
                country="USA",
                latitude=37.6213,
                longitude=181.0  # Invalid longitude
            )

class TestWeatherObservationModel:
    """Test cases for WeatherObservation model."""
    
    def test_weather_observation_creation(self, sample_weather):
        """Test creating a weather observation with valid data."""
        weather = WeatherObservation(**sample_weather)
        assert weather.airport_id == 1
        assert weather.flight_category == "VFR"
        assert weather.temperature_c == 20.0
        assert weather.dewpoint_c == 15.0
        assert weather.wind_dir_deg == 270
        assert weather.wind_speed_kts == 10
        assert weather.visibility_mi == 10.0
        assert weather.altimeter_hg == 29.92
        assert weather.ceiling_code == "CLR"
        assert weather.raw_metar == "KSFO 011200Z 27010KT 10SM CLR 20/15 A2992"
    
    def test_flight_category_validation(self):
        """Test flight category validation."""
        valid_categories = ["VFR", "MVFR", "IFR", "LIFR"]
        
        for category in valid_categories:
            weather = WeatherObservation(
                airport_id=1,
                time=datetime.now(),
                flight_category=category,
                temperature_c=20.0,
                dewpoint_c=15.0,
                wind_dir_deg=270,
                wind_speed_kts=10,
                visibility_mi=10.0,
                altimeter_hg=29.92,
                ceiling_code="CLR",
                raw_metar="TEST METAR"
            )
            assert weather.flight_category == category
        
        # Invalid flight category
        with pytest.raises(ValueError):
            WeatherObservation(
                airport_id=1,
                time=datetime.now(),
                flight_category="INVALID",
                temperature_c=20.0,
                dewpoint_c=15.0,
                wind_dir_deg=270,
                wind_speed_kts=10,
                visibility_mi=10.0,
                altimeter_hg=29.92,
                ceiling_code="CLR",
                raw_metar="TEST METAR"
            )
    
    def test_temperature_validation(self):
        """Test temperature validation."""
        # Valid temperature
        weather = WeatherObservation(
            airport_id=1,
            time=datetime.now(),
            flight_category="VFR",
            temperature_c=20.0,
            dewpoint_c=15.0,
            wind_dir_deg=270,
            wind_speed_kts=10,
            visibility_mi=10.0,
            altimeter_hg=29.92,
            ceiling_code="CLR",
            raw_metar="TEST METAR"
        )
        assert weather.temperature_c == 20.0
        
        # Invalid temperature (too cold)
        with pytest.raises(ValueError):
            WeatherObservation(
                airport_id=1,
                time=datetime.now(),
                flight_category="VFR",
                temperature_c=-100.0,  # Too cold
                dewpoint_c=15.0,
                wind_dir_deg=270,
                wind_speed_kts=10,
                visibility_mi=10.0,
                altimeter_hg=29.92,
                ceiling_code="CLR",
                raw_metar="TEST METAR"
            )
        
        # Invalid temperature (too hot)
        with pytest.raises(ValueError):
            WeatherObservation(
                airport_id=1,
                time=datetime.now(),
                flight_category="VFR",
                temperature_c=100.0,  # Too hot
                dewpoint_c=15.0,
                wind_dir_deg=270,
                wind_speed_kts=10,
                visibility_mi=10.0,
                altimeter_hg=29.92,
                ceiling_code="CLR",
                raw_metar="TEST METAR"
            )

class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, sample_user):
        """Test creating a user with valid data."""
        user = User(**sample_user)
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active == True
    
    def test_email_validation(self):
        """Test email validation."""
        # Valid email
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True
        )
        assert user.email == "test@example.com"
        
        # Invalid email format
        with pytest.raises(ValueError):
            User(
                email="invalid-email",
                username="testuser",
                full_name="Test User",
                is_active=True
            )
        
        # Empty email
        with pytest.raises(ValueError):
            User(
                email="",
                username="testuser",
                full_name="Test User",
                is_active=True
            )
    
    def test_username_validation(self):
        """Test username validation."""
        # Valid username
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True
        )
        assert user.username == "testuser"
        
        # Username too short
        with pytest.raises(ValueError):
            User(
                email="test@example.com",
                username="ab",  # Too short
                full_name="Test User",
                is_active=True
            )
        
        # Username too long
        with pytest.raises(ValueError):
            User(
                email="test@example.com",
                username="a" * 51,  # Too long
                full_name="Test User",
                is_active=True
            )
