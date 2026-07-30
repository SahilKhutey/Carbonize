import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface CO2FieldProps {
  density: number;
  concentration: number;
}

export function CO2Field({ density, concentration }: CO2FieldProps) {
  const meshRef = useRef<THREE.Group>(null);
  const opacity = Math.min(concentration / 1000, 0.4) * (density || 1.0);

  const particles = useMemo(() => {
    const arr = [];
    for (let i = 0; i < 200; i++) {
      arr.push({
        position: [
          (Math.random() - 0.5) * 30,
          Math.random() * 3,
          (Math.random() - 0.5) * 30,
        ] as [number, number, number],
        scale: 0.3 + Math.random() * 0.7,
        phase: Math.random() * Math.PI * 2,
      });
    }
    return arr;
  }, []);

  useFrame((state) => {
    if (!meshRef.current) return;
    meshRef.current.children.forEach((p, i) => {
      const phase = particles[i].phase;
      p.position.y = ((state.clock.elapsedTime * 0.5 + phase) % 3);
    });
  });

  if (opacity < 0.01) return null;

  return (
    <group ref={meshRef}>
      {particles.map((p, i) => (
        <mesh key={i} position={p.position} scale={p.scale}>
          <sphereGeometry args={[0.05, 8, 8]} />
          <meshBasicMaterial color="#86efac" transparent opacity={opacity * 0.4} />
        </mesh>
      ))}
    </group>
  );
}
