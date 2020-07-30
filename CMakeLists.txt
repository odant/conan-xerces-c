# CMake wrapper to build  Conan package
# Dmitriy Vetutnev, Odant 2018 - 2020


cmake_minimum_required(VERSION 3.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

enable_testing()
add_subdirectory(src)
