
# pbrAudioBlender
## [v0.3.0] - 2026-11-04

### Added
- Integrated `pbrAudioRender`, `pbrAudioShaders`, and `pbrAudioDAW` (with TUI) into the ecosystem.
- Added Viewport Panel integration, 3D viewport widgets GUI, and `viewRay` graphical preview.
- Added new acoustic rendering output options (Ambisonic, Surround, Stereo, ProLogic II, and Binaural with HRTF processing).
- Added new nodes for acoustic node trees, including spatial frequency response nodes, frequency response chart/curve nodes, frequency response files nodes, and node frequency points graphs.
- Added preset acoustic materials and `AcousticMaterialPreviewNode`.
- Added new collision and render data exporters with mesh validation and fixing, plus per-collection properties in the collision panel.
- Added metadata editing methods in `StorageEngine` and bz2 compression/decompression for classes saved by `KleptoEntityStore`.
- Added helper for external NumPy loading and memory allocation tracking via Pympler.

### Changed
- Reworked `utils/frd_io.py` to parse `.cal`, `.csv`, and `.txt` files with cubic spline resampling.
- Handled track groups in processors to subdivide based on DAG node/edge goals.
- Switched `blosc2Backend` to parallel append and mmapped mode.
- Renamed relevant naming conventions from "Audio" to "Acoustic".

### Fixed
- Fixed Out-Of-Memory (OOM) issues in `ModalComposer`.
- Fixed data misalignments between signals and `ScoreEvent` from physics solver and rigid body modules.
- Fixed storage root paths, indentation errors, schema registration duplication, and missing module dependencies (`zarr`).
- Fixed material data export and ensured collision exporters discard non-connected nodes.
- Fixed single-object multi-collisions, mixed continuous contact, and fracture module integration.

-
