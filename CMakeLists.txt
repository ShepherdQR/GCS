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
            ${CMAKE_CURRENT_SOURCE_DIR}/GCS
        FILES
            GCS/core/core.cppm
            GCS/dcm/dcm.cppm
            GCS/lgs/lgs.cppm
            GCS/cds/cds.cppm
            GCS/io/io.cppm
            GCS/app/App.cppm
    PRIVATE
        GCS/core/core.cpp
        GCS/dcm/dcm.cpp
        GCS/lgs/lgs.cpp
        GCS/cds/cds.cpp
        GCS/io/io.cpp
        GCS/app/App.cpp
)

target_compile_features(gcs_solver PUBLIC cxx_std_23)

add_executable(gcs_cli GCS/app/main.cpp)
target_link_libraries(gcs_cli PRIVATE gcs_solver)
target_compile_features(gcs_cli PRIVATE cxx_std_23)
set_target_properties(gcs_cli PROPERTIES OUTPUT_NAME GCS)
