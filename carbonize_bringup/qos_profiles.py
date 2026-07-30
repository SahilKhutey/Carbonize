"""
QoS Profile Library — Production-Grade
Fixes Bottleneck B3: DDS bandwidth saturation
"""

from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy


# ─── Sensor streams: high-rate, lossy OK ────────────────────────────
SENSOR_IMAGE_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1,                        # Latest frame only
    durability=QoSDurabilityPolicy.VOLATILE
)

SENSOR_LIDAR_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=5,
    durability=QoSDurabilityPolicy.VOLATILE
)

SENSOR_IMU_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10
)

# ─── Detection results: lossless, late-joiners OK ──────────────────
DETECTION_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10,
    durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
)

# ─── Telemetry to cloud: persistent, large queue ───────────────────
TELEMETRY_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_ALL,
    depth=1000,
    durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
)

# ─── Command / control: low-latency, reliable ──────────────────────
CONTROL_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10
)

# ─── TF transforms: reliable, transient for late subscribers ───────
TF_STATIC_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1,
    durability=QoSDurabilityPolicy.TRANSIENT_LOCAL
)

# ─── Diagnostics: best-effort, small queue ─────────────────────────
DIAGNOSTICS_QOS = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=5
)


PROFILE_MAP = {
    'image':         SENSOR_IMAGE_QOS,
    'lidar':         SENSOR_LIDAR_QOS,
    'imu':           SENSOR_IMU_QOS,
    'detection':     DETECTION_QOS,
    'telemetry':     TELEMETRY_QOS,
    'control':       CONTROL_QOS,
    'tf_static':     TF_STATIC_QOS,
    'diagnostics':   DIAGNOSTICS_QOS,
}


def get_qos(profile_name: str) -> QoSProfile:
    """Factory: lookup QoS profile by name."""
    if profile_name not in PROFILE_MAP:
        raise KeyError(f"Unknown QoS profile: {profile_name}")
    return PROFILE_MAP[profile_name]
