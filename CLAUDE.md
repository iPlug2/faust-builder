# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Build system that packages libfaust (the [Faust](https://github.com/grame-cncm/faust) DSP compiler) as an Apple `XCFramework` of static libraries. The Faust source is a Git submodule; everything else in this repo is the cross-compilation harness around Faust's own CMake build.

Consumer of the output is iPlug2 — hence the `iplug2-midi.h` header and the `iPlug2/faust` fork.

## Build

```bash
./build.py          # or: python3 build.py
```

Output: `build/LibFaust.xcframework` (ad-hoc code signed) plus `build/headers/`, `build/include/` and `build/libraries/faust/` (the Faust standard libraries from the `faust/libraries` submodule, which the interpreter needs at runtime; released as `faust-libraries.tar.gz`).

There is no test suite and no lint config. Verification is "does the XCFramework build and contain all five slices":

```bash
xcodebuild -create-xcframework ...   # done by build.py
plutil -p build/LibFaust.xcframework/Info.plist
lipo -info build/LibFaust.xcframework/macos-arm64_x86_64/macos_libfaust.a
```

### Build gotchas

- **`build.py` wipes `build/` on every run** — there is no incremental mode and no way to build a single platform. A full run compiles the Faust compiler six times and takes a long time. To iterate on one platform, re-run `cmake --build` by hand inside `build/<platform>/cmake_build` (the generated `platform.cmake` cache preload is preserved there).
- **`run_command()` swallows failures**: it prints stderr and returns `None` instead of raising. A failed `cmake` configure or build does *not* stop the script — the run continues and dies much later with a `FileNotFoundError` on `shutil.copy` of a missing `libfaust.a`. When a build breaks, scroll back to the *first* `Error:` line, not the traceback.
- Public headers are hand-enumerated in the dicts at the top of `build.py` (`faust_headers`, `dsp_headers`, `gui_headers`, `midi_headers`). New headers required by consumers must be added there or they silently won't ship (only a `Warning:` is printed).

## Architecture

Three CMake cache-preload files are fed to Faust's own `faust/build/CMakeLists.txt` via `-C`, in order, followed by `-D` command-line overrides (which win over all preloads):

1. `backend.cmake` — which code generators get compiled in. Currently only `CPP_BACKEND ON` and `INTERP_BACKEND STATIC`; everything else (LLVM, WASM, Rust, …) is `OFF` to keep the archive small. Also sets `IOS ON`.
2. `target.cmake` — artifact selection (no executable, no OSC/HTTP/machine libs).
3. `build/<platform>/platform.cmake` — generated per-platform by `build.py`: sysroot, arch, deployment target, output dirs, and (for non-macOS) the Xcode attributes.

Note `target.cmake` sets `INCLUDE_STATIC OFF` but `build.py` passes `-DINCLUDE_STATIC=ON` on the command line, which takes precedence. Don't "fix" the apparent contradiction in `target.cmake`.

### Platform matrix

`build.py` builds **six** slices which become **five** XCFramework slices:

| slice | sdk | generator | notes |
|---|---|---|---|
| ios | iphoneos | Xcode | arm64, min 14.0 |
| ios_simulator | iphonesimulator | Xcode | arm64 |
| xros | xros | Xcode | arm64, min 1.0 |
| xros_simulator | xrsimulator | Xcode | `CMAKE_SYSTEM_NAME` must be `xros`, not `xrsimulator` (hence the `system_name` override) |
| macos_arm64 | macosx | Unix Makefiles | `IOS=OFF`, `CMAKE_SYSTEM_NAME=Darwin` |
| macos_x86_64 | macosx | Unix Makefiles | lipo'd with arm64 into one universal slice |

macOS uses Makefiles rather than the Xcode generator; the Apple-device slices need the Xcode generator plus explicit `OTHER_LDFLAGS`/`OTHER_CFLAGS` carrying `-isysroot $(SDKROOT) -target <triple>` — this works around libtool being passed `-arch`. Changing generators or dropping those flags will break the device builds.

Libraries are copied to a temp dir under unique names (`ios_libfaust.a`, `xros_sim_libfaust.a`, …) before `xcodebuild -create-xcframework`, because that tool rejects multiple inputs sharing a basename. Those names are visible in the shipped `Info.plist` as `LibraryPath`.

## Faust submodule

The submodule points at the **`iPlug2/faust` fork, branch `ios-tweaks`** — not upstream `master-dev`. The fork carries iOS/visionOS build fixes and `iplug2-midi.h` that are not upstream. Update with:

```bash
cd faust && git checkout ios-tweaks && git pull origin ios-tweaks && cd ..
git add faust && git commit -m "Update faust submodule"
```

To pull in upstream Faust releases, rebase `ios-tweaks` onto `origin/master-dev` in the fork first; upstream is available as the `upstream` remote inside the submodule.

## CI / release

`.github/workflows/build-and-release.yml` runs on `macos-15` (needs the visionOS SDK). Triggered by pushing a `v*.*.*` tag, or manually via `workflow_dispatch`. It runs `build.py`, zips the XCFramework, tars the headers, and attaches both to a GitHub release. The release body's Faust version is scraped from `set (VERSION` in `faust/build/CMakeLists.txt` — if that line's format changes upstream, the version string silently becomes empty.

When modifying the workflow, check the result with `gh run list`.
