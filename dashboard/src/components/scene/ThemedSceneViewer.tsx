import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, Grid, Sky } from '@react-three/drei';
import { useEffect } from 'react';
import * as THREE from 'three';
import { useTheme } from '@/themes/ThemeProvider';
import { Robot3D } from './Robot3D';
import { CO2Field } from './CO2Field';
import { useSimulationStore } from '@/stores/simulationStore';

interface ThemedSceneViewerProps {
  showCO2?: boolean;
  showGrid?: boolean;
  showSky?: boolean;
}

export function ThemedSceneViewer({ showCO2 = true, showGrid = true, showSky = true }: ThemedSceneViewerProps) {
  const { theme } = useTheme();
  const robots = useSimulationStore((s) => Array.from(s.robots.values()));
  const simState = useSimulationStore((s) => s.simState);
  
  return (
    <Canvas
      shadows
      camera={{ position: [10, 8, 10], fov: 50 }}
      style={{ background: theme.colors.background }}
    >
      <SceneThemeApplier theme={theme} />
      
      <ambientLight intensity={0.4} color={theme.colors.sceneAmbient} />
      <directionalLight
        position={[10, 20, 5]}
        intensity={1}
        castShadow
        shadow-mapSize={[1024, 1024]}
      />
      
      {showSky && theme.mode === 'light' && (
        <Sky distance={450} sunPosition={[5, 10, 5]} inclination={0.5} />
      )}
      
      {showGrid && (
        <Grid
          args={[60, 60]}
          cellSize={1}
          cellThickness={0.5}
          cellColor={theme.colors.sceneGrid}
          sectionSize={5}
          sectionThickness={1}
          sectionColor={theme.colors.borderStrong}
          fadeDistance={50}
          fadeStrength={1}
        />
      )}
      
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
        <planeGeometry args={[60, 60]} />
        <meshStandardMaterial color={theme.colors.sceneGround} roughness={0.9} />
      </mesh>
      
      {showCO2 && simState && (
        <CO2Field density={simState.fog.density} concentration={simState.environment.co2Concentration} />
      )}
      
      {robots.map((r) => (
        <Robot3D
          key={r.id}
          robot={r}
          isSelected={r.id === useSimulationStore.getState().selectedRobotId}
          onClick={() => useSimulationStore.getState().setSelectedRobot(r.id)}
        />
      ))}
      
      <OrbitControls />
    </Canvas>
  );
}

function SceneThemeApplier({ theme }: { theme: any }) {
  const { scene, gl } = useThree();
  
  useEffect(() => {
    scene.background = new THREE.Color(theme.colors.background);
    scene.fog = new THREE.Fog(theme.colors.sceneFog, 30, 80);
    gl.setClearColor(theme.colors.background);
  }, [theme, scene, gl]);
  
  return null;
}
