# SPDX-License-Identifier: GPL-2.0-only
"""Host checks for the retained module components."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "kernel/gpu_unlock"
# Generated or installed firmware lets the adapter run the whole unlock
# against mocked hardware.
ASSETS = next((path for path in (Path(os.environ.get("GPU_UNLOCK_ASSETS", "")),
                                 Path("/usr/lib/firmware/gpu-unlock/610.43.03"))
               if (path / "gsp_ga10x.bin").is_file()), None)

CASES = {
    "gfw_eval": ["gfw_eval.c"],
    "layout_610": ["layout_610.c"],
    "prep_610": ["layout_610.c", "prep_610.c"],
    "vbios_610": ["vbios_610.c"],
    "unlock_adapter": ["gfw_eval.c", "prep_610.c", "layout_610.c", "vbios_610.c"],
    "main": [],
}
# Tests that include a kernel source directly build it against a shim.
SHIMS = {
    "unlock_adapter": ["-I", str(ROOT / "tests/unlock_shim")],
    # The kernel build does not warn on sign-compare; match it for main.c.
    "main": ["-I", str(ROOT / "tests/main_shim"), "-pthread", "-Wno-sign-compare"],
}


class ComponentTests(unittest.TestCase):
    def test_components(self):
        with tempfile.TemporaryDirectory() as directory:
            # No define exercises the existing default build, not just an
            # explicit equivalent. Ti is always an opt-in build profile.
            for profile in (None, "0x2203"):
                for name, sources in CASES.items():
                    with self.subTest(profile=profile or "default", component=name):
                        output = Path(directory) / f"{name}-{profile or 'default'}"
                        shim = SHIMS.get(name, [])
                        defines = [f"-DGPU_UNLOCK_DEVICE_ID={profile}"] if profile else []
                        command = [os.environ.get("CC", "cc"), "-std=c11", "-Wall",
                                   "-Wextra", "-Werror", "-Wno-unused-parameter",
                                   *defines, "-I", str(KERNEL), *shim,
                                   *(str(KERNEL / source) for source in sources),
                                   str(ROOT / "tests" / f"test_{name}.c"),
                                   "-o", str(output)]
                        subprocess.run(command, check=True)
                        args = [str(output)]
                        if name == "unlock_adapter" and ASSETS:
                            args += ["-", str(ASSETS)]
                        result = subprocess.run(args, capture_output=True, text=True)
                        self.assertEqual(result.returncode, 0,
                                         (result.stdout + result.stderr)[-4000:])

    def test_unreviewed_device_profile_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [os.environ.get("CC", "cc"), "-std=c11", "-x", "c", "-c",
                 "-DGPU_UNLOCK_DEVICE_ID=0x2208", "-I", str(KERNEL),
                 "-o", str(Path(directory) / "unsupported.o"), "-"],
                input='#include "device_profile.h"\n',
                capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unsupported GPU_UNLOCK_DEVICE_ID", result.stderr)
