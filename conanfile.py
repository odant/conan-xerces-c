# xerces-c Conan package
# Dmitriy Vetutnev, ODANT, 2018


from conans import ConanFile, CMake


class XercesConan(ConanFile):
    name = "xerces-c"
    version = "3.2.1"
    license = "Apache License v2.0"
    description = "Xerces-C++ XML parser"
    url = "https://github.com/odant/conan-xerces-c"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports_sources = "src/*", "CMakeLists.txt"
    no_copy_source = True
    build_policy = "missing"

    def configure(self):
        if self.settings.compiler.get_safe("libcxx") == "libstdc++":
            raise Exception("This package is only compatible with libstdc++11")

    def requirements(self):
        self.requires("icu/61.1@odant/testing")

    def build(self):
        build_type = "RelWithDebInfo" if self.settings.build_type == "Release" else "Debug"
        cmake = CMake(self, build_type=build_type)
        cmake.verbose = True
        #
        cmake.definitions["network:BOOL"] = "OFF"
        cmake.definitions["transcoder"] = "icu"
        cmake.definitions["message-loader"] = "inmemory"
        cmake.definitions["BUILD_SHARED_LIBS:BOOL"] = "OFF"
        if self.settings.os == "Windows":
            cmake.definitions["xmlch-type"] = "wchar_t"
        if self.settings.os == "Linux":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE:BOOL"] = "ON"
        #
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*xerces-c.pdb", dst="bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

