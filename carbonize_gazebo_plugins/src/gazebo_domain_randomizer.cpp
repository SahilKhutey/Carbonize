/**
 * Domain Randomization Plugin
 * Fixes Bottleneck B8: Sim2Real gap
 */

#include <gazebo/gazebo.hh>
#include <gazebo/common/Plugin.hh>
#include <gazebo/common/UpdateInfo.hh>
#include <gazebo/rendering/rendering.hh>
#include <gazebo/rendering/Scene.hh>
#include <gazebo/rendering/Light.hh>
#include <gazebo/transport/transport.hh>
#include <random>
#include <thread>
#include <atomic>

namespace gazebo
{
class DomainRandomizerPlugin : public WorldPlugin
{
public:
  void Load(physics::WorldPtr _world, sdf::ElementPtr _sdf) override
  {
    world_ = _world;
    node_ = transport::NodePtr(new transport::Node());
    node_->Init(_world->Name());
    
    // ─── SDF parameters ─────────────────────────────────────
    episode_duration_sec_ = _sdf->Get<double>("episode_duration", 30.0).first;
    light_intensity_range_ = _sdf->Get<double>("light_intensity_range", 0.7).first;
    ambient_range_        = _sdf->Get<double>("ambient_range", 0.4).first;
    fog_density_range_    = _sdf->Get<double>("fog_density_range", 0.05).first;
    bg_color_range_       = _sdf->Get<double>("bg_color_range", 0.3).first;
    
    running_.store(true, std::memory_order_relaxed);
    rand_thread_ = std::thread(&DomainRandomizerPlugin::RandomizationLoop, this);
    
    gzmsg << "DomainRandomizer loaded: episode=" << episode_duration_sec_ << "s\n";
  }

  ~DomainRandomizerPlugin() override
  {
    running_.store(false, std::memory_order_relaxed);
    if (rand_thread_.joinable()) rand_thread_.join();
  }

private:
  void RandomizationLoop()
  {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<double> uniform(0.0, 1.0);
    
    while (running_.load(std::memory_order_relaxed))
    {
      auto start = std::chrono::steady_clock::now();
      
      if (auto scene = rendering::get_scene())
      {
        // ─── Randomize lighting ───────────────────────────────
        if (scene->LightCount() > 0)
        {
          auto light = scene->LightByName("sun");
          if (light)
          {
            double i = sunset_intensity_ * (0.5 + uniform(gen) * light_intensity_range_);
            light->SetCastShadows(uniform(gen) > 0.3);
            light->SetDiffuseColor(0.5 + uniform(gen) * 0.5, 
                                    0.5 + uniform(gen) * 0.5, 
                                    0.5 + uniform(gen) * 0.5);
            light->SetIntensity(i);
          }
        }
        
        // ─── Randomize ambient ────────────────────────────────
        scene->SetAmbient(
          gazebo::common::Color(0.1 + uniform(gen) * ambient_range_,
                                0.1 + uniform(gen) * ambient_range_,
                                0.1 + uniform(gen) * ambient_range_));
        
        // ─── Randomize fog ────────────────────────────────────
        scene->SetFogEnabled(uniform(gen) > 0.5);
        scene->SetFogDensity(0.0 + uniform(gen) * fog_density_range_);
      }
      
      // ─── Randomize physics parameters ─────────────────────────
      if (world_)
      {
        world_->Physics()->SetGravity(
          gazebo::common::Vector3(0, 0, -9.81 * (0.95 + uniform(gen) * 0.1)));
      }
      
      // ─── Sleep until next episode ─────────────────────────────
      auto elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - start).count();
      int sleep_us = std::max(0, static_cast<int>((episode_duration_sec_ - elapsed) * 1e6));
      std::this_thread::sleep_for(std::chrono::microseconds(sleep_us));
    }
  }

  physics::WorldPtr world_;
  transport::NodePtr node_;
  std::thread rand_thread_;
  std::atomic<bool> running_;
  double episode_duration_sec_;
  double light_intensity_range_;
  double ambient_range_;
  double fog_density_range_;
  double bg_color_range_;
  double sunset_intensity_ = 1.0;
};

GZ_REGISTER_WORLD_PLUGIN(DomainRandomizerPlugin)
}  // namespace gazebo
