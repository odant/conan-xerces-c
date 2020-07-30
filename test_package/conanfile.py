# Test Conan package
# Dmitriy Vetutnev, Odant 2019 - 2020


from conans import ConanFile, CMake


class PackageTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    requires = "ninja/1.9.0"

    def build(self):
        cmake = CMake(self, generator="Ninja", msbuild_verbosity='normal')
        if not self.options["openssl"].shared:
            cmake.definitions["DISABLE_TEST_ENGINE"] = "ON"
        cmake.verbose = True
        cmake.configure()
        cmake.build()
        self.cmake_is_multi_configuration = cmake.is_multi_configuration

    def test(self):
        if self.cmake_is_multi_configuration:
            self.run("ctest --verbose --build-config %s" % self.settings.build_type)
        else:
            self.run("ctest --verbose")

