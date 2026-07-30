import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Sky, Stats } from '@react-three/drei';
import { Suspense } from 'react';
import { useSimulationStore } from '@/stores/simulationStore';
import { Robot3D } from './Robot3D';
import { CO2Field } from './CO2Field';
import { DetectionMarkers } from './DetectionMarkers';
import { PathTrails } from './PathTrails';

interface SceneViewerProps {
  showCO2Field?: boolean;
  showPathTrails?: boolean;
  showDetectionMarkers?: boolean;
  showGrid?: boolean;
  showSky?: boolean;
  cameraPreset?: 'top' | 'perspective' | 'follow';
  followRobotId?: string;
}

export function SceneViewer({
  showCO2Field = true,
  showPathTrails = true,
  showDetectionMarkers = true,
  showGrid = true,
  showSky = true,
  cameraPreset = 'perspective',
}: SceneViewerProps) {
  const robots = useSimulationStore((s) => Array.from(s.robots.values()));
  const simState = useSimulationStore((s) => s.simState);
  const detections = useSimulationStore((s) => s.detections);

  return (
    <div className="w-full h-full bg-slate-950 relative">
      <Canvas
        shadows
        camera={{ position: cameraPreset === 'top' ? [0, 30, 0.1] : [10, 8, 10], fov: 50 }}
        dpr={[1, 2]}
      >
        <Suspense fallback={null}>
          <ambientLight intensity={0.4} />
          <directionalLight
            position={[10, 20, 5]}
            intensity={1}
            castShadow
            shadow-mapSize={[1024, 1024]}
          />
          <hemisphereLight args={['#87ceeb', '#362907', 0.3]} />

          {showSky && <Sky distance={450} sunPosition={[5, 10, 5]} inclination={0.5} />}
          {showGrid && (
            <Grid
              args={[60, 60]}
              cellSize={1}
              cellThickness={0.5}
              cellColor="#1e293b"
              sectionSize={5}
              sectionThickness={1}
              sectionColor="#334155"
              fadeDistance={50}
              fadeStrength={1}
            />
          )}

          {showCO2Field && simState && <CO2Field density={simState.fog.density} concentration={simState.environment.co2Concentration} />}
          {showPathTrails && <PathTrails robots={robots} />}
          {showDetectionMarkers && <DetectionMarkers detections={detections.slice(0, 50)} />}

          {robots.map((robot) => (
            <Robot3D
              key={robot.id}
              robot={robot}
              isSelected={robot.id === useSimulationStore.getState().selectedRobotId}
              onClick={() => useSimulationStore.getState().setSelectedRobot(robot.id)}
            />
          ))}

          <OrbitControls
            makeDefault
            minDistance={3}
            maxDistance={80}
            maxPolarAngle={Math.PI / 2.1}
            dampingFactor={0.05}
          />

          {import.meta.env.DEV && <Stats />}
        </Suspense>
      </Canvas>

      <div className="absolute top-4 left-4 bg-slate-900/80 backdrop-blur rounded-lg p-3 text-xs space-y-1 border border-slate-800">
        <div className="font-semibold text-carbon-400">Scene Info</div>
        <div className="text-slate-400">Robots: <span className="text-slate-200">{robots.length}</span></div>
        <div className="text-slate-400">Detections: <span className="text-slate-200">{detections.length}</span></div>
        <div className="text-slate-400">CO₂: <span className="text-slate-200">{simState?.environment.co2Concentration.toFixed(0) ?? 400} ppm</span></div>
      </div>
    </div>
  );
}
