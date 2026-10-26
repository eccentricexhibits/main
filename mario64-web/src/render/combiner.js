// Turns an N64 RDP colour-combiner setting into a Three.js ShaderMaterial.
// The combiner computes (A - B) * C + D separately for colour and alpha; we only
// emulate 1-cycle mode, which is what Mario's model uses.

import * as THREE from 'three';

const COLOR_A = ['vec3(0.0)', 'texel0.rgb', 'texel0.rgb', 'prim.rgb', 'shade.rgb', 'env.rgb', 'vec3(1.0)', 'vec3(0.5)'];
const COLOR_B = ['vec3(0.0)', 'texel0.rgb', 'texel0.rgb', 'prim.rgb', 'shade.rgb', 'env.rgb', 'vec3(0.5)', 'vec3(0.0)'];
const COLOR_C = ['vec3(0.0)', 'texel0.rgb', 'texel0.rgb', 'prim.rgb', 'shade.rgb', 'env.rgb', 'vec3(1.0)', 'vec3(0.0)',
  'vec3(texel0.a)', 'vec3(texel0.a)', 'vec3(prim.a)', 'vec3(shade.a)', 'vec3(env.a)', 'vec3(1.0)', 'vec3(1.0)', 'vec3(0.0)'];
const COLOR_D = ['vec3(0.0)', 'texel0.rgb', 'texel0.rgb', 'prim.rgb', 'shade.rgb', 'env.rgb', 'vec3(1.0)', 'vec3(0.0)'];
const ALPHA_ABD = ['0.0', 'texel0.a', 'texel0.a', 'prim.a', 'shade.a', 'env.a', '1.0', '0.0'];
const ALPHA_C = ['1.0', 'texel0.a', 'texel0.a', 'prim.a', 'shade.a', 'env.a', '1.0', '0.0'];

const pick = (table, i) => table[i] ?? table[table.length - 1];

export function decodeCombine([w0, w1]) {
  return {
    a: (w0 >> 20) & 0xf, c: (w0 >> 15) & 0x1f, Aa: (w0 >> 12) & 7, Ac: (w0 >> 9) & 7,
    b: (w1 >>> 28) & 0xf, d: (w1 >> 15) & 7, Ab: (w1 >> 12) & 7, Ad: (w1 >> 9) & 7,
  };
}

export function combinerExpressions(combine) {
  const m = decodeCombine(combine);
  const color = `(${pick(COLOR_A, m.a)} - ${pick(COLOR_B, m.b)}) * ${pick(COLOR_C, m.c)} + ${pick(COLOR_D, m.d)}`;
  const alpha = `(${ALPHA_ABD[m.Aa]} - ${ALPHA_ABD[m.Ab]}) * ${ALPHA_C[m.Ac]} + ${ALPHA_ABD[m.Ad]}`;
  const usesTexture = /texel0/.test(color + alpha);
  return { color, alpha, usesTexture };
}

const VERTEX = /* glsl */ `
  attribute vec4 color;
  uniform bool uLighting;
  uniform vec3 uAmbient;
  uniform vec3 uDiffuse;
  uniform vec3 uLightDir; // view space
  uniform bool uTexGen;
  uniform vec2 uTexGenScale;
  varying vec4 vShade;
  varying vec2 vUv;
  void main() {
    vUv = uv;
    if (uTexGen) {
      // G_TEXTURE_GEN: spherical environment mapping from the view-space normal
      vec3 nv = normalize(normalMatrix * normal);
      vUv = (nv.xy * 0.5 + 0.5) * uTexGenScale;
    }
    if (uLighting) {
      vec3 n = normalize(normalMatrix * normal);
      vec3 lit = uAmbient + uDiffuse * max(dot(n, uLightDir), 0.0);
      vShade = vec4(min(lit, vec3(1.0)), color.a);
    } else {
      vShade = color;
    }
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

function fragment(expr, alphaTest) {
  return /* glsl */ `
    uniform sampler2D uTex;
    uniform bool uHasTex;
    uniform vec4 uPrim;
    uniform vec4 uEnv;
    varying vec4 vShade;
    varying vec2 vUv;
    void main() {
      vec4 texel0 = uHasTex ? texture2D(uTex, vUv) : vec4(1.0);
      vec4 shade = vShade;
      vec4 prim = uPrim;
      vec4 env = uEnv;
      vec3 rgb = clamp(${expr.color}, 0.0, 1.0);
      float a = clamp(${expr.alpha}, 0.0, 1.0);
      ${alphaTest ? 'if (a < 0.5) discard;' : ''}
      gl_FragColor = vec4(rgb, a);
    }
  `;
}

const rgb = (c) => new THREE.Vector3(c[0] / 255, c[1] / 255, c[2] / 255);
const rgba = (c) => new THREE.Vector4(c[0] / 255, c[1] / 255, c[2] / 255, c[3] / 255);

/**
 * @param material batch material from f3d.js BatchSink
 * @param texture THREE.Texture | null
 * @param layer SM64 drawing layer (1 opaque, 4 alpha-tested, 5 translucent)
 */
export function createN64Material(material, texture, layer) {
  const expr = combinerExpressions(material.combine);
  const dir = new THREE.Vector3(...material.lightDir);
  if (dir.lengthSq() === 0) dir.set(1, 1, 1);
  dir.normalize();
  const translucent = layer >= 5;
  const mat = new THREE.ShaderMaterial({
    uniforms: {
      uTex: { value: texture },
      uHasTex: { value: !!texture && expr.usesTexture },
      uPrim: { value: rgba(material.primColor) },
      uEnv: { value: rgba(material.envColor) },
      uLighting: { value: material.lighting },
      uAmbient: { value: rgb(material.ambient) },
      uDiffuse: { value: rgb(material.diffuse) },
      uLightDir: { value: dir },
      uTexGen: { value: material.texgen },
      uTexGenScale: { value: new THREE.Vector2(...material.texGenScale) },
    },
    vertexShader: VERTEX,
    fragmentShader: fragment(expr, layer === 4),
    side: material.cullBack ? THREE.FrontSide : THREE.DoubleSide,
    transparent: translucent,
    depthWrite: !translucent,
  });
  return mat;
}
