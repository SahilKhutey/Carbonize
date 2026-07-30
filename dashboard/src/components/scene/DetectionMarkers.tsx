import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { Detection } from '@/types';

interface DetectionMarkersProps {
  detections: Detection[];
}

export function DetectionMarkers({ detections }: DetectionMarkersProps) {
  return (
    <group>
      {detections.map((det) => {
        if (!det.position) return null;
        return <DetectionMarker key={det.id} detection={det} />;
      })}
    </group>
  );
}

function DetectionMarker({ detection }: { detection: Detection }) {
  const ref = useRef<THREE.Mesh>(null);
  const age = (Date.now() - detection.timestamp) / 1000;
  const opacity = Math.max(0, 1 - age / 10);

  useFrame((state) => {
    if (!ref.current) return;
    const scale = 1 + Math.sin(state.clock.elapsedTime * 4) * 0.2;
    ref.current.scale.setScalar(scale);
  });

  if (opacity <= 0) return null;

  return (
    <mesh
      ref={ref}
      position={[detection.position!.x, detection.position!.y, detection.position!.z]}
    >
      <sphereGeometry args={[0.15, 16, 16]} />
      <meshBasicMaterial color="#22c55e" transparent opacity={opacity * 0.8} />
      <mesh>
        <sphereGeometry args={[0.25, 16, 16]} />
        <meshBasicMaterial color="#22c55e" transparent opacity={opacity * 0.2} wireframe />
      </mesh>
    </mesh>
  );
}
