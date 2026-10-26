// Shared lights. The level and Mario's N64 shader only need the hemisphere + sun;
// the cow's physically based materials (fur sheen, satin, lacquer) also need an
// environment to reflect, or they render flat and grey.
import * as THREE from 'three';
import { RoomEnvironment } from '../../vendor/addons/environments/RoomEnvironment.js';

export function setupLighting(renderer, scene) {
  scene.add(new THREE.HemisphereLight(0xdff1ff, 0x4a5a32, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 1.6);
  sun.position.set(0.5, 1, 0.35);
  scene.add(sun);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.7;
  pmrem.dispose();
}
