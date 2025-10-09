"""
Migration API Endpoints

Provides endpoints for managing data migration from legacy systems.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
import logging

from ...database import get_db
from ...models.airport import Airport
from ...models.weather import WeatherObservation
from ..migration.rrd_migration_service import rrd_migration_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/rrd/migrate")
async def migrate_rrd_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    rrd_path: Optional[str] = None
):
    """
    Start RRD data migration in the background.
    
    Args:
        background_tasks: FastAPI background tasks
        db: Database session
        rrd_path: Optional custom RRD path
        
    Returns:
        Migration status
    """
    try:
        if rrd_path:
            rrd_migration_service.rrd_path = rrd_path
            
        # Start migration in background
        background_tasks.add_task(rrd_migration_service.migrate_all_rrd_data, db)
        
        return {
            "status": "migration_started",
            "message": "RRD data migration started in background",
            "rrd_path": str(rrd_migration_service.rrd_path)
        }
        
    except Exception as e:
        logger.error(f"Error starting RRD migration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rrd/status")
async def get_migration_status():
    """
    Get current migration status.
    
    Returns:
        Migration status and statistics
    """
    try:
        status = await rrd_migration_service.get_migration_status()
        return {
            "status": "success",
            "migration_stats": status
        }
        
    except Exception as e:
        logger.error(f"Error getting migration status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rrd/validate")
async def validate_migration(
    db: Session = Depends(get_db)
):
    """
    Validate the migration by comparing RRD data with database data.
    
    Args:
        db: Database session
        
    Returns:
        Validation results
    """
    try:
        validation_results = await rrd_migration_service.validate_migration(db)
        return {
            "status": "success",
            "validation_results": validation_results
        }
        
    except Exception as e:
        logger.error(f"Error validating migration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rrd/airports")
async def get_rrd_airports():
    """
    Get list of airports with RRD data.
    
    Returns:
        List of airport codes with RRD data
    """
    try:
        airports = await rrd_migration_service._discover_airports_from_rrd()
        return {
            "status": "success",
            "airports": airports,
            "count": len(airports)
        }
        
    except Exception as e:
        logger.error(f"Error getting RRD airports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rrd/airport/{airport_code}/info")
async def get_rrd_airport_info(airport_code: str):
    """
    Get information about RRD files for a specific airport.
    
    Args:
        airport_code: ICAO airport code
        
    Returns:
        RRD file information
    """
    try:
        airport_code = airport_code.upper()
        rrd_path = rrd_migration_service.rrd_path
        
        rrd_files = {
            "temperature": rrd_path / f"{airport_code.lower()}-temp.rrd",
            "altimeter": rrd_path / f"{airport_code.lower()}-altimeter.rrd",
            "wind": rrd_path / f"{airport_code.lower()}-wind.rrd",
            "visibility": rrd_path / f"{airport_code.lower()}-visibility.rrd",
            "ceiling": rrd_path / f"{airport_code.lower()}-ceiling.rrd"
        }
        
        file_info = {}
        for file_type, file_path in rrd_files.items():
            if file_path.exists():
                stat = file_path.stat()
                file_info[file_type] = {
                    "exists": True,
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime,
                    "path": str(file_path)
                }
            else:
                file_info[file_type] = {
                    "exists": False,
                    "path": str(file_path)
                }
        
        return {
            "status": "success",
            "airport_code": airport_code,
            "rrd_files": file_info
        }
        
    except Exception as e:
        logger.error(f"Error getting RRD airport info for {airport_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rrd/airport/{airport_code}/migrate")
async def migrate_single_airport(
    airport_code: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Migrate RRD data for a single airport.
    
    Args:
        airport_code: ICAO airport code
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Migration status
    """
    try:
        airport_code = airport_code.upper()
        
        # Start migration in background
        background_tasks.add_task(
            rrd_migration_service._migrate_airport_data, 
            db, 
            airport_code
        )
        
        return {
            "status": "migration_started",
            "message": f"RRD data migration started for {airport_code}",
            "airport_code": airport_code
        }
        
    except Exception as e:
        logger.error(f"Error starting migration for {airport_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rrd/sample/{airport_code}")
async def get_rrd_sample_data(
    airport_code: str,
    file_type: str = "temperature",
    limit: int = 10
):
    """
    Get sample data from RRD files for testing.
    
    Args:
        airport_code: ICAO airport code
        file_type: Type of RRD file (temperature, altimeter, wind, visibility, ceiling)
        limit: Number of sample records to return
        
    Returns:
        Sample RRD data
    """
    try:
        airport_code = airport_code.upper()
        rrd_path = rrd_migration_service.rrd_path
        
        file_mapping = {
            "temperature": f"{airport_code.lower()}-temp.rrd",
            "altimeter": f"{airport_code.lower()}-altimeter.rrd",
            "wind": f"{airport_code.lower()}-wind.rrd",
            "visibility": f"{airport_code.lower()}-visibility.rrd",
            "ceiling": f"{airport_code.lower()}-ceiling.rrd"
        }
        
        if file_type not in file_mapping:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file_type. Must be one of: {list(file_mapping.keys())}"
            )
        
        rrd_file = rrd_path / file_mapping[file_type]
        if not rrd_file.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"RRD file not found: {rrd_file}"
            )
        
        # Get data sources based on file type
        data_sources = {
            "temperature": ['temp_c', 'temp_f', 'dew_pt_c', 'dew_pt_f'],
            "altimeter": ['altimeter'],
            "wind": ['wind_dir', 'wind_speed'],
            "visibility": ['visibility'],
            "ceiling": ['ceiling']
        }
        
        # Extract sample data
        data_points = await rrd_migration_service._extract_rrd_data(
            rrd_file, 
            data_sources[file_type]
        )
        
        # Limit results
        sample_data = data_points[-limit:] if len(data_points) > limit else data_points
        
        return {
            "status": "success",
            "airport_code": airport_code,
            "file_type": file_type,
            "sample_data": [
                {
                    "timestamp": point[0].isoformat(),
                    "values": point[1]
                }
                for point in sample_data
            ],
            "total_records": len(data_points),
            "sample_size": len(sample_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sample RRD data for {airport_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/migration/summary")
async def get_migration_summary(db: Session = Depends(get_db)):
    """
    Get a summary of migration status and database statistics.
    
    Args:
        db: Database session
        
    Returns:
        Migration and database summary
    """
    try:
        # Get database statistics
        airport_count = db.query(Airport).count()
        weather_count = db.query(WeatherObservation).count()
        
        # Get migration status
        migration_status = await rrd_migration_service.get_migration_status()
        
        # Get RRD airports
        rrd_airports = await rrd_migration_service._discover_airports_from_rrd()
        
        return {
            "status": "success",
            "database_stats": {
                "airports": airport_count,
                "weather_observations": weather_count
            },
            "migration_stats": migration_status,
            "rrd_airports": {
                "count": len(rrd_airports),
                "airports": rrd_airports
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting migration summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
