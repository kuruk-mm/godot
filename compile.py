import sys
import os

target = ''
n_proc = os.cpu_count()

if len(sys.argv) > 1:
    target = sys.argv[1]

if len(sys.argv) > 2:
    n_proc = max(min(n_proc, int(sys.argv[2])), 1)

options = [
    'x11_client',
    'x11_editor',
    'win64_client',
    'win64_editor',
    'win32_client',
    'osx_client',
    'osx_editor',
    'android_client',
    'web_client',
    'linux_headless',

    # Those are a shortcut
    'desktop',
    'desktop_client',
    'editor',
    'client',

    'fast_linux_editor_release',
]

while not target in options:
    print("- Available options: ", options)
    print("- Please choose target: ")
    target = input("\t")

target_list = filter(lambda x: x.endswith(target) and x != "editor" and x != "client", options)
if target == "desktop":
    target_list = filter(lambda x: x.startswith("x11") or x.startswith("win") or x.startswith("osx"), options)
if target == "desktop_client":
    target_list = filter(lambda x: x.startswith("x11") or x.startswith("win") or x.startswith("osx"), options)

base_command_editor = f"scons -j{n_proc} custom_modules=dcl-modules target=release_debug tools=yes"
base_command_client_debug = f"scons -j{n_proc} custom_modules=dcl-modules target=release_debug tools=no"
base_command_client_release = f"scons -j{n_proc} custom_modules=dcl-modules target=release tools=no"

# Linux Fast Compile 
# scons -j32 platform=x11 tools=yes target=release_debug use_llvm=yes use_lld=yes custom_modules=aesir-godot-modules

command_mapping = {
    # #################################
    'x11_client': [
        f"{base_command_client_debug} platform=x11 tools=no",
        "strip ./bin/godot.x11.opt.debug.64"
    ],
    'x11_editor': [
        f"{base_command_editor} platform=x11 tools=yes",
        "strip ./bin/godot.x11.opt.tools.64"
    ],
    # #################################
    'win64_client': [
        f"{base_command_client_debug} platform=windows tools=no bits=64",
        "strip ./bin/godot.windows.opt.debug.64.exe"
    ],
    'win32_client': [
        f"{base_command_client_debug} platform=windows tools=no bits=32",
        "strip ./bin/godot.windows.opt.debug.32.exe"
    ],
    'win64_editor': [
        f"{base_command_editor} platform=windows bits=64",
        "strip ./bin/godot.windows.opt.tools.64.exe"
    ],
    # #################################
    'osx_client': [
        f"{base_command_client_debug} platform=osx arch=x86_64",
        f"{base_command_client_debug} platform=osx arch=arm64",
        "lipo -create bin/godot.osx.opt.debug.x86_64 bin/godot.osx.opt.debug.arm64 -output bin/godot.osx.opt.debug.universal",
        "cp -r misc/dist/osx_template.app .",
        "mkdir -p osx_template.app/Contents/MacOS",
        "cp bin/godot.osx.opt.debug.universal osx_template.app/Contents/MacOS/godot_osx_release.64",
        "cp bin/godot.osx.opt.debug.universal osx_template.app/Contents/MacOS/godot_osx_debug.64",
        "chmod +x osx_template.app/Contents/MacOS/godot_osx*",
        "zip -q -9 -r osx.zip osx_template.app"
    ],
    'osx_editor': [
        f"{base_command_editor} platform=osx tools=yes "
    ],
    # #################################
    'android_client': [
        f"{base_command_client_debug} platform=android android_arch=armv7",
        f"{base_command_client_debug} platform=android android_arch=arm64v8",
        f"{base_command_client_debug} platform=android android_arch=x86",
        f"{base_command_client_debug} platform=android android_arch=x86_64",
        f"{base_command_client_release} platform=android android_arch=armv7",
        f"{base_command_client_release} platform=android android_arch=arm64v8",
        f"{base_command_client_release} platform=android android_arch=x86",
        f"{base_command_client_release} platform=android android_arch=x86_64",
        "cd platform/android/java && ./gradlew generateGodotTemplates",
    ],
    'web_client': [
        f"{base_command_client_debug} platform=javascript threads_enabled=yes"
    ],
    # #################################
    'linux_headless': [
        f"{base_command_client_debug} platform=server tools=yes",
        "strip ./bin/godot_server.x11.opt.tools.64"
    ],
    'fast_linux_editor_release': [
        f"scons -j{n_proc} platform=x11 tools=yes target=release_debug use_llvm=yes use_lld=yes custom_modules=dcl-modules"
    ]
}

target_list = list(target_list)
print("\n## Selected Options ## \n", target_list, n_proc)

for opt in target_list:
    print(f"#################### Running {opt}")
    commands = command_mapping[opt]
    for command in commands:
        print(f"$$$$$$$$$$$$$ Running command \n {command}")
        os.system(command)
