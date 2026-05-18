# GCS Test Architecture

## Overview

Tests are plain C++ executables using the lightweight helpers in `GCS/test/test_framework.h`.

## Layout

```text
GCS/test/
  test_framework.h
  build_tests.bat
  run_tests.bat
  app/
  core/
  io/
  dcm/
  lgs/
  cds/
```

Each module test directory contains its `.cpp` test runner. Text model fixtures live under `GCS/scene/test/<module>/`.

## Build And Run

From the repository root:

```bat
GCS\test\build_tests.bat
GCS\test\run_tests.bat
```

The test build writes generated files to:

```text
build/bin/x64/Debug/
build/obj/tests/x64/Debug/
```
