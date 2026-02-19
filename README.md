# cmake_generator
A little cmake generator because I'm too lazy

Write a YAML file describing the project:

```yaml
project_name: MyProject
version: 0.0.1

languages:
  CXX:
    standard: 20

include_dir: include
src_dir: src

options:
  use_native_opt:
    description: Enable -march=native -mtune=native
    default: OFF

build_tests: true
build_demos: false

install:
  cmake: true
  pkgconfig: true


CXX_options:
  clang_gnu:
    - -Wvarargs
    - -Wall
    - -Wextra
    - -Wpedantic
    - -Werror
    - -Wconversion
    - -Wuninitialized
    - -Wsign-conversion
    - -Wshadow
    - -Wnon-virtual-dtor
    - -Wold-style-cast
    - -Wcast-align
    - -Woverloaded-virtual
    - -Wnull-dereference
    - -Wformat=2
    - -flax-vector-conversions
    - -pedantic
    - -pedantic-errors
    - -Wdouble-promotion
    - -Wswitch-enum 
    - -Wlogical-op
    - -Wduplicated-cond 
    - -Wduplicated-branches
    - -Wvexing-parse

dependencies:
  samurai:
    git: https://github.com/hpc-maths/samurai.git
    tag: 2c91ab34a213c71b6be995f6b0f51333c5f1c133

libraries:
  MortensenFilterUtils:
    folder: MFU
    sources:
      - SymplecticEuler.cpp
      
executables:
  SymplecticDataAssimilation:
    sources:
      - main.cpp
    dependencies:
      - samurai::samurai
    CXX_options:
      - -Wno-error=array-bounds
```

execute and it generates the folders and CMakeLists.txt.
