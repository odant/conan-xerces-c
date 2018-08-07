# Test Xerces-C++ Conan package
# Dmitriy Vetutnev, ODANT, 2018


project(PackageTest CXX)
cmake_minimum_required(VERSION 3.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

enable_testing()


# CONAN_PKG imported targets

add_executable(CreateDOMDocument_CONAN_PKG CreateDOMDocument.cpp)
target_link_libraries(CreateDOMDocument_CONAN_PKG CONAN_PKG::xerces-c)
add_test(
    NAME CreateDOMDocument_CONAN_PKG
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    COMMAND CreateDOMDocument_CONAN_PKG
)
if(UNIX)
    set_property(TEST CreateDOMDocument_CONAN_PKG PROPERTY ENVIRONMENT LD_DEBUG=libs LD_LIBRARY_PATH=${CMAKE_BINARY_DIR}/bin)
endif()


# Normal imported targets

find_package(XercesC REQUIRED)
add_executable(CreateDOMDocument CreateDOMDocument.cpp)
target_link_libraries(CreateDOMDocument XercesC::XercesC)
add_test(
    NAME CreateDOMDocument
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    COMMAND CreateDOMDocument
)
if(UNIX)
    set_property(TEST CreateDOMDocument PROPERTY ENVIRONMENT LD_DEBUG=libs LD_LIBRARY_PATH=${CMAKE_BINARY_DIR}/bin)
endif()
