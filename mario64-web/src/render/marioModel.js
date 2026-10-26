// Mario's model, posed every frame from the game's animation data and his body
// state. The per-node behaviour ports the geo callbacks in src/game/mario_misc.c.

import * as THREE from 'three';
import { animValue } from '../rom/anims.js';
import { GeoModel, coss, setRotateXYZTranslate, setRotateZXYTranslate } from './geoModel.js';

// Geo callback addresses in the US ROM (ascending source order in mario_misc.c).
const GEO_FN = {
  0x802770a4: 'mirrorSetAlpha',
  0x80277150: 'standRun',
  0x802771bc: 'eyes',
  0x80277294: 'tiltTorso',
  0x802773a4: 'headRotation',
  0x802774f4: 'hand',
  0x802775cc: 'handFootScaler',
  0x802776d8: 'capEffect',
  0x80277740: 'capOnOff',
  0x80277824: 'wingCapWings',
  0x8027795c: 'handGrabPos',
  0x80277d6c: 'mirrorBackfaceCulling',
  0x802b1bb0: 'movePartFromParent',
};

const MARIO_BLINK = [1, 2, 1, 0, 1, 2, 1];
const ATTACK_SCALE = [10, 12, 16, 24, 10, 10, 10, 14, 20, 30, 10, 10, 10, 16, 20, 26, 26, 20];

// From include/sm64.h
const ACT_FLAG_SWIMMING_OR_FLYING = 1 << 28;
const ACT_FLAG_WATER_OR_TEXT = 1 << 29;
const ACT_WALKING = 0x04000440;
const ACT_BUTT_SLIDE = 0x00840452;
const ACT_HOLD_BUTT_SLIDE = 0x00840454;
const ACT_RIDING_SHELL_GROUND = 0x20810446;
const MARIO_HAND_FISTS = 0;
const MARIO_HAND_OPEN = 1;

const s16 = (v) => (v << 16) >> 16;
const lerpAngle = (a, b, t) => a + s16(b - a) * t;
const _scale = new THREE.Vector3();

export class MarioModel extends GeoModel {
  constructor(rom, animations) {
    super(rom, rom.layout.marioGeo, GEO_FN);
    this.root.name = 'Mario';
    this.animations = animations;
    this.areaUpdateCounter = 0;
    this.attackAnimCounter = -1;
    this.visualScale = 1; // a character drawn on this skeleton can be larger than Mario
  }

  // Only the normal-cap, high-poly Mario is needed: skip LOD and cap-effect variants.
  pruneCase(rt, i) {
    return i > 0 && (rt.fn === 'standRun' || rt.fn === 'capEffect');
  }

  /**
   * Pose the model.
   * @param m Mario state (marioObj.header.gfx, marioBodyState) — see src/mario
   * @param prev optional snapshot of the previous tick for interpolation
   * @param alpha interpolation factor between prev (0) and current (1)
   */
  update(m, prev = null, alpha = 1) {
    const gfx = m.marioObj.header.gfx;
    const ai = gfx.animInfo;
    const anim = this.animations[ai.animID];
    this.bodyState = m.marioBodyState;

    // Object transform (geo_process_object): a floor-aligned throwMatrix while
    // crawling/sliding, otherwise position + angles; then the squish scale.
    let pos = gfx.pos, angle = gfx.angle;
    if (prev) {
      pos = pos.map((v, i) => prev.pos[i] + (v - prev.pos[i]) * alpha);
      angle = angle.map((v, i) => lerpAngle(prev.angle[i], v, alpha));
    }
    const t = gfx.throwMatrix;
    if (t) {
      this.root.matrix.set(
        t[0][0], t[1][0], t[2][0], pos[0],
        t[0][1], t[1][1], t[2][1], pos[1],
        t[0][2], t[1][2], t[2][2], pos[2],
        0, 0, 0, 1);
    } else {
      setRotateZXYTranslate(this.root.matrix, pos, angle);
    }
    if (gfx.scale) this.root.matrix.scale(_scale.set(gfx.scale[0], gfx.scale[1], gfx.scale[2]));
    if (this.visualScale !== 1) this.root.matrix.scale(_scale.setScalar(this.visualScale));
    this.root.matrixWorldNeedsUpdate = true;

    // Animation globals (geo_set_animation_globals)
    let type = 'none';
    if (anim) {
      if (anim.flags & (1 << 3)) type = 'vertical';
      else if (anim.flags & (1 << 4)) type = 'lateral';
      else if (anim.flags & (1 << 6)) type = 'noTranslation';
      else type = 'translation';
    }
    const frame = ai.animFrame;
    // Blend from the previous tick's frame when the same animation advanced a little.
    const from = prev && prev.animID === ai.animID && anim && prev.animFrame !== frame &&
      Math.abs(prev.animFrame - frame) <= 2 ? prev.animFrame : null;
    this.anim = anim;
    this.animState = {
      type,
      attr: 0,
      mul: anim && anim.animYTransDivisor ? ai.animYTrans / anim.animYTransDivisor : 1,
      angle: (attr) => {
        const v = animValue(anim, frame, attr);
        return from === null ? v : lerpAngle(animValue(anim, from, attr), v, alpha);
      },
      trans: (attr) => {
        const v = animValue(anim, frame, attr);
        if (from === null) return v;
        const p = animValue(anim, from, attr);
        return p + (v - p) * alpha;
      },
    };
    this.areaUpdateCounter = m.areaUpdateCounter ?? this.areaUpdateCounter;
    this.poseNode(this.nodes[0], true);
  }

  // Mirrors geo_process_animated_part: the first part consumes translation attributes.
  poseAnimatedPart(rt) {
    const s = this.animState;
    const t = rt.geo.translation.slice();
    const r = [0, 0, 0];
    if (this.anim) {
      if (s.type === 'translation') {
        t[0] += s.trans(s.attr) * s.mul; s.attr += 2;
        t[1] += s.trans(s.attr) * s.mul; s.attr += 2;
        t[2] += s.trans(s.attr) * s.mul; s.attr += 2;
        s.type = 'rotation';
      } else if (s.type === 'lateral') {
        t[0] += s.trans(s.attr) * s.mul; s.attr += 4;
        t[2] += s.trans(s.attr) * s.mul; s.attr += 2;
        s.type = 'rotation';
      } else if (s.type === 'vertical') {
        s.attr += 2;
        t[1] += s.trans(s.attr) * s.mul; s.attr += 4;
        s.type = 'rotation';
      } else if (s.type === 'noTranslation') {
        s.attr += 6;
        s.type = 'rotation';
      }
      if (s.type === 'rotation') {
        r[0] = s.angle(s.attr); s.attr += 2;
        r[1] = s.angle(s.attr); s.attr += 2;
        r[2] = s.angle(s.attr); s.attr += 2;
      }
    }
    setRotateXYZTranslate(rt.group.matrix, t, r);
  }

  selectCase(rt) {
    const body = this.bodyState;
    const param = rt.geo.param;
    switch (rt.fn) {
      case 'eyes': // geo_switch_mario_eyes
        if (body.eyeState === 0) {
          const blinkFrame = ((param * 32 + this.areaUpdateCounter) >> 1) & 0x1f;
          return blinkFrame < 7 ? MARIO_BLINK[blinkFrame] : 0;
        }
        return body.eyeState - 1;
      case 'capOnOff': { // geo_switch_mario_cap_on_off: also toggles the wing-cap wings
        for (let n = rt.next; n; n = n.next) {
          if (n.geo.type === 'translateRotate') n.active = (body.capState & 2) !== 0;
        }
        return body.capState & 1;
      }
      case 'hand': // geo_switch_mario_hand
        if (body.handState === MARIO_HAND_FISTS) return (body.action & ACT_FLAG_SWIMMING_OR_FLYING) !== 0 ? 1 : 0;
        if (param === 0) return body.handState < 5 ? body.handState : MARIO_HAND_OPEN;
        return body.handState < 2 ? body.handState : MARIO_HAND_FISTS;
      default: // standRun / capEffect: always the high-poly normal model
        return 0;
    }
  }

  runAsm(rt) {
    const body = this.bodyState;
    const next = rt.next;
    if (!next) return;
    switch (rt.fn) {
      case 'tiltTorso': {
        const a = body.action;
        if (a !== ACT_BUTT_SLIDE && a !== ACT_HOLD_BUTT_SLIDE && a !== ACT_WALKING && a !== ACT_RIDING_SHELL_GROUND) {
          body.torsoAngle[0] = body.torsoAngle[1] = body.torsoAngle[2] = 0;
        }
        next.rotation = [body.torsoAngle[1], body.torsoAngle[2], body.torsoAngle[0]];
        break;
      }
      case 'headRotation':
        if (body.action & ACT_FLAG_WATER_OR_TEXT) {
          next.rotation = [body.headAngle[1], body.headAngle[2], body.headAngle[0]];
        } else {
          body.headAngle[0] = body.headAngle[1] = body.headAngle[2] = 0;
          next.rotation = [0, 0, 0];
        }
        break;
      case 'handFootScaler':
        next.scale = 1;
        if (rt.geo.param === body.punchState >> 6) {
          if (this.attackAnimCounter !== this.areaUpdateCounter && (body.punchState & 0x3f) > 0) {
            body.punchState -= 1;
            this.attackAnimCounter = this.areaUpdateCounter;
          }
          next.scale = ATTACK_SCALE[rt.geo.param * 6 + (body.punchState & 0x3f)] / 10;
        }
        break;
      case 'wingCapWings': {
        const c = this.areaUpdateCounter;
        const rotX = body.wingFlutter
          ? Math.trunc((coss((c & 7) << 13) + 1) * 6144)
          : Math.trunc((coss((c & 0xf) << 12) + 1) * 4096);
        next.rotation = [(rt.geo.param & 1) ? rotX : -rotX, 0, 0];
        break;
      }
      default:
        break;
    }
  }
}
