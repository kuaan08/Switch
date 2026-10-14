#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Validate a pinned upstream checkout and apply the Xbox One D3D12 diagnostic overlay.

This is an intentionally conservative instrumentation patch, NOT an implementation
of Shader Model fallback or proof of Xbox One compatibility.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM = ROOT / "upstream" / "eden-xbox"
PIN = "bb7916615d706e66f761482d5b091557b4b13151"
CPP = UPSTREAM / "src/video_core/renderer_d3d12/d3d12_device.cpp"
ANCHOR = (
    "    ThrowIfFailed(D3D12CreateDevice(nullptr, D3D_FEATURE_LEVEL_11_0, IID_PPV_ARGS(&device)),\n"
    '                  "D3D12CreateDevice");'
)
MARKER = "// XBOX_ONE_FAT_SHADER_MODEL_PROBE_V1"
PROBE = """
    // XBOX_ONE_FAT_SHADER_MODEL_PROBE_V1
    // The upstream DXIL translator targets Shader Model 6.4. Query, do not assume,
    // the actual runtime capability on an original Xbox One.
    D3D12_FEATURE_DATA_SHADER_MODEL xbox_one_sm{D3D_SHADER_MODEL_6_4};
    HRESULT xbox_one_sm_hr = device->CheckFeatureSupport(
        D3D12_FEATURE_SHADER_MODEL, &xbox_one_sm, sizeof(xbox_one_sm));
    // Older runtimes can reject the queried model instead of returning their maximum.
    if (xbox_one_sm_hr == E_INVALIDARG) {
        xbox_one_sm.HighestShaderModel = D3D_SHADER_MODEL_6_0;
        xbox_one_sm_hr = device->CheckFeatureSupport(
            D3D12_FEATURE_SHADER_MODEL, &xbox_one_sm, sizeof(xbox_one_sm));
    }
    if (SUCCEEDED(xbox_one_sm_hr)) {
        const auto model = static_cast<unsigned>(xbox_one_sm.HighestShaderModel);
        LOG_INFO(Render, "Xbox One diagnostic: highest D3D Shader Model {}.{}",
                 model >> 4, model & 0xF);
        if (xbox_one_sm.HighestShaderModel < D3D_SHADER_MODEL_6_4) {
            LOG_WARNING(Render,
                        "Xbox One diagnostic: shader model below 6.4; Eden DXIL translation "
                        "still targets 6.4 and needs a real compatibility implementation");
        }
    } else {
        LOG_WARNING(Render, "Xbox One diagnostic: shader model query failed (0x{:08X})",
                    static_cast<unsigned>(xbox_one_sm_hr));
    }
"""

def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="validate source, no mutation")
    mode.add_argument("--apply", action="store_true", help="apply idempotent instrumentation")
    args = parser.parse_args()
    if not (UPSTREAM / ".git").exists():
        sys.exit("Missing submodule. Run: git submodule update --init --recursive")
    head = subprocess.check_output(
        ["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != PIN:
        sys.exit(f"Upstream pin mismatch: expected {PIN}, got {head}")
    preset_path = UPSTREAM / "CMakePresets.json"
    presets = json.loads(preset_path.read_text(encoding="utf-8"))
    names = {p["name"] for p in presets.get("configurePresets", [])}
    if "uwp-x64" not in names:
        sys.exit("Upstream no longer exposes the uwp-x64 preset")
    if not CPP.is_file():
        sys.exit(f"Missing D3D12 file: {CPP}")
    text = CPP.read_text(encoding="utf-8")
    if text.count(MARKER) > 1:
        sys.exit("Duplicate diagnostic markers")
    if text.count(ANCHOR) != 1:
        sys.exit("D3D12CreateDevice anchor changed; manual rebase needed")
    if MARKER not in text and args.apply:
        text = text.replace(ANCHOR, ANCHOR + "\n" + PROBE, 1)
        CPP.write_text(text, encoding="utf-8", newline="\n")
        print("Applied D3D12 shader model capability probe")
    elif MARKER in text:
        print("Overlay already applied")
    else:
        print("Overlay anchor validated (no changes)")
    print("Pinned Eden Xbox source validated:", head)
    print("Xbox One support is NOT confirmed. Record real hardware logs.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
