cmake_minimum_required(VERSION 4.0)

project(GCS VERSION 0.2.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_SCAN_FOR_MODULES ON)

option(GCS_BUILD_TESTS "Build GCS contract tests" ON)
option(GCS_FETCH_GTEST "Fetch GoogleTest when an installed package is not available" OFF)

add_library(gcs_solver)

target_sources(gcs_solver
    PUBLIC
        FILE_SET CXX_MODULES
        BASE_DIRS
            ${CMAKE_CURRENT_SOURCE_DIR}/src
        FILES
            src/gcs/kernel/kernel.cppm
            src/gcs/constraint_catalog/constraint_catalog.cppm
            src/gcs/incidence_graph/incidence_graph.cppm
            src/gcs/decomposition_planner/decomposition_planner.cppm
            src/gcs/numeric_engine/numeric_engine.cppm
            src/gcs/diagnostics/diagnostics.cppm
            src/gcs/session_runtime/session_runtime.cppm
            src/gcs/io_adapters/io_adapters.cppm
            src/gcs/viewer_bridge/viewer_bridge.cppm
            src/gcs/tools/contract_tools.cppm
    PRIVATE
        src/gcs/kernel/kernel.cpp
        src/gcs/constraint_catalog/constraint_catalog.cpp
        src/gcs/incidence_graph/incidence_graph.cpp
        src/gcs/decomposition_planner/decomposition_planner.cpp
        src/gcs/numeric_engine/numeric_engine.cpp
        src/gcs/diagnostics/diagnostics.cpp
        src/gcs/session_runtime/session_runtime.cpp
        src/gcs/io_adapters/io_adapters.cpp
        src/gcs/viewer_bridge/viewer_bridge.cpp
        src/gcs/tools/contract_tools.cpp
)

target_compile_features(gcs_solver PUBLIC cxx_std_23)

add_executable(gcs_cli apps/gcs_cli/main.cpp)
target_link_libraries(gcs_cli PRIVATE gcs_solver)
target_compile_features(gcs_cli PRIVATE cxx_std_23)
set_target_properties(gcs_cli PROPERTIES OUTPUT_NAME GCS)

if(GCS_BUILD_TESTS)
    include(CTest)
    if(BUILD_TESTING)
        find_package(GTest CONFIG QUIET)
        if(NOT GTest_FOUND)
            find_package(GTest QUIET)
        endif()

        if(NOT GTest_FOUND AND GCS_FETCH_GTEST)
            include(FetchContent)
            FetchContent_Declare(
                googletest
                URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
            )
            set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
            FetchContent_MakeAvailable(googletest)
        endif()

        if(TARGET GTest::gtest_main)
            add_executable(gcs_contract_tests
                tests/gcs_contract_tests.cpp
            )
            target_link_libraries(gcs_contract_tests
                PRIVATE
                    gcs_solver
                    GTest::gtest_main
            )
            target_compile_features(gcs_contract_tests PRIVATE cxx_std_23)

            include(GoogleTest)
            gtest_discover_tests(gcs_contract_tests)
        else()
            message(STATUS "GTest not found; skipping gcs_contract_tests. Set GCS_FETCH_GTEST=ON to fetch it.")
        endif()
    endif()
endif()
