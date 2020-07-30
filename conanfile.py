# Xerces-C++ Conan package
# Dmitriy Vetutnev, ODANT, 2018


from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os, glob, shutil


def get_safe(options, name):
    try:
        return getattr(options, name, None)
    except ConanException:
        return None


class XercesConan(ConanFile):
    name = "xerces-c"
    version = "3.2.2+8"
    license = "Apache License v2.0"
    description = "Xerces-C++ XML parser"
    url = "https://github.com/odant/conan-xerces-c"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "dll_sign": [True, False],
        "with_unit_tests": [False, True],
        "xmlch": [None, "char16_t", "wchar_t", "uint16_t"],
        "shared": [True, False]
    }
    default_options = "dll_sign=True", "with_unit_tests=False", "xmlch=None", "shared=True"
    generators = "cmake"
    exports_sources = "src/*", "CMakeLists.txt", "build.patch", "FindXercesC.cmake"
    no_copy_source = True
    build_policy = "missing"

    def configure(self):
        if self.settings.compiler.get_safe("libcxx") == "libstdc++":
            raise Exception("This package is only compatible with libstdc++11")
        if self.options.xmlch is None or self.options.xmlch == "None":
            self.options.xmlch = "char16_t"
        # MT(d) static library
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            if self.settings.compiler.runtime == "MT" or self.settings.compiler.runtime == "MTd":
                self.options.shared=False
        # DLL sign, only Windows and shared
        if self.settings.os != "Windows" or self.options.shared == False:
            del self.options.dll_sign

    def build_requirements(self):
        if get_safe(self.options, "dll_sign"):
            self.build_requires("windows_signtool/[>=1.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("icu/[>=61.1]@odant/stable")

    def source(self):
        tools.patch(patch_file="build.patch")

    def build(self):
        build_type = "RelWithDebInfo" if self.settings.build_type == "Release" else "Debug"
        cmake = CMake(self, build_type=build_type)
        cmake.verbose = True
        #
        cmake.definitions["network:BOOL"] = "OFF"
        cmake.definitions["transcoder"] = "icu"
        cmake.definitions["message-loader"] = "inmemory"
        cmake.definitions["xmlch-type"] = self.options.xmlch
        cmake.definitions["BUILD_SHARED_LIBS:BOOL"] = "ON" if self.options.shared == True else "OFF"
        if self.settings.os == "Linux":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE:BOOL"] = "ON"
        if self.options.with_unit_tests:
            cmake.definitions["with_unit_tests"] = "ON"
            cmake.definitions["AXT_WORKING_DIRECTORY"] = os.path.join(self.source_folder, "src/samples/data").replace("\\", "/")
        #
        cmake.configure()
        cmake.build()
        cmake.install()
        if self.options.with_unit_tests:
            if self.settings.os == "Windows":
                self.output.info("Import ICU DLLs")
                icu_dll = os.path.join(self.deps_cpp_info["icu"].bin_paths[0], "*.dll")
                build_bin = os.path.join(self.build_folder, "bin")
                self.output.info("icu_dll: %s" % icu_dll)
                self.output.info("build_bin: %s" % build_bin)
                for f in glob.glob(icu_dll):
                    self.output.info("Copy %s to %s" % (f, build_bin))
                    shutil.copy(f, build_bin)
                self.run("ctest --build-config %s" % self.settings.build_type)
            else:
                self.run("ctest")

    def package_id(self):
        self.info.options.with_unit_tests = "any"

    def package(self):
        self.copy("FindXercesC.cmake", dst=".", src=".", keep_path=False)
        self.copy("xerces-c*.pdb", dst="bin", src="bin", keep_path=False)
        # Sign DLL
        if get_safe(self.options, "dll_sign"):
            import windows_signtool
            pattern = os.path.join(self.package_folder, "bin", "*.dll")
            for fpath in glob.glob(pattern):
                fpath = fpath.replace("\\", "/")
                for alg in ["sha1", "sha256"]:
                    is_timestamp = True if self.settings.build_type == "Release" else False
                    cmd = windows_signtool.get_sign_command(fpath, digest_algorithm=alg, timestamp=is_timestamp)
                    self.output.info("Sign %s" % fpath)
                    self.run(cmd)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os != "Windows":
            self.cpp_info.libs.append("pthread")
