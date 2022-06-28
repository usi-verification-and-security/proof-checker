cmake_minimum_required(VERSION 3.21)

set(PROOFCHECKER_VERSION_MAJOR 0)
set(PROOFCHECKER_VERSION_MINOR 0)
set(PROOFCHECKER_VERSION_PATCH 0)
set(PROOFCHECKER_VERSION ${PROOFCHECKER_VERSION_MAJOR}.${PROOFCHECKER_VERSION_MINOR}.${PROOFCHECKER_VERSION_PATCH})
project(proofchecker VERSION ${PROOFCHECKER_VERSION} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

option(STATIC_BUILD "Build statically linked binary" ON)

include(GNUInstallDirs)

add_executable(ProofParser-bin proofparser.cc)

include(FetchContent)
FetchContent_Declare(
    base64
    GIT_REPOSITORY https://github.com/aehyvari/cpp-base64.git
)
FetchContent_MakeAvailable(base64)

FetchContent_Declare(
        drat-trim
        GIT_REPOSITORY https://github.com/aehyvari/drat-trim.git
)

FetchContent_MakeAvailable(drat-trim)
install(IMPORTED_RUNTIME_ARTIFACTS
        drat-trim-bin
        base64
)

set_target_properties(ProofParser-bin PROPERTIES
    OUTPUT_NAME proofparser
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

if (STATIC_BUILD)
    include_directories(${base64_SOURCE_DIR})
    target_sources(ProofParser-bin PRIVATE $<TARGET_OBJECTS:base64>)
else ()
    target_link_libraries(ProofParser-bin PUBLIC base64)
endif ()

install(TARGETS ProofParser-bin)

install(PROGRAMS
        check_cnfization.py
        check_liaTheory.py
        check_liaTheoryProp.py
        check_lia_lraTheory.py
        check_lraTheoryProp.py
        check_lra_lraTheory.py
        check_ufTheory.py
        check_ufTheoryProp.py
        proof-check.sh
        TYPE BIN
        )
