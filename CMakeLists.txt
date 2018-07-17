# xerces-c Conan package
# Dmitriy Vetutnev, ODANT, 2018


cmake_minimum_required(VERSION 3.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(src)
