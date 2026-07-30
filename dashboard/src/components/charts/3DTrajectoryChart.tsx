import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Line } from '@react-three/drei';
import { useRef, useMemo, useState } from 'react';
import * as THREE from 'three';
import { useTheme } from '@/themes/ThemeProvider';

export interface TrajectoryPoint {
  timestamp: number;
  position: [number, number, number];
  velocity?: number;
  orientation?: number;
  event?: 'start' | 'capture' | 'pause' | 'end' | 'detection';
  label?: string;
}

export interface Trajectory3DChartProps {
  trajectories: Array<{ id: string; name: string; points: TrajectoryPoint[]; color?: string }>;
  height?: number;
  showAxes?: boolean;
  showPath?: boolean;
  showDirectionMarkers?: boolean;
  showEvents?: boolean;
  interactive?: boolean;
  onPointClick?: (trajectoryId: string, point: TrajectoryPoint) => void;
}

export function Trajectory3DChart({
  trajectories,
  height = 500,
  showAxes = true,
  showPath = true,
  showDirectionMarkers = true,
  showEvents = true,
  interactive = true,
  onPointClick,
}: Trajectory3DChartProps) {
  const { theme } = useTheme();
  
  return (
    <div
      className="bg-surface border border-border rounded-theme-md overflow-hidden"
      style={{ height }}
    >
      <Canvas
        camera={{ position: [15, 12, 15], fov: 50 }}
        dpr={[1, 2]}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 20, 5]} intensity={1} castShadow />
        
        <SceneBackground theme={theme} />
        
        {showAxes && <AxesHelper />}
        
        {trajectories.map((t, i) => (
          <Trajectory
            key={t.id}
            trajectory={t}
            color={t.color || (theme.colors as any)[`chart${(i % 8) + 1}`]}
            showPath={showPath}
            showEvents={showEvents}
            interactive={interactive}
            onPointClick={onPointClick}
          />
        ))}
        
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          minDistance={5}
          maxDistance={50}
        />
      </Canvas>
    </div>
  );
}

function SceneBackground({ theme }: any) {
  const { scene } = useThree();
  if (!(scene.background instanceof THREE.Color)) {
    scene.background = new THREE.Color(theme.colors.background);
  }
  return <gridHelper args={[30, 30, theme.colors.border, theme.colors.borderMuted]} />;
}

function AxesHelper() {
  return (
    <group>
      <Line points={[[-10, 0, 0], [10, 0, 0]]} color="#ef4444" lineWidth={2} />
      <Line points={[[0, -10, 0], [0, 10, 0]]} color="#22c55e" lineWidth={2} />
      <Line points={[[0, 0, -10], [0, 0, 10]]} color="#0ea5e9" lineWidth={2} />
      <Text position={[10.5, 0, 0]} fontSize={0.5} color="#ef4444">X</Text>
      <Text position={[0, 10.5, 0]} fontSize={0.5} color="#22c55e">Y</Text>
      <Text position={[0, 0, 10.5]} fontSize={0.5} color="#0ea5e9">Z</Text>
    </group>
  );
}

function Trajectory({
  trajectory, color, showPath, showEvents, interactive, onPointClick,
}: any) {
  const points3D = useMemo(() => {
    return trajectory.points.map((p: TrajectoryPoint) => new THREE.Vector3(...p.position));
  }, [trajectory.points]);
  
  const pathGeometry = useMemo(() => {
    if (points3D.length < 2) return null;
    const curve = new THREE.CatmullRomCurve3(points3D);
    return new THREE.BufferGeometry().setFromPoints(curve.getPoints(100));
  }, [points3D]);
  
  const [progress, setProgress] = useState(0);
  useFrame((_, delta) => {
    setProgress((p) => (p + delta * 0.2) % 1);
  });
  
  return (
    <group>
      {showPath && pathGeometry && (
        <line>
          <primitive object={pathGeometry} attach="geometry" />
          <lineBasicMaterial color={color} linewidth={3} />
        </line>
      )}
      
      {points3D.length > 0 && (
        <group>
          {(() => {
            const idx = Math.floor(progress * (points3D.length - 1));
            const p = points3D[idx];
            return (
              <mesh position={p}>
                <sphereGeometry args={[0.15, 16, 16]} />
                <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
              </mesh>
            );
          })()}
        </group>
      )}
      
      {showEvents && trajectory.points.map((point: TrajectoryPoint, i: number) => {
        if (!point.event) return null;
        return (
          <EventMarker
            key={i}
            position={point.position}
            event={point.event}
            label={point.label}
            color={color}
          />
        );
      })}
      
      {interactive && trajectory.points.map((point: TrajectoryPoint, i: number) => (
        <ClickPoint
          key={i}
          position={point.position}
          onClick={() => onPointClick?.(trajectory.id, point)}
          color={color}
        />
      ))}
      
      <Text
        position={points3D[points3D.length - 1] || [0, 0, 0]}
        fontSize={0.4}
        color={color}
        anchorX="left"
        anchorY="bottom"
      >
        {trajectory.name}
      </Text>
    </group>
  );
}

function EventMarker({ position, event, label, color }: any) {
  const eventColors: Record<string, string> = {
    start: '#22c55e',
    capture: '#0ea5e9',
    pause: '#fbbf24',
    end: '#ef4444',
    detection: '#d946ef',
  };
  const eventColor = eventColors[event] || color;
  
  return (
    <group position={position}>
      <mesh>
        <octahedronGeometry args={[0.2, 0]} />
        <meshStandardMaterial color={eventColor} emissive={eventColor} emissiveIntensity={0.6} />
      </mesh>
      {label && (
        <Text position={[0, 0.5, 0]} fontSize={0.25} color={eventColor}>{label}</Text>
      )}
    </group>
  );
}

function ClickPoint({ position, onClick, color }: any) {
  const [hovered, setHovered] = useState(false);
  return (
    <mesh
      position={position}
      onClick={onClick}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <sphereGeometry args={[hovered ? 0.15 : 0.08, 8, 8]} />
      <meshStandardMaterial color={color} transparent opacity={hovered ? 1 : 0.6} />
    </mesh>
  );
}
