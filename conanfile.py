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
        cmake.definitions["network:BOOL"] = "OFF"
        cmake.definitions["transcoder"] = "icu"
        cmake.definitions["message-loader"] = "inmemory"
        cmake.definitions["BUILD_SHARED_LIBS:BOOL"] = "OFF"
        if self.settings.os == "Windows":
            cmake.definitions["xmlch-type"] = "wchar_t"
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*xerces-c.pdb", dst="bin", keep_path=False)
        return
        # CMake scripts
        self.copy("FindGTest.cmake", dst=".", src=".", keep_path=False)
        self.copy("FindGMock.cmake", dst=".", src=".", keep_path=False)
        # Headers
        self.copy("*.h", dst="include", src="src/googletest/include", keep_path=True)
        self.copy("*.h", dst="include", src="src/googlemock/include", keep_path=True)
        # Libraries
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        # PDB
        self.copy("*gtest.pdb", dst="bin", keep_path=False)
        self.copy("*gmock.pdb", dst="bin", keep_path=False)
        self.copy("*gtest_main.pdb", dst="bin", keep_path=False)
        self.copy("*gmock_main.pdb", dst="bin", keep_path=False)
        self.copy("*gtestd.pdb", dst="bin", keep_path=False)
        self.copy("*gmockd.pdb", dst="bin", keep_path=False)
        self.copy("*gtest_maind.pdb", dst="bin", keep_path=False)
        self.copy("*gmock_maind.pdb", dst="bin", keep_path=False)

    def package_info(self):
        return
        self.cpp_info.libs = ["gmock_main"] if self.settings.build_type == "Release" else ["gmock_maind"]
        self.cpp_info.defines = ["GTEST_LANG_CXX11"]
        #
        if self.settings.os == "Linux":
            if self.settings.build_type == "Release":
                self.cpp_info.libs.extend(["gmock", "gtest"])
            else:
                self.cpp_info.libs.extend(["gmockd", "gtestd"])
            self.cpp_info.libs.append("pthread")

