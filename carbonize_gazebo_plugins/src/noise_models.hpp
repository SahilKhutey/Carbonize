/**
 * Realistic Multi-Modal Noise Models
 * Fixes Bottleneck B11: Unrealistic synthetic data
 */

#pragma once
#include <random>
#include <chrono>
#include <cmath>
#include <algorithm>

class RealisticCO2Sensor {
public:
    struct Profile {
        double base_ppm;
        double bias;              // Systematic offset
        double drift_rate;        // ppm/s slow drift
        double gaussian_std;      // Random noise
        double temp_coeff;        // ppm/°C cross-sensitivity
        double humidity_coeff;    // ppm/%RH cross-sensitivity
        double correlation_lag;   // s for CO2-CO2 autocorrelation
    };
    
    RealisticCO2Sensor(const Profile& p) : profile_(p) {
        std::random_device rd;
        rng_.seed(rd());
        mean_ = p.base_ppm;
        var_ = p.gaussian_std * p.gaussian_std;
        last_update_ = std::chrono::steady_clock::now();
    }
    
    double sample(double true_co2, double temperature_c, double humidity_pct) {
        auto now = std::chrono::steady_clock::now();
        double dt = std::chrono::duration<double>(now - last_update_).count();
        last_update_ = now;
        
        // ─── 1. Bias (deterministic offset) ───────────────────────
        double bias = profile_.bias;
        
        // ─── 2. Slow drift (1/f noise, random walk) ───────────────
        drift_ += profile_.drift_rate * dt * (uniform_() - 0.5) * 2.0;
        drift_ = std::clamp(drift_, -50.0, 50.0);
        
        // ─── 3. Gaussian white noise ──────────────────────────────
        std::normal_distribution<double> gauss(0.0, profile_.gaussian_std);
        double noise = gauss(rng_);
        
        // ─── 4. Cross-sensitivity to environmental variables ───────
        double temp_effect = profile_.temp_coeff * (temperature_c - 25.0);
        double hum_effect = profile_.humidity_coeff * (humidity_pct - 50.0);
        
        // ─── 5. Quantization (sensor ADC resolution) ──────────────
        double raw = true_co2 + bias + drift_ + noise + temp_effect + hum_effect;
        double quantized = std::round(raw);  // 1 ppm ADC
        
        return quantized;
    }
    
private:
    Profile profile_;
    std::mt19937 rng_;
    double mean_;
    double var_;
    double drift_ = 0.0;
    std::chrono::steady_clock::time_point last_update_;
    
    double uniform_() {
        std::uniform_real_distribution<double> u(0.0, 1.0);
        return u(rng_);
    }
};

// ─── Real-world profile (e.g., K30 CO2 sensor) ──────────────────────
inline RealisticCO2Sensor::Profile k30_profile() {
    return {
        .base_ppm = 400.0,
        .bias = 30.0,              // Typical K30 overshoot
        .drift_rate = 0.5,         // ppm/s
        .gaussian_std = 25.0,      // K30 datasheet
        .temp_coeff = 2.0,         // 2 ppm/°C
        .humidity_coeff = 0.5,
        .correlation_lag = 1.0
    };
}
