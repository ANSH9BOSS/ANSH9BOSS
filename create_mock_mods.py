#!/usr/bin/env python3
import os
import zipfile
from pathlib import Path

TEST_DIR = Path("/home/ubuntu/ansh9boss/test_mods")
TEST_DIR.mkdir(exist_ok=True)

def create_zip(filename, file_contents_dict):
    filepath = TEST_DIR / filename
    with zipfile.ZipFile(filepath, "w") as z:
        for fname, content in file_contents_dict.items():
            z.writestr(fname, content)
    print(f"Created mock mod: {filepath}")

# 1. Clean Mod
create_zip("legit-mod-v1.jar", {
    "fabric.mod.json": '{"id": "examplemod", "version": "1.0.0", "name": "Example Mod"}',
    "com/example/ExampleMod.class": b"legit java byte code structure representation"
})

# 2. Filename Match (Layer 1 Wurst)
create_zip("Wurst-Client-v1.12.jar", {
    "META-INF/MANIFEST.MF": "Manifest-Version: 1.0\nCreated-By: Wurst\n",
    "wurst/WurstClient.class": b"Wurst client entrypoint"
})

# 3. Manifest / Package Match (Layer 2 Meteor)
create_zip("meteor-addon-v2.jar", {
    "fabric.mod.json": '{"id": "meteor-helper", "version": "2.0", "custom": {"meteorclient": "addon"}}',
    "net/meteorclient/addon/Helper.class": b"addon helpers"
})

# 4. Cheat Strings Match (Layer 3 Cheat Strings)
# We will write aimbot, killaura, esp to check Layer 3 triggers
create_zip("fancy-particles.jar", {
    "fabric.mod.json": '{"id": "fancy-particles", "version": "1.1.2"}',
    "net/particles/Particles.class": b"some byte code content containing aimbot and killaura and esp signatures"
})

# 5. Obfuscated Mod (Heuristic trigger: >75% short names)
obf_files = {
    "fabric.mod.json": '{"id": "hidden-mod", "version": "0.1"}'
}
for i in range(15):
    char = chr(97 + i) # a, b, c...
    obf_files[f"net/hidden/{char}.class"] = b"small obfuscated class bytecode content"

create_zip("obfuscated-protected.jar", obf_files)

# 6. Corrupt / Protected Mod (Triggers unzip failure)
corrupt_filepath = TEST_DIR / "corrupt-headers-mod.jar"
with open(corrupt_filepath, "wb") as f:
    f.write(b"PK\x03\x04 corrupt zip payload header error simulation")
print(f"Created mock mod: {corrupt_filepath}")

print("\nMock mods generated successfully.")
