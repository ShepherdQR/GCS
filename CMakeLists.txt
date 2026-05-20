cmake_minimum_required(VERSION 4.0)

project(GCS VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_SCAN_FOR_MODULES ON)

add_library(gcs_solver)

target_sources(gcs_solver
    PUBLIC
        FILE_SET CXX_MODULES
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}/src
        FILES
            src/gcs/kernel/kernel.cppm
            src/gcs/incidence_graph/incidence_graph.cppm
            src/gcs/diagnostics/diagnostics.cppm
            src/gcs/numeric_engine/numeric_engine.cppm
            src/gcs/io_adapters/io_adapters.cppm
            src/gcs/session_runtime/session_runtime.cppm
    PRIVATE
        src/gcs/kernel/kernel.cpp
        src/gcs/incidence_graph/incidence_graph.cpp
        src/gcs/diagnostics/diagnostics.cpp
        src/gcs/numeric_engine/numeric_engine.cpp
        src/gcs/io_adapters/io_adapters.cpp
        src/gcs/session_runtime/session_runtime.cpp
)

target_compile_features(gcs_solver PUBLIC cxx_std_23)

add_executable(gcs_cli apps/gcs_cli/main.cpp)
target_link_libraries(gcs_cli PRIVATE gcs_solver)
target_compile_features(gcs_cli PRIVATE cxx_std_23)
set_target_properties(gcs_cli PROPERTIES OUTPUT_NAME GCS)
