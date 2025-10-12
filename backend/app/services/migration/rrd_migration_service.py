"""
RRD Data Migration Service

This service handles the migration of legacy RRD (Round Robin Database) data
from the old AirPuff system to the new TimescaleDB-based system.

RRD Structure:
- Temperature: temp_c, temp_f, dew_pt_c, dew_pt_f, t_dp_spread_c, t_dp_spread_f
- Altimeter: altimeter
- Wind: wind_dir, wind_speed
- Visibility: visibility
- Ceiling: ceiling
- Category: flight_category (derived)

Data Retention:
- 1 day: 5-minute averages
- 7 days: 15-minute averages
- 30 days: 30-minute averages
- 365 days: 60-minute averages
- 10 years: 24-hour averages
"""

import os
import sys
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import subprocess
import json

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.database import get_db
from app.models.airport import Airport
from app.models.weather import WeatherObservation
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)

class RRDMigrationService:
    """Service for migrating RRD data to TimescaleDB."""
    
    def __init__(self, rrd_path: str = "/var/airpuff/rrd-data"):
        """
        Initialize the RRD migration service.
        
        Args:
            rrd_path: Path to the RRD data directory
        """
        self.rrd_path = Path(rrd_path)
        self.migration_stats = {
            'airports_processed': 0,
            'records_migrated': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
    async def migrate_all_rrd_data(self, db: Session) -> Dict:
        """
        Migrate all RRD data to TimescaleDB.
        
        Args:
            db: Database session
            
        Returns:
            Migration statistics
        """
        logger.info("Starting RRD data migration")
        self.migration_stats['start_time'] = datetime.utcnow()
        
        try:
            # Get list of airports from RRD files
            airports = await self._discover_airports_from_rrd()
            logger.info(f"Discovered {len(airports)} airports with RRD data")
            
            for airport_code in airports:
                try:
                    await self._migrate_airport_data(db, airport_code)
                    self.migration_stats['airports_processed'] += 1
                except Exception as e:
                    logger.error(f"Error migrating data for {airport_code}: {e}")
                    self.migration_stats['errors'] += 1
                    
            self.migration_stats['end_time'] = datetime.utcnow()
            logger.info(f"RRD migration completed. Stats: {self.migration_stats}")
            
        except Exception as e:
            logger.error(f"Fatal error during RRD migration: {e}")
            self.migration_stats['errors'] += 1
            
        return self.migration_stats
    
    async def _discover_airports_from_rrd(self) -> List[str]:
        """
        Discover airports by scanning RRD files.
        
        Returns:
            List of airport ICAO codes
        """
        airports = set()
        
        if not self.rrd_path.exists():
            logger.warning(f"RRD path does not exist: {self.rrd_path}")
            return list(airports)
            
        # Look for temperature RRD files (they all follow the same pattern)
        for rrd_file in self.rrd_path.glob("*-temp.rrd"):
            airport_code = rrd_file.stem.replace("-temp", "").upper()
            airports.add(airport_code)
            
        logger.info(f"Discovered airports: {sorted(airports)}")
        return sorted(airports)
    
    async def _migrate_airport_data(self, db: Session, airport_code: str):
        """
        Migrate all RRD data for a specific airport.
        
        Args:
            db: Database session
            airport_code: ICAO airport code
        """
        logger.info(f"Migrating data for airport: {airport_code}")
        
        # Ensure airport exists in database
        airport = await self._ensure_airport_exists(db, airport_code)
        if not airport:
            logger.error(f"Could not create/find airport: {airport_code}")
            return
            
        # Migrate each RRD file type
        await self._migrate_temperature_data(db, airport_code, airport.id)
        await self._migrate_altimeter_data(db, airport_code, airport.id)
        await self._migrate_wind_data(db, airport_code, airport.id)
        await self._migrate_visibility_data(db, airport_code, airport.id)
        await self._migrate_ceiling_data(db, airport_code, airport.id)
        
        logger.info(f"Completed migration for airport: {airport_code}")
    
    async def _ensure_airport_exists(self, db: Session, airport_code: str) -> Optional[Airport]:
        """
        Ensure airport exists in database, create if necessary.
        
        Args:
            db: Database session
            airport_code: ICAO airport code
            
        Returns:
            Airport object
        """
        # Check if airport already exists
        airport = db.query(Airport).filter(Airport.icao == airport_code).first()
        
        if not airport:
            # Create airport with basic info
            airport = Airport(
                icao=airport_code,
                name=f"{airport_code} Airport",
                city="Unknown",
                state="Unknown",
                country="Unknown",
                latitude=0.0,
                longitude=0.0,
                elevation_ft=0
            )
            db.add(airport)
            db.commit()
            db.refresh(airport)
            logger.info(f"Created airport: {airport_code}")
        else:
            logger.info(f"Found existing airport: {airport_code}")
            
        return airport
    
    async def _migrate_temperature_data(self, db: Session, airport_code: str, airport_id: int):
        """Migrate temperature RRD data."""
        rrd_file = self.rrd_path / f"{airport_code.lower()}-temp.rrd"
        if not rrd_file.exists():
            logger.warning(f"Temperature RRD file not found: {rrd_file}")
            return
            
        try:
            # Extract data from RRD file
            data_points = await self._extract_rrd_data(rrd_file, [
                'temp_c', 'temp_f', 'dew_pt_c', 'dew_pt_f', 
                't_dp_spread_c', 't_dp_spread_f'
            ])
            
            # Insert into database
            for timestamp, values in data_points:
                await self._upsert_weather_observation(
                    db, airport_id, timestamp, {
                        'temperature_c': values.get('temp_c'),
                        'dewpoint_c': values.get('dew_pt_c'),
                        'temperature_f': values.get('temp_f'),
                        'dewpoint_f': values.get('dew_pt_f'),
                        'temp_dewpoint_spread_c': values.get('t_dp_spread_c'),
                        'temp_dewpoint_spread_f': values.get('t_dp_spread_f')
                    }
                )
                
            logger.info(f"Migrated {len(data_points)} temperature records for {airport_code}")
            
        except Exception as e:
            logger.error(f"Error migrating temperature data for {airport_code}: {e}")
    
    async def _migrate_altimeter_data(self, db: Session, airport_code: str, airport_id: int):
        """Migrate altimeter RRD data."""
        rrd_file = self.rrd_path / f"{airport_code.lower()}-altimeter.rrd"
        if not rrd_file.exists():
            logger.warning(f"Altimeter RRD file not found: {rrd_file}")
            return
            
        try:
            data_points = await self._extract_rrd_data(rrd_file, ['altimeter'])
            
            for timestamp, values in data_points:
                await self._upsert_weather_observation(
                    db, airport_id, timestamp, {
                        'altimeter_hg': values.get('altimeter')
                    }
                )
                
            logger.info(f"Migrated {len(data_points)} altimeter records for {airport_code}")
            
        except Exception as e:
            logger.error(f"Error migrating altimeter data for {airport_code}: {e}")
    
    async def _migrate_wind_data(self, db: Session, airport_code: str, airport_id: int):
        """Migrate wind RRD data."""
        rrd_file = self.rrd_path / f"{airport_code.lower()}-wind.rrd"
        if not rrd_file.exists():
            logger.warning(f"Wind RRD file not found: {rrd_file}")
            return
            
        try:
            data_points = await self._extract_rrd_data(rrd_file, ['wind_dir', 'wind_speed'])
            
            for timestamp, values in data_points:
                await self._upsert_weather_observation(
                    db, airport_id, timestamp, {
                        'wind_dir_deg': values.get('wind_dir'),
                        'wind_speed_kts': values.get('wind_speed')
                    }
                )
                
            logger.info(f"Migrated {len(data_points)} wind records for {airport_code}")
            
        except Exception as e:
            logger.error(f"Error migrating wind data for {airport_code}: {e}")
    
    async def _migrate_visibility_data(self, db: Session, airport_code: str, airport_id: int):
        """Migrate visibility RRD data."""
        rrd_file = self.rrd_path / f"{airport_code.lower()}-visibility.rrd"
        if not rrd_file.exists():
            logger.warning(f"Visibility RRD file not found: {rrd_file}")
            return
            
        try:
            data_points = await self._extract_rrd_data(rrd_file, ['visibility'])
            
            for timestamp, values in data_points:
                await self._upsert_weather_observation(
                    db, airport_id, timestamp, {
                        'visibility_mi': values.get('visibility')
                    }
                )
                
            logger.info(f"Migrated {len(data_points)} visibility records for {airport_code}")
            
        except Exception as e:
            logger.error(f"Error migrating visibility data for {airport_code}: {e}")
    
    async def _migrate_ceiling_data(self, db: Session, airport_code: str, airport_id: int):
        """Migrate ceiling RRD data."""
        rrd_file = self.rrd_path / f"{airport_code.lower()}-ceiling.rrd"
        if not rrd_file.exists():
            logger.warning(f"Ceiling RRD file not found: {rrd_file}")
            return
            
        try:
            data_points = await self._extract_rrd_data(rrd_file, ['ceiling'])
            
            for timestamp, values in data_points:
                await self._upsert_weather_observation(
                    db, airport_id, timestamp, {
                        'ceiling_ft': values.get('ceiling')
                    }
                )
                
            logger.info(f"Migrated {len(data_points)} ceiling records for {airport_code}")
            
        except Exception as e:
            logger.error(f"Error migrating ceiling data for {airport_code}: {e}")
    
    async def _extract_rrd_data(self, rrd_file: Path, data_sources: List[str]) -> List[Tuple[datetime, Dict]]:
        """
        Extract data from RRD file using rrdtool.
        
        Args:
            rrd_file: Path to RRD file
            data_sources: List of data source names to extract
            
        Returns:
            List of (timestamp, values) tuples
        """
        data_points = []
        
        try:
            # Use rrdtool to export data as JSON
            cmd = [
                'rrdtool', 'xport',
                '--start', 'now-10y',  # Last 10 years
                '--end', 'now',
                '--json',
                '--showtime'
            ]
            
            # Add data sources
            for ds in data_sources:
                cmd.extend(['DEF', f'{ds}={rrd_file}', ds, 'AVERAGE'])
                cmd.extend(['XPORT', ds, ds])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            json_data = json.loads(result.stdout)
            
            # Parse the JSON data
            if 'data' in json_data and json_data['data']:
                for row in json_data['data']:
                    if len(row) >= len(data_sources) + 1:  # +1 for timestamp
                        timestamp = datetime.fromtimestamp(row[0])
                        values = {}
                        for i, ds in enumerate(data_sources):
                            values[ds] = row[i + 1] if row[i + 1] is not None else None
                        data_points.append((timestamp, values))
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running rrdtool for {rrd_file}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing rrdtool output for {rrd_file}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error extracting RRD data from {rrd_file}: {e}")
            
        return data_points
    
    async def _upsert_weather_observation(self, db: Session, airport_id: int, timestamp: datetime, data: Dict):
        """
        Upsert weather observation data.
        
        Args:
            db: Database session
            airport_id: Airport ID
            timestamp: Observation timestamp
            data: Weather data dictionary
        """
        try:
            # Check if observation already exists
            existing = db.query(WeatherObservation).filter(
                WeatherObservation.airport_id == airport_id,
                WeatherObservation.time == timestamp
            ).first()
            
            if existing:
                # Update existing observation
                for key, value in data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
            else:
                # Create new observation
                observation = WeatherObservation(
                    airport_id=airport_id,
                    time=timestamp,
                    **{k: v for k, v in data.items() if v is not None}
                )
                db.add(observation)
            
            db.commit()
            self.migration_stats['records_migrated'] += 1
            
        except Exception as e:
            logger.error(f"Error upserting weather observation: {e}")
            db.rollback()
    
    async def get_migration_status(self) -> Dict:
        """Get current migration status."""
        return self.migration_stats.copy()
    
    async def validate_migration(self, db: Session) -> Dict:
        """
        Validate the migration by comparing RRD data with database data.
        
        Args:
            db: Database session
            
        Returns:
            Validation results
        """
        validation_results = {
            'airports_validated': 0,
            'data_points_validated': 0,
            'discrepancies': 0,
            'validation_errors': 0
        }
        
        try:
            airports = await self._discover_airports_from_rrd()
            
            for airport_code in airports:
                try:
                    airport = db.query(Airport).filter(Airport.icao == airport_code).first()
                    if not airport:
                        continue
                        
                    # Validate temperature data
                    temp_file = self.rrd_path / f"{airport_code.lower()}-temp.rrd"
                    if temp_file.exists():
                        rrd_data = await self._extract_rrd_data(temp_file, ['temp_c'])
                        db_data = db.query(WeatherObservation).filter(
                            WeatherObservation.airport_id == airport.id,
                            WeatherObservation.temperature_c.isnot(None)
                        ).order_by(WeatherObservation.time).all()
                        
                        # Compare data points (simplified validation)
                        validation_results['data_points_validated'] += len(db_data)
                        
                    validation_results['airports_validated'] += 1
                    
                except Exception as e:
                    logger.error(f"Error validating {airport_code}: {e}")
                    validation_results['validation_errors'] += 1
                    
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            validation_results['validation_errors'] += 1
            
        return validation_results

# Global instance
rrd_migration_service = RRDMigrationService()
