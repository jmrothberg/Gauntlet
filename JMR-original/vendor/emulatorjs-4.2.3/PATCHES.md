# EmulatorJS 4.2.3 + Handy

Runtime copied from the checksum-verified upstream 4.2.3 release. Only Handy core binaries are retained. Original source files and license notices from the release are included.

JMR compatibility change: guard `MediaRecorder.isTypeSupported(x)` with `typeof MediaRecorder!=="undefined"`. An optional screen-recording API must not prevent starting a cartridge. Recording controls are disabled by the launcher. Both the minified runtime and unminified emulator source receive the same change. The workflow in `.github/workflows/vendor-handy.yml` reproduces the patch; `manifest.json` records upstream and served hashes.

Upstream frontend source: https://github.com/EmulatorJS/EmulatorJS/tree/v4.2.3
Handy source: https://github.com/libretro/libretro-handy
Core build information: `cores/reports/handy.json`.
