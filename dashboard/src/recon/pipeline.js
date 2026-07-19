/* Post-processing: ACES filmic tonemap + hardware MSAA. That's it.

   SSAOPass, UnrealBloomPass, and SMAAPass were all tried and dropped after empirical
   testing (pixel-counted against a direct renderer.render() baseline): SSAO/bloom washed
   the whole scene out to near-white, and SMAA alone still smeared the thin fat-line path/
   wireframe accents from ~140 visible pixels down to ~3 — an edge-detection blur pass is
   just a bad fit for content that's already only 1-2px wide. EffectComposer's own
   render-to-texture pipeline doesn't benefit from the renderer's `antialias` context flag
   either (that only applies when rendering straight to the canvas), so once every
   composer pass was gone there was nothing left EffectComposer was doing for us — hardware
   MSAA (set on the WebGLRenderer itself, see recon.js) plus the renderer's own tonemapping
   already covers what's left of the mission's "subtle post-processing" ask (ACES + AA),
   with none of the above failure modes. Contact shadow / bloom can be revisited later with
   passes authored for this scene's scale if the room ever needs them. */

import * as THREE from "three";

export function createPipeline(renderer, scene, camera) {
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  function render() {
    renderer.render(scene, camera);
  }

  return { render };
}
