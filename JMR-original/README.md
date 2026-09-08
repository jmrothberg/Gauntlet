# JMR's Original

[Play Gauntlet: The Third Encounter](https://jmrothberg.github.io/Gauntlet/JMR-original/)

This runs the **original Atari Lynx cartridge** through the WebAssembly build of libretro **Handy**, with a pinned, locally hosted EmulatorJS 4.2.3 frontend. It is not a JavaScript recreation of the game.

## Playing

Open the link and tap **PLAY GAUNTLET** once. The game image is already selected and the tap enables browser audio. There is no cartridge picker, ROM upload, BIOS upload, account or installation step.

The D-pad and **A**, **B**, **OPTION 1**, **OPTION 2**, **PAUSE** buttons remain visible outside the game display. Buttons support simultaneous movement and action, held presses, diagonals and release on pointer cancellation. The Help button explains the interface; Share opens the device share sheet or copies the play URL.

Keyboard: arrows = D-pad; Z = A; X = B; Q/W = Option 1/2; Enter = Pause. Reloading starts the console again; it does not ask for a cartridge.

Gauntlet uses the Lynx vertically. The launcher sets the Handy core's `handy_rot` option to `90`, rather than rotating just an HTML screenshot. The display area is fitted to the resulting 102:160 portrait aspect ratio in both device orientations.

## Verified original cartridge

`Gauntlet-The-Third-Encounter.lnx` is the non-overdump image from the supplied ZIP, unmodified:

- Size including LNX header: **131136 bytes**
- SHA-256: **21a83624a636fde4d6f6a01363ebd7644dd5c3da19013525aae11ff0aeb2eb60**
- Git blob SHA: **0243ea374e5eca1af945b110b9122473688dbde3**

The launcher checks the full size and SHA-256 before enabling the emulator, then loads the binary directly using a checksum-versioned URL. This avoids reusing the truncated cartridge cached by earlier builds. There is no application Base64 reconstruction or decompression step.

## Emulator and firmware

Runtime files live in `vendor/emulatorjs-4.2.3/`, including `cores/handy-wasm.data`, the frontend, decompression helper for the packaged emulator core, source files and license notices. The vendoring workflow downloads the official 4.2.3 release archive and verifies its published SHA-256 before extracting the Lynx runtime. The runtime manifest records individual hashes.

This Handy build boots the cartridge using its internal boot fallback, without a separately supplied Atari boot ROM. Earlier notes saying the missing external BIOS necessarily prevented this build from running were incorrect: the cartridge boot and character-selection screens were reproduced in browser execution tests without one.

The frontend has a small documented compatibility patch: missing support for optional screen recording must not crash startup. Recording controls are not exposed. See `vendor/emulatorjs-4.2.3/PATCHES.md`.

## Tests

`.github/workflows/verify-jmr-original.yml` validates the cartridge and executes `tools/verify_original.cjs` in Chromium and WebKit. It exercises button holds, D-pad release, rendering, Help and portrait/landscape layouts, and records screenshots, audio-buffer observations, errors and requested URLs. It also runs against the published GitHub Pages link. Check the latest workflow result rather than treating a successful file upload as proof the game works.

These are automated browser-engine tests, not a claim of physical iPad hardware testing or exhaustive completion of every game level. PNG sprite-sheet extraction is separate from this player; the running game uses the graphics within its original ROM.
