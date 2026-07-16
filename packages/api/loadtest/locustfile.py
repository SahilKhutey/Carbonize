"""
Locust load test for production capacity planning.

Run: locust -f loadtest/locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import random


class CBMSUser(HttpUser):
    """Simulated CBMS user behavior."""
    
    wait_time = between(1, 5)
    
    def on_start(self):
        """Login once at start."""
        self.client.post(
            "/api/auth/login",
            json={
                "email": f"user{random.randint(0, 9)}@org{random.randint(0, 9)}.com",
                "password": "LoadTest123!",
            },
        )
    
    @task(10)
    def list_plants(self):
        """Most common: list plants."""
        self.client.get("/api/plants")
    
    @task(5)
    def get_plant(self):
        """Get specific plant."""
        plant_id = "00000000-0000-0000-0000-000000000001"
        self.client.get(f"/api/plants/{plant_id}")
    
    @task(1)
    def submit_simulation(self):
        """Submit a new simulation (heaviest endpoint)."""
        self.client.post(
            "/api/simulations",
            json={
                "plant_profile_id": "00000000-0000-0000-0000-000000000001",
                "press_force_bar": 200.0,
                "enzyme_concentration_mg_l": 12.0,
                "chitosan_wt_pct": 3.0,
                "reactor_temperature_c": 40.0,
            },
        )
    
    @task(2)
    def get_simulation(self):
        """Get simulation status."""
        sim_id = "00000000-0000-0000-0000-000000000001"
        self.client.get(f"/api/simulations/{sim_id}")
