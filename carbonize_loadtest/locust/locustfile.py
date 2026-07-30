"""
Locust complex scenario with realistic user behavior
"""
import json
import random
import time
import base64
import os
from locust import HttpUser, task, between, events, LoadTestShape
import numpy as np

def generate_realistic_telemetry():
    metrics = {
        'co2_ppm': random.gauss(420, 50),
        'temperature': random.gauss(22, 3),
        'humidity': random.gauss(50, 10),
        'battery': random.uniform(20, 100),
    }
    metric_type = random.choice(list(metrics.keys()))
    return {
        'robot_id': f'robot_{random.randint(1, 5)}',
        'metric_type': metric_type,
        'value': max(0, metrics[metric_type]),
        'unit': 'ppm' if metric_type == 'co2_ppm' else 'C' if metric_type == 'temperature' else '%',
        'timestamp': int(time.time() * 1000),
        'source': 'locust',
    }


class InferenceUser(HttpUser):
    wait_time = between(0.1, 0.5)
    weight = 60
    
    @task(70)
    def single_inference(self):
        fake_b64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
        with self.client.post(
            '/api/v1/inference/predict',
            json={'model_id': '1.5.0', 'image': fake_b64, 'confidence_threshold': 0.5},
            catch_response=True,
            timeout=30,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f'Status {response.status_code}')

    @task(30)
    def telemetry_ingest(self):
        payload = generate_realistic_telemetry()
        with self.client.post('/api/v1/telemetry', json=payload, catch_response=True) as response:
            if response.status_code in (200, 202):
                response.success()


class StaircaseLoadShape(LoadTestShape):
    stages = [
        {'duration': 60, 'users': 50, 'spawn_rate': 10},
        {'duration': 180, 'users': 150, 'spawn_rate': 10},
        {'duration': 300, 'users': 300, 'spawn_rate': 20},
        {'duration': 600, 'users': 0, 'spawn_rate': 50},
    ]
    
    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage['duration']:
                return (stage['users'], stage['spawn_rate'])
        return None
