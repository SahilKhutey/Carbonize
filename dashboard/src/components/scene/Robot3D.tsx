import { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, Billboard } from '@react-three/drei';
import * as THREE from 'three';
import type { Robot } from '@/types';

interface Robot3DProps {
  robot: Robot;
  isSelected: boolean;
  onClick: () => void;
}

const statusColors = {
  idle: '#64748b',
  navigating: '#0ea5e9',
  capturing: '#22c55e',
  charging: '#fbbf24',
  error: '#ef4444',
  offline: '#475569',
};

export function Robot3D({ robot, isSelected, onClick }: Robot3DProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState(false);

  const statusColor = statusColors[robot.status];

  useFrame((state) => {
    if (!groupRef.current) return;
    const target = new THREE.Vector3(robot.position.x, robot.position.y, robot.position.z);
    groupRef.current.position.lerp(target, 0.1);

    if (robot.status === 'idle') {
      groupRef.current.position.y += Math.sin(state.clock.elapsedTime * 2) * 0.02;
    }
  });

  return (
    <group
      ref={groupRef}
      onClick={onClick}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <mesh castShadow position={[0, 0.1, 0]}>
        <cylinderGeometry args={[0.3, 0.3, 0.2, 16]} />
        <meshStandardMaterial color={statusColor} metalness={0.6} roughness={0.4} />
      </mesh>

      <mesh castShadow position={[0, 0.3, 0]}>
        <boxGeometry args={[0.4, 0.3, 0.5]} />
        <meshStandardMaterial color="#1e293b" metalness={0.7} roughness={0.3} />
      </mesh>

      <mesh castShadow position={[0, 0.6, 0]}>
        <cylinderGeometry args={[0.05, 0.05, 0.4, 8]} />
        <meshStandardMaterial color="#475569" />
      </mesh>

      <mesh castShadow position={[0, 0.85, 0.1]}>
        <boxGeometry args={[0.15, 0.1, 0.1]} />
        <meshStandardMaterial color="#0f172a" />
      </mesh>

      <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.32, 0.4, 32]} />
        <meshBasicMaterial color={statusColor} transparent opacity={0.4} />
      </mesh>

      {(isSelected || hovered) && (
        <mesh position={[0, 0.02, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.4, 0.5, 32]} />
          <meshBasicMaterial color={isSelected ? '#22c55e' : '#0ea5e9'} transparent opacity={0.8} />
        </mesh>
      )}

      <Billboard position={[0, 1.4, 0]}>
        <Text
          fontSize={0.2}
          color="#e2e8f0"
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.02}
          outlineColor="#0f172a"
        >
          {robot.name}
        </Text>
        <Text
          position={[0, -0.25, 0]}
          fontSize={0.12}
          color={statusColor}
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.01}
          outlineColor="#0f172a"
        >
          {robot.status} • {robot.battery.toFixed(0)}%
        </Text>
      </Billboard>

      {robot.status === 'capturing' && (
        <mesh position={[0, 0.5, 0]}>
          <coneGeometry args={[0.3, 1.2, 16, 1, true]} />
          <meshBasicMaterial color="#22c55e" transparent opacity={0.2} wireframe />
        </mesh>
      )}
    </group>
  );
}
