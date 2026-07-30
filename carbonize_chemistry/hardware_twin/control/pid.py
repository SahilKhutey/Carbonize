"""
Industrial PID controller
"""
from dataclasses import dataclass


@dataclass
class PIDController:
    Kp: float = 1.0
    Ki: float = 0.0
    Kd: float = 0.0
    setpoint: float = 0.0
    output_min: float = 0.0
    output_max: float = 1000.0
    
    error: float = 0.0
    integral: float = 0.0
    last_error: float = 0.0
    
    def update(self, setpoint: float, measurement: float, dt: float) -> float:
        self.setpoint = setpoint
        self.error = setpoint - measurement
        
        P = self.Kp * self.error
        self.integral += self.error * dt
        I = self.Ki * self.integral
        D = self.Kd * ((self.error - self.last_error) / max(dt, 1e-5))
        
        output = max(self.output_min, min(self.output_max, P + I + D))
        self.last_error = self.error
        return float(output)
