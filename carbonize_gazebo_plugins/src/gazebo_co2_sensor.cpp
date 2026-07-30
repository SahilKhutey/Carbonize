/**
 * CO2 Concentration Sensor Plugin — Thread-Safe
 * Fixes Bottleneck B2: Decoupled sensor updates
 */

#include <gazebo/gazebo.hh>
#include <gazebo/sensors/sensors.hh>
#include <gazebo/common/Plugin.hh>
#include <gazebo/common/UpdateInfo.hh>
#include <gazebo/transport/transport.hh>
#include <gazebo/msgs/msgs.hh>
#include <gazebo/physics/World.hh>
#include <thread>
#include <atomic>
#include <random>

namespace gazebo
{
class CO2SensorPlugin : public SensorPlugin
{
public:
  CO2SensorPlugin() : SensorPlugin(), running_(false) {}
  ~CO2SensorPlugin() override
  {
    running_ = false;
    if (update_thread_.joinable()) update_thread_.join();
  }

  void Load(sensors::SensorPtr _sensor, sdf::ElementPtr _sdf) override
  {
    if (!_sensor) {
      gzerr << "CO2SensorPlugin: null sensor\n";
      return;
    }
    sensor_ = std::dynamic_pointer_cast<sensors::Sensor>(_sensor);
    if (!sensor_) {
      gzerr << "CO2SensorPlugin: cast failed\n";
      return;
    }

    // ─── Read SDF parameters ─────────────────────────────────
    update_rate_ = _sdf->Get<double>("update_rate", 10.0).first;
    topic_name_  = _sdf->Get<std::string>("topic", "~/co2_concentration").first;
    base_ppm_    = _sdf->Get<double>("base_ppm", 420.0).first;
    noise_std_   = _sdf->Get<double>("noise_std", 5.0).first;
    drift_rate_  = _sdf->Get<double>("drift_rate", 0.1).first;

    // ─── Transport setup ─────────────────────────────────────
    node_ = transport::NodePtr(new transport::Node());
    node_->Init(sensor_->WorldName());
    pub_ = node_->Advertise<msgs::Any>(topic_name_);

    // ─── Thread-safe state ───────────────────────────────────
    current_ppm_.store(base_ppm_, std::memory_order_relaxed);
    running_.store(true, std::memory_order_relaxed);

    // ─── Bind to sensor update ───────────────────────────────
    update_conn_ = sensor_->ConnectUpdated(
      std::bind(&CO2SensorPlugin::OnSensorUpdate, this));

    // ─── Independent update thread ──────────────────────────
    update_thread_ = std::thread(&CO2SensorPlugin::UpdateLoop, this);

    gzmsg << "CO2SensorPlugin loaded: " << topic_name_
          << " @ " << update_rate_ << " Hz\n";
  }

private:
  void OnSensorUpdate()
  {
    // Hook for sensor-specific callbacks (no-op here)
  }

  void UpdateLoop()
  {
    // High-resolution RNG independent of simulation thread
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<double> noise(0.0, noise_std_);

    // CO2 concentration dynamics with slow drift
    double drift = 0.0;
    auto last = std::chrono::steady_clock::now();
    const auto period = std::chrono::microseconds(
      static_cast<int>(1e6 / update_rate_));

    while (running_.load(std::memory_order_relaxed))
    {
      auto now = std::chrono::steady_clock::now();
      auto dt = std::chrono::duration<double>(now - last).count();
      last = now;

      // Simulate slow atmospheric drift + measurement noise
      drift += drift_rate_ * (gen() % 2 == 0 ? 1 : -1) * dt;
      double measured = base_ppm_ + drift + noise(gen);
      current_ppm_.store(measured, std::memory_order_relaxed);

      // Publish
      msgs::Any msg;
      msg.set_type(msgs::Any::DOUBLE);
      msg.set_double_value(measured);
      pub_->Publish(msg);

      // Sleep until next update window
      std::this_thread::sleep_until(now + period);
    }
  }

  // Members
  sensors::SensorPtr sensor_;
  gazebo::event::ConnectionPtr update_conn_;
  transport::NodePtr node_;
  transport::PublisherPtr pub_;
  std::thread update_thread_;
  std::atomic<bool> running_;
  std::atomic<double> current_ppm_;
  std::string topic_name_;
  double update_rate_;
  double base_ppm_;
  double noise_std_;
  double drift_rate_;
};

GZ_REGISTER_SENSOR_PLUGIN(CO2SensorPlugin)
}  // namespace gazebo
