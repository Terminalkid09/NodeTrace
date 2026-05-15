import json
import secrets
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from decouple import config

# Rate limiting
from app.utils.ratelimit import device_limiter, user_limiter

# Logger
from app.utils.logger import logger

# Schemi
from app.schemas.device import (
    DeviceRegister,
    TelemetryData,
    Heartbeat,
    DeviceOut,
    DeviceDetail,
    TelemetryOut,
    StatusOut
)
from app.schemas.user import UserLogin
from app.schemas.alert import AlertOut

# Database
from app.database.connection import SessionLocal

# Modelli
from app.models.device import Device
from app.models.telemetry import Telemetry
from app.models.user import User
from app.models.alert import Alert

# Sicurezza agent
from app.utils.security import generate_device_token, verify_device_token

# Sicurezza admin
from app.utils.auth import (
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter()


# Alert thresholds
CPU_CRITICAL = 90.0
RAM_CRITICAL = 95.0
DISK_WARNING_MB = 1024  # 1GB
DISK_CRITICAL_MB = 512  # 512MB
CONNECTIONS_WARNING = 100


def check_and_create_alerts(db: Session, device_id: str, telemetry: TelemetryData):
    """Check telemetry against thresholds and create alerts if needed."""
    alerts_to_create = []

    # CPU high
    if telemetry.cpu_usage and telemetry.cpu_usage > CPU_CRITICAL:
        existing = db.query(Alert).filter(
            Alert.device_id == device_id,
            Alert.alert_type == "cpu_high",
            Alert.resolved == False
        ).first()
        if not existing:
            alerts_to_create.append({
                "alert_type": "cpu_high",
                "severity": "critical",
                "message": f"CPU usage is {telemetry.cpu_usage:.1f}% (threshold: {CPU_CRITICAL}%)",
                "alert_value": telemetry.cpu_usage
            })

    # RAM high
    if telemetry.ram_usage and telemetry.ram_usage > RAM_CRITICAL:
        existing = db.query(Alert).filter(
            Alert.device_id == device_id,
            Alert.alert_type == "ram_high",
            Alert.resolved == False
        ).first()
        if not existing:
            alerts_to_create.append({
                "alert_type": "ram_high",
                "severity": "critical",
                "message": f"RAM usage is {telemetry.ram_usage:.1f}% (threshold: {RAM_CRITICAL}%)",
                "alert_value": telemetry.ram_usage
            })

    # Disk low
    if telemetry.disk_free is not None:
        disk_free_gb = telemetry.disk_free / 1024  # Convert to GB
        if disk_free_gb < DISK_CRITICAL_MB / 1024:
            existing = db.query(Alert).filter(
                Alert.device_id == device_id,
                Alert.alert_type == "disk_critical",
                Alert.resolved == False
            ).first()
            if not existing:
                alerts_to_create.append({
                    "alert_type": "disk_critical",
                    "severity": "critical",
                    "message": f"Disk free space is {disk_free_gb:.1f} GB (critical threshold: {DISK_CRITICAL_MB/1024:.1f} GB)",
                    "alert_value": disk_free_gb
                })
        elif disk_free_gb < DISK_WARNING_MB / 1024:
            existing = db.query(Alert).filter(
                Alert.device_id == device_id,
                Alert.alert_type == "disk_warning",
                Alert.resolved == False
            ).first()
            if not existing:
                alerts_to_create.append({
                    "alert_type": "disk_warning",
                    "severity": "warning",
                    "message": f"Disk free space is {disk_free_gb:.1f} GB (warning threshold: {DISK_WARNING_MB/1024:.1f} GB)",
                    "alert_value": disk_free_gb
                })

    # Active connections high
    if telemetry.active_connections and telemetry.active_connections > CONNECTIONS_WARNING:
        existing = db.query(Alert).filter(
            Alert.device_id == device_id,
            Alert.alert_type == "connections_high",
            Alert.resolved == False
        ).first()
        if not existing:
            alerts_to_create.append({
                "alert_type": "connections_high",
                "severity": "warning",
                "message": f"Active connections: {telemetry.active_connections} (threshold: {CONNECTIONS_WARNING})",
                "alert_value": float(telemetry.active_connections)
            })

    # Create alerts
    for alert_data in alerts_to_create:
        alert = Alert(
            device_id=device_id,
            **alert_data
        )
        db.add(alert)
        logger.warning(f"Alert created for device_id={device_id}: {alert_data['alert_type']} - {alert_data['message']}")

    if alerts_to_create:
        db.commit()


# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health Check
@router.get("/health")
def health_check():
    return {"status": "ok"}


# Agent registration
ENROLL_KEY = config("ENROLL_KEY")

@user_limiter.limit("1/minute")  # Limit registrations per IP
@router.post("/register")
def register_device(payload: DeviceRegister, request: Request, db: Session = Depends(get_db)):
    if payload.enroll_key != ENROLL_KEY:
        logger.warning(f"Invalid enroll key attempt from hostname={payload.hostname}")
        return {"status": "error", "message": "invalid_enrollment_key"}

    device_id = "dev-" + secrets.token_hex(8)
    device_token = generate_device_token()

    device = Device(
        device_id=device_id,
        hostname=payload.hostname,
        os=payload.os,
        os_version=payload.os_version,
        cpu_model=payload.cpu_model,
        total_ram=payload.total_ram,
        mac_address=payload.mac_address,
        device_token=device_token
    )

    db.add(device)
    db.commit()

    logger.info(f"New device registered: device_id={device_id}, hostname={payload.hostname}")

    return {
        "status": "registered",
        "device_id": device_id,
        "device_token": device_token
    }


# Agent telemetry update
@device_limiter.limit("6/minute")  # Allow burst but limit sustained rate
@router.post("/update")
def update_telemetry(
    payload: TelemetryData,
    request: Request,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header on /update")
        return {"status": "error", "message": "missing_token"}

    token = authorization.split(" ")[1]
    device = verify_device_token(db, token)

    if not device:
        logger.warning("Invalid device token on /update")
        return {"status": "error", "message": "invalid_token"}

    entry = Telemetry(
        device_id=payload.device_id,
        cpu_usage=payload.cpu_usage,
        ram_usage=payload.ram_usage,
        ip_local=payload.ip_local,
        ip_public=payload.ip_public,
        geo_country=payload.geo_country,
        geo_city=payload.geo_city,
        processes=json.dumps(payload.processes) if payload.processes else None,
        disk_free=payload.disk_free,
        disk_total=payload.disk_total,
        network_sent=payload.network_sent,
        network_received=payload.network_received,
        active_connections=payload.active_connections
    )

    db.add(entry)
    db.commit()

    # Create alerts for anomalies
    for anomaly in anomalies_found:
        new_alert = Alert(
            device_id=payload.device_id,
            alert_type="statistical_anomaly",
            severity="warning",
            message=f"Statistical anomaly detected in {anomaly['metric']}: value {anomaly['value']} (Z-Score: {anomaly['z_score']:.2f})",
            alert_value=float(anomaly['value'])
        )
        db.add(new_alert)
    
    if anomalies_found:
        db.commit()

    # Check for alerts
    check_and_create_alerts(db, payload.device_id, payload)

    logger.info(f"Telemetry saved for device_id={payload.device_id}")

    return {"status": "telemetry_saved"}


# Agent heartbeat
@device_limiter.limit("2/minute")  # Heartbeats every 30s, allow some tolerance
@router.post("/heartbeat")
def heartbeat(
    payload: Heartbeat,
    request: Request,
    db: Session = Depends(get_db),
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid Authorization header on /heartbeat")
        return {"status": "error", "message": "missing_token"}

    token = authorization.split(" ")[1]
    device = verify_device_token(db, token)

    if not device:
        logger.warning("Invalid device token on /heartbeat")
        return {"status": "error", "message": "invalid_token"}

    device.last_seen = datetime.utcnow()
    db.commit()

    logger.info(f"Heartbeat received from device_id={payload.device_id}")

    return {"status": "alive"}


# Dashboard endpoints (Protected)
@user_limiter.limit("30/minute")  # Generous limit for admin dashboard
@router.get("/devices", response_model=List[DeviceOut])
def get_devices(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    devices = db.query(Device).all()
    now = datetime.utcnow()

    output = []
    for d in devices:
        is_online = (now - d.last_seen) < timedelta(seconds=120)
        output.append(DeviceOut(
            device_id=d.device_id,
            hostname=d.hostname,
            os=d.os,
            mac_address=d.mac_address,
            last_seen=d.last_seen,
            status="online" if is_online else "offline"
        ))

    logger.info(f"Devices list requested by user={user}")

    return output


@user_limiter.limit("20/minute")
@router.get("/devices/{device_id}", response_model=DeviceDetail)
def get_device_detail(device_id: str, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    device = db.query(Device).filter(Device.device_id == device_id).first()

    if not device:
        logger.warning(f"Device detail requested for non-existing device_id={device_id} by user={user}")
        raise HTTPException(status_code=404, detail="device_not_found")

    now = datetime.utcnow()
    is_online = (now - device.last_seen) < timedelta(seconds=120)

    latest = (
        db.query(Telemetry)
        .filter(Telemetry.device_id == device_id)
        .order_by(Telemetry.timestamp.desc())
        .first()
    )

    latest_out = None
    if latest:
        latest_out = TelemetryOut(
            timestamp=latest.timestamp,
            cpu_usage=latest.cpu_usage,
            ram_usage=latest.ram_usage,
            ip_local=latest.ip_local,
            ip_public=latest.ip_public,
            geo_country=latest.geo_country,
            geo_city=latest.geo_city,
            processes=json.loads(latest.processes) if latest.processes else None,
            disk_free=latest.disk_free,
            disk_total=latest.disk_total,
            network_sent=latest.network_sent,
            network_received=latest.network_received,
            active_connections=latest.active_connections
        )

    history = (
        db.query(Telemetry)
        .filter(Telemetry.device_id == device_id)
        .order_by(Telemetry.timestamp.desc())
        .limit(20)
        .all()
    )

    history_out = [
        TelemetryOut(
            timestamp=t.timestamp,
            cpu_usage=t.cpu_usage,
            ram_usage=t.ram_usage,
            ip_local=t.ip_local,
            ip_public=t.ip_public,
            geo_country=t.geo_country,
            geo_city=t.geo_city,
            processes=json.loads(t.processes) if t.processes else None,
            disk_free=t.disk_free,
            disk_total=t.disk_total,
            network_sent=t.network_sent,
            network_received=t.network_received,
            active_connections=t.active_connections
        )
        for t in history
    ]

    # Count active alerts
    active_alerts_count = db.query(Alert).filter(
        Alert.device_id == device_id,
        Alert.resolved == False
    ).count()

    logger.info(f"Device detail requested for device_id={device_id} by user={user}")

    return DeviceDetail(
        device_id=device.device_id,
        hostname=device.hostname,
        os=device.os,
        mac_address=device.mac_address,
        last_seen=device.last_seen,
        status="online" if is_online else "offline",
        latest_telemetry=latest_out,
        telemetry_history=history_out,
        active_alerts_count=active_alerts_count
    )


@user_limiter.limit("10/minute")
@router.get("/telemetry/{device_id}", response_model=List[TelemetryOut])
def get_telemetry_history(device_id: str, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    device = db.query(Device).filter(Device.device_id == device_id).first()

    if not device:
        logger.warning(f"Telemetry history requested for non-existing device_id={device_id} by user={user}")
        raise HTTPException(status_code=404, detail="device_not_found")

    entries = (
        db.query(Telemetry)
        .filter(Telemetry.device_id == device_id)
        .order_by(Telemetry.timestamp.asc())
        .all()
    )

    output = []
    for t in entries:
        output.append(TelemetryOut(
            timestamp=t.timestamp,
            cpu_usage=t.cpu_usage,
            ram_usage=t.ram_usage,
            ip_local=t.ip_local,
            ip_public=t.ip_public,
            geo_country=t.geo_country,
            geo_city=t.geo_city,
            processes=json.loads(t.processes) if t.processes else None,
            disk_free=t.disk_free,
            disk_total=t.disk_total,
            network_sent=t.network_sent,
            network_received=t.network_received,
            active_connections=t.active_connections
        ))

    logger.info(f"Telemetry history requested for device_id={device_id} by user={user}")

    return output


@user_limiter.limit("60/minute")  # Status can be polled frequently
@router.get("/status", response_model=StatusOut)
def get_status(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    devices = db.query(Device).all()
    now = datetime.utcnow()

    online = 0
    offline = 0

    for d in devices:
        if (now - d.last_seen) < timedelta(seconds=120):
            online += 1
        else:
            offline += 1

    logger.info(f"Status requested by user={user}")

    return StatusOut(
        total=len(devices),
        online=online,
        offline=offline,
        timestamp=now
    )


# Alert endpoints
@user_limiter.limit("20/minute")
@router.get("/alerts", response_model=List[AlertOut])
def get_alerts(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).all()
    logger.info(f"Alerts list requested by user={user}")
    return alerts


@user_limiter.limit("15/minute")
@router.get("/alerts/{device_id}", response_model=List[AlertOut])
def get_device_alerts(device_id: str, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        logger.warning(f"Alerts requested for non-existing device_id={device_id} by user={user}")
        raise HTTPException(status_code=404, detail="device_not_found")

    alerts = db.query(Alert).filter(Alert.device_id == device_id).order_by(Alert.timestamp.desc()).all()
    logger.info(f"Alerts requested for device_id={device_id} by user={user}")
    return alerts


@user_limiter.limit("10/minute")
@router.put("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        logger.warning(f"Resolve requested for non-existing alert_id={alert_id} by user={user}")
        raise HTTPException(status_code=404, detail="alert_not_found")

    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    db.commit()

    logger.info(f"Alert resolved: alert_id={alert_id} by user={user}")
    return {"status": "alert_resolved"}