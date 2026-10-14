# Alternative UWP Shader Pipeline CI

The GitHub workflow `.github/workflows/xbox-shaders-alternative.yml` is a
**separate path** to build the WindowsStore x64-compatible Mesa
`spirv_to_dxil.dll` and repack the already compiled Eden emulator with both
the translator DLL and the Windows SDK's `dxil.dll`.

This workflow is independent of the original job that appeared to stall in
`Compile Mesa SPIR-V-to-DXIL UWP translator` (run `38587712454`).
It does not cancel or alter that job.

Key differences:
- Validates the official Mesa source archive by SHA-256.
- Restores caches for source files and, when available, intermediate builds.
- Runs compilation with a 30-second heartbeat: progress and the last
  lines of stdout/stderr are visible in the Actions job log.
- Kills the build if no log output appears for 16 minutes or total build
  exceeds 60 minutes. The job itself is limited to 85 minutes.
- Uploads the full compiler output to the
  `Eden-Xbox-Mesa-Shader-Build-Logs` artifact even if compilation fails.
- Checks shader exports (where dumpbin is available) and requires both
  shader DLLs inside the signed APPX packages. No artifact is labeled ready
  for installation if a required DLL was not packaged.
- Uses the successful executable from Actions run `38510035231` so the
  core does not need to rebuild on every shader attempt.

Outputs after a successful run:
- `Eden-Xbox-Normal-Shader-Fixed-APPX`
- `Eden-Xbox-Diagnostic-Shader-Fixed-APPX`

WARNING: Even with valid shader DLLs, successful compilation and packaging
do not prove Xbox One Fat graphics/feature-level compatibility. Confirm with
console test and logs. No keys, firmware or commercial game dumps are shipped.
