import { useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { Robot } from '@/types';

interface PathTrailsProps {
  robots: Robot[];
}

export function PathTrails({ robots }: PathTrailsProps) {
  return (
    <group>
      {robots.map((r) => (
        <PathLine key={r.id} robotId={r.id} currentPos={r.position} color={r.status === 'navigating' ? '#0ea5e9' : '#475569'} />
      ))}
    </group>
  );
}

function PathLine({ currentPos, color }: { robotId: string; currentPos: { x: number; y: number; z: number }; color: string }) {
  const lineRef = useRef<THREE.Line>(null);
  const trailRef = useRef<Array<{ x: number; y: number; z: number }>>([]);

  useEffect(() => {
    trailRef.current.push({ ...currentPos });
    if (trailRef.current.length > 50) trailRef.current.shift();
  }, [currentPos.x, currentPos.y, currentPos.z]);

  useFrame(() => {
    if (!lineRef.current || trailRef.current.length < 2) return;
    const positions = new Float32Array(trailRef.current.flatMap((p) => [p.x, p.y + 0.05, p.z]));
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    lineRef.current.geometry = geometry;
  });

  return (
    <line ref={lineRef as any}>
      <bufferGeometry />
      <lineBasicMaterial color={color} transparent opacity={0.6} />
    </line>
  );
}
