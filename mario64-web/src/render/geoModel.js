// Generic Three.js model built from an SM64 geo layout + its display lists.
// Subclasses customise switch selection, geo callbacks and animation.

import * as THREE from 'three';
import { parseGeoLayout } from '../rom/geo.js';
import { createF3DState, cloneF3DState, runDisplayList, BatchSink } from '../rom/f3d.js';
import { createN64Material } from './combiner.js';

const TAU = Math.PI * 2;
export const sins = (a) => Math.sin(((a & 0xffff) / 65536) * TAU);
export const coss = (a) => Math.cos(((a & 0xffff) / 65536) * TAU);

/** mtxf_rotate_xyz_and_translate (animated parts), as a THREE.Matrix4. */
export function setRotateXYZTranslate(m, t, r) {
  const sx = sins(r[0]), cx = coss(r[0]);
  const sy = sins(r[1]), cy = coss(r[1]);
  const sz = sins(r[2]), cz = coss(r[2]);
  // SM64 stores row vectors (v' = v * M); THREE.Matrix4.set takes the transpose.
  m.set(
    cy * cz, sx * sy * cz - cx * sz, cx * sy * cz + sx * sz, t[0],
    cy * sz, sx * sy * sz + cx * cz, cx * sy * sz - sx * cz, t[1],
    -sy, sx * cy, cx * cy, t[2],
    0, 0, 0, 1);
  return m;
}

/** mtxf_rotate_zxy_and_translate (objects, rotation nodes). */
export function setRotateZXYTranslate(m, t, r) {
  const sx = sins(r[0]), cx = coss(r[0]);
  const sy = sins(r[1]), cy = coss(r[1]);
  const sz = sins(r[2]), cz = coss(r[2]);
  m.set(
    cy * cz + sx * sy * sz, -cy * sz + sx * sy * cz, cx * sy, t[0],
    cx * sz, cx * cz, -sx, t[1],
    -sy * cz + sx * cy * sz, sy * sz + sx * cy * cz, cx * cy, t[2],
    0, 0, 0, 1);
  return m;
}

export class GeoModel {
  /**
   * @param rom Rom with the needed segments loaded
   * @param geoAddr segmented address of the geo layout
   * @param fnNames map of geo callback address -> name (for subclasses)
   */
  constructor(rom, geoAddr, fnNames = {}) {
    this.rom = rom;
    this.fnNames = fnNames;
    this.textures = new Map();
    this.root = new THREE.Group();
    this.root.matrixAutoUpdate = false;
    this.nodes = [];
    this.animatedParts = []; // every animated part node, including all switch-case variants
    this.posedParts = []; // by animation slot: the variant posed most recently
    this.triangleCount = 0;

    const geo = parseGeoLayout(rom, geoAddr);
    this.sink = new BatchSink(rom);
    this.build(geo, this.root, createF3DState(), { animIndex: 0 });
    for (const tex of this.sink.textures.values()) this.makeTexture(tex);
    this.finishMeshes();
  }

  /** Override to skip building some switch cases entirely. */
  pruneCase(_rt, _index) {
    return false;
  }

  makeTexture(tex) {
    const t = new THREE.DataTexture(tex.rgba, tex.width, tex.height, THREE.RGBAFormat);
    const wrap = (cm) => (cm & 2 ? THREE.ClampToEdgeWrapping : cm & 1 ? THREE.MirroredRepeatWrapping : THREE.RepeatWrapping);
    t.wrapS = wrap(tex.cms);
    t.wrapT = wrap(tex.cmt);
    t.magFilter = THREE.LinearFilter;
    t.minFilter = THREE.LinearFilter;
    t.needsUpdate = true;
    this.textures.set(tex.key, t);
  }

  /**
   * Recursively build runtime nodes. F3D state flows through display lists in
   * render order, because SM64 relies on it (e.g. forearms inherit the arm's lights).
   * Returns the state after this subtree; the built node is left in this.lastBuilt.
   */
  build(geoNode, parentGroup, state, ctx) {
    const group = new THREE.Group();
    group.matrixAutoUpdate = false;
    parentGroup.add(group);
    const rt = {
      geo: geoNode, group, children: [], next: null, active: true, selected: 0,
      fn: this.fnNames[geoNode.fn] || null,
      scale: geoNode.scale ?? 1,
      rotation: (geoNode.rotation || [0, 0, 0]).slice(),
    };
    this.nodes.push(rt);

    if (geoNode.type === 'animatedPart') {
      rt.animIndex = ctx.animIndex++;
      this.animatedParts.push(rt);
    }
    if (geoNode.dl) {
      runDisplayList(this.rom, geoNode.dl, state, this.sink);
      group.userData.pending = this.sink.takeBatches().map((batch) => ({ batch, layer: geoNode.layer }));
    }

    if (geoNode.type === 'switch') {
      // Every case starts from the same F3D state and animation index; the state
      // after the switch is the one left by case 0.
      const entryIndex = ctx.animIndex;
      let exitState = null;
      let exitIndex = entryIndex;
      geoNode.children.forEach((child, i) => {
        if (this.pruneCase(rt, i)) { rt.children.push(null); return; }
        ctx.animIndex = entryIndex;
        const after = this.build(child, group, cloneF3DState(state), ctx);
        rt.children.push(this.lastBuilt);
        if (i === 0) { exitState = after; exitIndex = ctx.animIndex; }
      });
      ctx.animIndex = exitIndex;
      this.lastBuilt = rt;
      return exitState ?? state;
    }

    let prev = null;
    for (const child of geoNode.children) {
      state = this.build(child, group, state, ctx);
      const childRt = this.lastBuilt;
      if (prev) prev.next = childRt;
      rt.children.push(childRt);
      prev = childRt;
    }
    this.lastBuilt = rt;
    return state;
  }

  finishMeshes() {
    this.root.traverse((g) => {
      const pending = g.userData.pending;
      if (!pending) return;
      for (const { batch, layer } of pending) {
        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.Float32BufferAttribute(batch.positions, 3));
        geom.setAttribute('normal', new THREE.Float32BufferAttribute(batch.normals, 3));
        geom.setAttribute('color', new THREE.Float32BufferAttribute(batch.colors, 4));
        geom.setAttribute('uv', new THREE.Float32BufferAttribute(batch.uvs, 2));
        const tex = batch.material.texKey ? this.textures.get(batch.material.texKey) : null;
        const mesh = new THREE.Mesh(geom, createN64Material(batch.material, tex, layer));
        mesh.frustumCulled = false;
        this.triangleCount += batch.positions.length / 9;
        g.add(mesh);
      }
      delete g.userData.pending;
    });
  }

  /** Walk the tree in render order, updating local matrices and switch visibility. */
  poseNode(rt, visible) {
    if (!rt) return;
    const g = rt.geo;
    rt.group.visible = visible;
    if (!visible) return;

    switch (g.type) {
      case 'scale':
        rt.group.matrix.makeScale(rt.scale, rt.scale, rt.scale);
        break;
      case 'rotation':
        setRotateZXYTranslate(rt.group.matrix, [0, 0, 0], rt.rotation);
        break;
      case 'translateRotate':
      case 'translation':
        setRotateZXYTranslate(rt.group.matrix, g.translation || [0, 0, 0], rt.rotation);
        break;
      case 'animatedPart':
        this.poseAnimatedPart(rt);
        this.posedParts[rt.animIndex] = rt;
        break;
      case 'switch':
        rt.selected = this.selectCase(rt);
        if (rt.selected >= rt.children.length || !rt.children[rt.selected]) rt.selected = 0;
        break;
      case 'asm':
        this.runAsm(rt);
        rt.group.matrix.identity();
        break;
      default:
        break;
    }
    rt.group.matrixWorldNeedsUpdate = true;

    if (g.type === 'switch') {
      rt.children.forEach((c, i) => c && this.poseNode(c, i === rt.selected));
      return;
    }
    for (const c of rt.children) this.poseNode(c, c.active !== false);
  }

  poseAnimatedPart(rt) {
    setRotateXYZTranslate(rt.group.matrix, rt.geo.translation, [0, 0, 0]);
  }

  selectCase(rt) {
    return rt.selected;
  }

  runAsm(_rt) {}
}
