# Switch — Xbox One (2013) research port

Experimental **Nintendo Switch emulator port for the original Xbox One (2013)** in Developer Mode / UWP x64.

**Status: research/preflight only. No Xbox One gameplay or working package is claimed.**

## Source and license

This repository keeps the complete [Eden Xbox UWP port](https://github.com/JulianDr14/eden-xbox) as a **pinned Git submodule** under `upstream/eden-xbox`. The original work comes from the Eden project and contributors, licensed GPL-3.0-or-later. This repository's overlay is also GPL-3.0-or-later. Preserve upstream licenses, copyrights, and attribution when redistributing a complete build.

Unlike the upstream Xbox **Series** target, our hardware target is **Xbox One Fat / AMD Jaguar x64 / GCN / UWP Game Mode**. A successful Series X|S build does *not* establish Xbox One compatibility.

## Getting the code

```bash
git clone --recurse-submodules https://github.com/kuaan08/Switch.git
cd Switch
git submodule update --init --recursive
python tools/xbox_one_overlay.py --check
```

Submodule source is pinned to a reviewed commit; do not automatically track the moving upstream branch. To apply the first instrumentation overlay to a disposable source checkout:

```bash
python tools/xbox_one_overlay.py --apply
```

The overlay adds **capability logging only**. It does not implement Shader Model fallback or guarantee D3D12 will work on the 2013 model.

## First hardware gates

1. Run static overlay/source checks.
2. Establish UWP x64 build toolchain and a diagnostic app package (Windows 10/11 SDK and VS2022 UWP C++ workload).
3. Boot on a real Xbox One Fat in Dev Mode **Game** classification.
4. Collect `eden_uwp_diag.txt` and `eden_log.txt` and record D3D12 feature level, **supported shader model** and CPU instruction availability.
5. Only then implement verified GPU feature fallbacks and run homebrew NRO/JIT tests.
6. Commercial game compatibility/performance is a later, unproven milestone.

Eden's [upstream UWP build instructions](https://github.com/JulianDr14/eden-xbox/blob/xbox/docs/xbox/uwp_build.md) describe the environment:
```bat
cd upstream\eden-xbox
tools\xbox\build-env.bat cmake --preset uwp-x64
tools\xbox\build-env.bat cmake --build --preset uwp-x64 --target eden-uwp
```
**Do not ship keys, firmware or game dumps**. Use lawful homebrew for initial tests.

For known risks, progress and commands see [docs/XBOX_ONE_PLAN.md](docs/XBOX_ONE_PLAN.md). The GitHub Actions workflow currently runs static validation; optional manual Windows preflight is not a substitute for a console test.
