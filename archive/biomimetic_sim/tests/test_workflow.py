"""
tests/test_workflow.py
Unit tests verifying the Redis progress streaming and workflow pipeline.
"""

import json
import pytest
import redis
from uuid import uuid4
from workers.tasks import publish_progress

def test_progress_publication():
    """Verify that publish_progress publishes to the appropriate Redis channels."""
    run_id = str(uuid4())
    
    # Establish a connection directly and ping to verify it's active
    try:
        r = redis.Redis(host="localhost", port=6379, db=0, socket_connect_timeout=2.0)
        r.ping()
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
        pytest.skip("Local Redis server is not active or refused connection.")

    pubsub = r.pubsub()
    pubsub.subscribe(f"simulation.{run_id}.progress")
    
    # Run publication helper
    publish_progress(
        run_id_str=run_id,
        stage="KINETICS_SOLVE",
        pct=20,
        stage_pct=50,
        details="Solving carbonation kinetics"
    )
    
    # Read published message (must ignore first subscribe handshake)
    msg = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
    assert msg is not None
    assert msg["type"] == "message"
    
    data = json.loads(msg["data"].decode("utf-8"))
    assert data["run_id"] == run_id
    assert data["stage"] == "KINETICS_SOLVE"
    assert data["pct"] == 20
    assert data["details"] == "Solving carbonation kinetics"
    
    pubsub.unsubscribe()
    pubsub.close()
