// Red coins and the Power Star, built from their geo layouts in the ROM.
import { GeoModel, setRotateZXYTranslate } from './geoModel.js';

/** A billboarded, spinning red coin (red_coin_geo: 8 animation states, 4 textures). */
export class RedCoinModel extends GeoModel {
  constructor(rom) {
    super(rom, rom.layout.redCoinGeo, {});
    this.frame = 0;
  }

  selectCase() {
    return this.frame & 7;
  }

  /** @param pos [x,y,z]; @param camera THREE.Camera (coins always face it) */
  update(pos, camera, counter) {
    this.frame = counter;
    const m = this.root.matrix;
    m.extractRotation(camera.matrixWorld);
    m.setPosition(pos[0], pos[1], pos[2]);
    this.root.matrixWorldNeedsUpdate = true;
    this.poseNode(this.nodes[0], true);
  }
}

/** The Power Star (star_geo): shiny environment-mapped body + eyes. */
export class StarModel extends GeoModel {
  constructor(rom) {
    super(rom, rom.layout.starGeo, {});
  }

  update(pos, yaw) {
    setRotateZXYTranslate(this.root.matrix, pos, [0, yaw, 0]);
    this.root.matrixWorldNeedsUpdate = true;
    this.poseNode(this.nodes[0], true);
  }
}
