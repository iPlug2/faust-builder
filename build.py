#!/usr/bin/env python3

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

def run_command(command, cwd=None, env=None):
    print(f"Running: {' '.join([str(c) for c in command])}")
    result = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()

def main():
    # Get the absolute path to the current directory
    current_dir = Path(os.getcwd()).resolve()
    
    build_dir = current_dir / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create headers directory and copy headers
    headers_dir = build_dir / "headers"
    headers_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the faust directory structure
    faust_dir = headers_dir / "faust"
    faust_dir.mkdir(parents=True, exist_ok=True)
    
    # Create dsp, gui, and midi subdirectories
    dsp_dir = faust_dir / "dsp"
    gui_dir = faust_dir / "gui"
    midi_dir = faust_dir / "midi"
    dsp_dir.mkdir(parents=True, exist_ok=True)
    gui_dir.mkdir(parents=True, exist_ok=True)
    midi_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy libfaust.h
    libfaust_header = current_dir / "faust" / "compiler" / "generator" / "libfaust.h"
    if libfaust_header.exists():
        shutil.copy(libfaust_header, dsp_dir / "libfaust.h")
    else:
        print(f"Warning: Header file {libfaust_header} not found")
    
    # Copy additional required headers
    architecture_dir = current_dir / "faust" / "architecture" / "faust"
    
    # Copy root faust headers
    faust_headers = {
        "export.h": architecture_dir / "export.h"
    }
    
    # Copy dsp headers
    dsp_headers = {
        "poly-dsp.h": architecture_dir / "dsp" / "poly-dsp.h",
        "dsp-combiner.h": architecture_dir / "dsp" / "dsp-combiner.h",
        "dsp-adapter.h": architecture_dir / "dsp" / "dsp-adapter.h",
        "proxy-dsp.h": architecture_dir / "dsp" / "proxy-dsp.h",
        "dsp.h": architecture_dir / "dsp" / "dsp.h",
        "interpreter-dsp.h": architecture_dir / "dsp" / "interpreter-dsp.h",
        "libfaust-signal.h": architecture_dir / "dsp" / "libfaust-signal.h",
        "libfaust-box.h": architecture_dir / "dsp" / "libfaust-box.h"
    }
    
    # Copy gui headers
    gui_headers = {
        "MetaDataUI.h": architecture_dir / "gui" / "MetaDataUI.h",
        "MidiUI.h": architecture_dir / "gui" / "MidiUI.h",
        "GUI.h": architecture_dir / "gui" / "GUI.h",
        "JSONUI.h": architecture_dir / "gui" / "JSONUI.h",
        "DecoratorUI.h": architecture_dir / "gui" / "DecoratorUI.h",
        "MapUI.h": architecture_dir / "gui" / "MapUI.h",
        "JSONControl.h": architecture_dir / "gui" / "JSONControl.h",
        "UI.h": architecture_dir / "gui" / "UI.h",
        "JSONUIDecoder.h": architecture_dir / "gui" / "JSONUIDecoder.h",
        "CGlue.h": architecture_dir / "gui" / "CGlue.h",
        "meta.h": architecture_dir / "gui" / "meta.h",
        "SimpleParser.h": architecture_dir / "gui" / "SimpleParser.h",
        "CInterface.h": architecture_dir / "gui" / "CInterface.h",
        "PathBuilder.h": architecture_dir / "gui" / "PathBuilder.h",
        "ValueConverter.h": architecture_dir / "gui" / "ValueConverter.h",
        "ring-buffer.h": architecture_dir / "gui" / "ring-buffer.h"
    }
    
    # Copy midi headers
    midi_headers = {
        "midi.h": architecture_dir / "midi" / "midi.h",
        "iplug2-midi.h": architecture_dir / "midi" / "iplug2-midi.h"
    }
    
    # Copy all headers
    for header_name, header_path in {**faust_headers, **dsp_headers, **gui_headers, **midi_headers}.items():
        if header_path.exists():
            if header_name in faust_headers:
                target_dir = faust_dir
            elif header_name in dsp_headers:
                target_dir = dsp_dir
            elif header_name in gui_headers:
                target_dir = gui_dir
            else:  # midi headers
                target_dir = midi_dir
            shutil.copy(header_path, target_dir / header_name)
        else:
            print(f"Warning: Header file {header_path} not found")
    
    # Define platforms to build for
    platforms = [
        {
            "name": "ios",
            "sdk": "iphoneos",
            "platform": "iphoneos",
            "target": "arm64-apple-ios",
            "arch": "arm64",
            "min_version": "14.0"
        },
        {
            "name": "ios_simulator",
            "sdk": "iphonesimulator",
            "platform": "iphonesimulator",
            "target": "arm64-apple-ios-simulator",
            "arch": "arm64",
            "min_version": "14.0"
        },
        {
            "name": "xros",
            "sdk": "xros",
            "platform": "xros",
            "target": "arm64-apple-xros",
            "arch": "arm64",
            "min_version": "1.0"
        },
        {
            "name": "xros_simulator",
            "sdk": "xrsimulator",
            "platform": "xrsimulator",
            "system_name": "xros",
            "target": "arm64-apple-xros-simulator",
            "arch": "arm64",
            "min_version": "1.0"
        },
        {
            "name": "macos_arm64",
            "sdk": "macosx",
            "platform": "macosx",
            "target": "arm64-apple-macos",
            "arch": "arm64",
            "min_version": "11.0",
            "is_macos": True
        },
        {
            "name": "macos_x86_64",
            "sdk": "macosx",
            "platform": "macosx",
            "target": "x86_64-apple-macos",
            "arch": "x86_64",
            "min_version": "11.0",
            "is_macos": True
        },
    ]
    
    # Build for each platform
    for platform in platforms:
        print(f"Building for {platform['name']}...")
        
        # Create platform-specific build directory
        platform_build_dir = build_dir / platform["name"]
        platform_build_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a temporary CMake cache file for this platform
        arch = platform['arch']
        is_macos = platform.get('is_macos', False)
        cmake_cache_file = platform_build_dir / "platform.cmake"
        with open(cmake_cache_file, "w") as f:
            f.write(f"set(CMAKE_OSX_SYSROOT \"{platform['sdk']}\" CACHE STRING \"\" FORCE)\n")
            f.write(f"set(CMAKE_OSX_ARCHITECTURES \"{arch}\" CACHE STRING \"\" FORCE)\n")
            f.write(f"set(CMAKE_OSX_DEPLOYMENT_TARGET \"{platform['min_version']}\" CACHE STRING \"\" FORCE)\n")
            f.write(f"set(CMAKE_SYSTEM_PROCESSOR \"{arch}\" CACHE STRING \"\" FORCE)\n")
            f.write(f"set(CMAKE_C_COMPILER \"clang\" CACHE STRING \"\" FORCE)\n")
            f.write(f"set(CMAKE_CXX_COMPILER \"clang++\" CACHE STRING \"\" FORCE)\n")

            if is_macos:
                # macOS-specific settings - simpler configuration
                f.write(f"set(CMAKE_SYSTEM_NAME \"Darwin\" CACHE STRING \"\" FORCE)\n")
                # Override the IOS flag from backend.cmake
                f.write(f"set(IOS OFF CACHE BOOL \"Compiles for iOS\" FORCE)\n")
            else:
                # iOS/visionOS-specific settings
                f.write(f"set(CMAKE_XCODE_EFFECTIVE_PLATFORMS \"{platform['platform']}\" CACHE STRING \"\" FORCE)\n")
                system_name = platform.get('system_name', platform['platform'])
                f.write(f"set(CMAKE_SYSTEM_NAME \"{system_name}\" CACHE STRING \"\" FORCE)\n")
                # Add these lines to fix the libtool issue
                f.write(f"set(CMAKE_XCODE_ATTRIBUTE_ONLY_ACTIVE_ARCH \"NO\" CACHE STRING \"\" FORCE)\n")
                f.write(f"set(CMAKE_XCODE_ATTRIBUTE_ENABLE_BITCODE \"NO\" CACHE STRING \"\" FORCE)\n")
                f.write(f"set(CMAKE_XCODE_ATTRIBUTE_VALID_ARCHS \"{arch}\" CACHE STRING \"\" FORCE)\n")
                f.write(f"set(CMAKE_XCODE_ATTRIBUTE_ARCHS \"{arch}\" CACHE STRING \"\" FORCE)\n")
                f.write(f"set(CMAKE_XCODE_ATTRIBUTE_SKIP_INSTALL \"YES\" CACHE STRING \"\" FORCE)\n")
                f.write(f"set(CMAKE_XCODE_ATTRIBUTE_BUILD_LIBRARY_FOR_DISTRIBUTION \"YES\" CACHE STRING \"\" FORCE)\n")
                # Fix for libtool issue - don't pass -arch to libtool
                f.write(f"set(CMAKE_XCODE_ATTRIBUTE_OTHER_LDFLAGS \"-isysroot $(SDKROOT) -target {platform['target']}\" CACHE STRING \"\" FORCE)\n")
                f.write(f"set(CMAKE_XCODE_ATTRIBUTE_OTHER_CFLAGS \"-isysroot $(SDKROOT) -target {platform['target']}\" CACHE STRING \"\" FORCE)\n")
                f.write(f"set(CMAKE_XCODE_ATTRIBUTE_OTHER_CPLUSPLUSFLAGS \"-isysroot $(SDKROOT) -target {platform['target']}\" CACHE STRING \"\" FORCE)\n")

            # Set output directories to prevent building in the source directory
            f.write(f"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY \"{platform_build_dir}/bin\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_LIBRARY_OUTPUT_DIRECTORY \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE \"{platform_build_dir}/bin\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO \"{platform_build_dir}/bin\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELWITHDEBINFO \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL \"{platform_build_dir}/bin\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_MINSIZEREL \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG \"{platform_build_dir}/bin\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_DEBUG \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")
            f.write(f"set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY_DEBUG \"{platform_build_dir}/lib\" CACHE PATH \"\" FORCE)\n")

        # Create CMake build directory
        cmake_build_dir = platform_build_dir / "cmake_build"
        cmake_build_dir.mkdir(parents=True, exist_ok=True)

        # Use different generator for macOS vs iOS/visionOS
        generator = "Unix Makefiles" if is_macos else "Xcode"

        # Run CMake with absolute paths
        cmake_args = [
            "cmake",
            "-C", str(current_dir / "backend.cmake"),
            "-C", str(current_dir / "target.cmake"),
            "-C", str(cmake_cache_file),
            "-G", generator,
            "-DCMAKE_BUILD_TYPE=MinSizeRel",
            "-DINCLUDE_STATIC=ON",
            "-DINCLUDE_EXECUTABLE=OFF",
            "-DINCLUDE_DYNAMIC=OFF",
            "-DINCLUDE_OSC=OFF",
            "-DINCLUDE_HTTP=OFF",
            "-DINCLUDE_ITP=OFF",
            "-DINCLUDE_EMCC=OFF",
            "-DINCLUDE_WASM_GLUE=OFF",
            "-DLINK_LLVM_STATIC=ON",
            "-DINCLUDE_LLVM_STATIC_IN_ARCHIVE=ON",
        ]
        # For macOS, disable iOS mode
        if is_macos:
            cmake_args.append("-DIOS=OFF")
        cmake_args.append(str(current_dir / "faust" / "build"))
        run_command(cmake_args, cwd=cmake_build_dir)

        # Build the static library - different args for different generators
        if is_macos:
            run_command([
                "cmake",
                "--build", str(cmake_build_dir),
                "--target", "staticlib",
                "--", "-j", "10"
            ])
        else:
            run_command([
                "cmake",
                "--build", str(cmake_build_dir),
                "--target", "staticlib",
                "--config", "MinSizeRel",
                "--", "-j", "10"
            ])
        
        # Install the static library
        # install_dir = platform_build_dir / "install"
        # run_command([
        #     "cmake", 
        #     "--install", str(cmake_build_dir), 
        #     "--config", "MinSizeRel",
        #     "--prefix", str(install_dir)
        # ])
        
        # Copy the static library to the platform directory
        # static_lib_path = install_dir / "lib" / "libfaust.a"
        # if static_lib_path.exists():
        #     shutil.copy(static_lib_path, platform_build_dir / "libfaust.a")
        # else:
        #     # Try to find the library in the build directory
        #     build_lib_path = cmake_build_dir / "lib" / "MinSizeRel" / "libfaust.a"
        #     if build_lib_path.exists():
        #         shutil.copy(build_lib_path, platform_build_dir / "libfaust.a")
        #     else:
        #         print(f"Warning: Static library not found at {static_lib_path} or {build_lib_path}")
    
    # Create a simple script to build the XCFramework - with unique library names
    temp_dir = tempfile.mkdtemp()

    # Copy libraries with unique names
    ios_unique = Path(temp_dir) / "ios_libfaust.a"
    ios_sim_unique = Path(temp_dir) / "ios_sim_libfaust.a"
    xros_unique = Path(temp_dir) / "xros_libfaust.a"
    xros_sim_unique = Path(temp_dir) / "xros_sim_libfaust.a"
    macos_unique = Path(temp_dir) / "macos_libfaust.a"

    shutil.copy(build_dir / "ios" / "lib" / "libfaust.a", ios_unique)
    shutil.copy(build_dir / "ios_simulator" / "lib" / "libfaust.a", ios_sim_unique)
    shutil.copy(build_dir / "xros" / "lib" / "libfaust.a", xros_unique)
    shutil.copy(build_dir / "xros_simulator" / "lib" / "libfaust.a", xros_sim_unique)

    # Create universal macOS binary using lipo
    print("Creating universal macOS binary...")
    run_command([
        "lipo", "-create",
        str(build_dir / "macos_arm64" / "lib" / "libfaust.a"),
        str(build_dir / "macos_x86_64" / "lib" / "libfaust.a"),
        "-output", str(macos_unique)
    ])

    xcframework_path = build_dir / "LibFaust.xcframework"
    if xcframework_path.exists():
        shutil.rmtree(xcframework_path)

    # Execute xcodebuild directly
    run_command([
        "xcodebuild", "-create-xcframework",
        "-library", str(ios_unique), "-headers", str(headers_dir),
        "-library", str(ios_sim_unique), "-headers", str(headers_dir),
        "-library", str(xros_unique), "-headers", str(headers_dir),
        "-library", str(xros_sim_unique), "-headers", str(headers_dir),
        "-library", str(macos_unique), "-headers", str(headers_dir),
        "-output", str(xcframework_path)
    ])

    # Code sign the XCFramework (ad-hoc)
    print("Code signing the XCFramework...")
    run_command([
        "codesign", "--force", "--deep", "--sign", "-", str(xcframework_path)
    ])
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    # Copy headers to include directory
    include_dir = build_dir / "include"
    include_dir.mkdir(parents=True, exist_ok=True)
    
    if libfaust_header.exists():
        # Create the faust/dsp directory structure
        faust_dsp_dir = include_dir / "faust" / "dsp"
        faust_dsp_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(libfaust_header, faust_dsp_dir / "libfaust.h")
    
    print(f"\n=== Build Complete ===\n")
    print(f"XCFramework created at: {build_dir}/LibFaust.xcframework")
    print(f"Header files copied to: {include_dir}")

if __name__ == "__main__":
    main()
