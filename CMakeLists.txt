cmake_minimum_required(VERSION 3.3)

set(PROOFCHECKER_VERSION_MAJOR 0)
set(PROOFCHECKER_VERSION_MINOR 0)
set(PROOFCHECKER_VERSION_PATCH 0)
set(PROOFCHECKER_VERSION ${PROOFCHECKER_VERSION_MAJOR}.${PROOFCHECKER_VERSION_MINOR}.${PROOFCHECKER_VERSION_PATCH})
project(proofchecker VERSION ${PROOFCHECKER_VERSION} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

add_executable(ProofParser proofparser.cc)

include(FetchContent)
FetchContent_Declare(
    base64
    GIT_REPOSITORY https://github.com/aehyvari/cpp-base64.git
)
FetchContent_MakeAvailable(base64)
add_library(base64::base64 ALIAS base64)
target_link_libraries(ProofParser PUBLIC base64)

set_target_properties(ProofParser PROPERTIES
    OUTPUT_NAME proofparser
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)
