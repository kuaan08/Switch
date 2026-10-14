# Xbox One Fat port: evidence and gates

Target: original 2013 Xbox One, AMD Jaguar x64 + GCN, retail Developer Mode, UWP **Game Mode**.

Source: `JulianDr14/eden-xbox` branch `xbox` pinned to `bb7916615d706e66f761482d5b091557b4b13151` (2026-10-13). Upstream uses Eden's GPL-3.0-or-later license. The pinned submodule is **the full emulator source**; `Switch` is currently an integration/port overlay, not a completely independent in-tree fork.

## What upstream already provides

- Core WindowsStore/UWP x64 target `uwp-x64`.
- Dynarmic AppContainer JIT and UWP frontend.
- Direct3D 12 Feature Level 11_0 device creation.
- DirectX Shader Model **6.4 is currently hardcoded** in `src/video_core/renderer_d3d12/d3d12_shader_compiler.cpp`.
- Shader translation `spirv_to_dxil.dll` and DXIL validator `dxil.dll` must be packaged for guest graphics; absent DLLs trigger fallback rendering.
- Xbox controller and XAudio2.
- Memory guard and cache reclamation tuned for Series, not benchmarked on Xbox One.

## Device-specific risks

| Risk | Known status | Evidence/next action |
| --- | --- | --- |
| AMD Jaguar instruction set | No AVX2 (SSE4 variants and AVX available) | Build all code/dependencies with compatible ISA; do not inherit Series AVX2 prebuilts |
| Direct3D 12 | FL11_0 requested upstream | Verify activation, CreateDevice, command submission on real Xbox One |
| Shader Model 6.4 | Translator assumes 6.4 | Overlay logs negotiated device SM. If below 6.4, the translator and shader features need rework; lowering a constant is insufficient |
| CPU performance | Unknown | First test lightweight homebrew with JIT sentinel |
| Game Mode 5 GiB process budget | Documented UWP restriction | Keep allocations below budget; profile reserves + textures |
| AppContainer filesystem | UWP-limited | Use LocalState and Storage APIs; avoid desktop-only dependencies |
| Emulator gameplay | Not tested | Do not report working games until measured on this device |

## Source preparation

```bash
git clone --recurse-submodules https://github.com/kuaan08/Switch.git
cd Switch
python tools/xbox_one_overlay.py --check
python tools/xbox_one_overlay.py --apply
```

The overlay is safe to rerun and changes only a log probe in `upstream/eden-xbox/src/video_core/renderer_d3d12/d3d12_device.cpp`. Check `git -C upstream/eden-xbox diff` to review it. The first CI job verifies the pinned source and its patch anchor. No console is remotely available to this workflow.

## Windows build preflight

Use Visual Studio 2022 + C++ v143 UWP tools, Windows SDK, Perl, NASM, CMake, Ninja and `glslangValidator`. From the checked-out repo:

```bat
cd upstream\eden-xbox
tools\xbox\build-env.bat cmake --preset uwp-x64
tools\xbox\build-env.bat cmake --build --preset uwp-x64 --target eden-uwp
```

Upstream's full [build instructions](https://github.com/JulianDr14/eden-xbox/blob/xbox/docs/xbox/uwp_build.md) and [deployment guide](https://github.com/JulianDr14/eden-xbox/blob/xbox/docs/xbox/xbox_deploy.md) apply to their Series implementation. An executable and signed APPX are not yet validated here for Xbox One.

### Validation checklist

- [x] Identify a real GPL UWP emulation source and pin a known revision.
- [x] Establish a reproducible overlay for original Xbox One diagnosis.
- [ ] Confirm static CI job passes with submodule.
- [ ] Compile UWP x64 using WindowsStore CRT and no AVX2 dependency.
- [ ] Build/sign diagnostic APPX and install with VCLibs dependency.
- [ ] Launch in original Xbox One Fat in Game Mode.
- [ ] Verify D3D12 FL11_0 and shader model in logs.
- [ ] Verify guest JIT sentinel with freely distributable homebrew NRO.
- [ ] Implement genuine fallback for unsupported shader features if necessary.
- [ ] Profile CPU, GPU, memory and native game execution only after earlier gates.

Do not commit Nintendo keys, firmware, copyrighted game images, signing private keys, or certificate private keys.
