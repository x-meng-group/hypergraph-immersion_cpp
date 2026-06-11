cmake_minimum_required(VERSION 3.16)

project(FastHypergraphImmersion VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(FHI_BUILD_TESTS "Build FastHypergraphImmersion tests" ON)

add_library(fhi
    src/Hypergraph.cpp
    src/ImmersionFunction.cpp
    src/Matching.cpp
    src/Parser.cpp
    src/QuickImmersion.cpp
)

target_include_directories(fhi
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_options(fhi PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic>
)

add_executable(fhi_cli src/main.cpp)
target_link_libraries(fhi_cli PRIVATE fhi)

if(FHI_BUILD_TESTS)
    enable_testing()
    add_executable(fhi_tests
        tests/test_hypergraph.cpp
        tests/test_immersion_function.cpp
        tests/test_matching.cpp
        tests/test_quick_immersion.cpp
    )
    target_link_libraries(fhi_tests PRIVATE fhi)
    add_test(NAME fhi_tests COMMAND fhi_tests)
endif()
