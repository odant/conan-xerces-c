# Xerces-C++ Conan package
# Dmitriy Vetutnev, ODANT, 2018, 2020


from conans import ConanFile, CMake, tools
import os, glob, shutil


class XercesConan(ConanFile):
    name = "xerces-c"
    version = "3.2.3+0"
    license = "Apache License v2.0"
    description = "Xerces-C++ XML parser"
    url = "https://github.com/odant/conan-xerces-c"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "dll_sign": [True, False],
        "with_unit_tests": [True, False],
        "ninja": [True, False],
        "xmlch": ["char16_t", "wchar_t", "uint16_t"]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "dll_sign": True,
        "with_unit_tests": False,
        "ninja": True,
        "xmlch": "char16_t"
    }
    generators = "cmake"
    exports_sources = "src/*", "CMakeLists.txt", "build.patch", "FindXercesC.cmake"
    no_copy_source = True
    build_policy = "missing"

    def configure(self):
        # MT(d) static library
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            if self.settings.compiler.runtime == "MT" or self.settings.compiler.runtime == "MTd":
                self.options.shared=False
        # DLL sign, only Windows and shared
        if self.settings.os != "Windows" or self.options.shared == False:
            del self.options.dll_sign

    def build_requirements(self):
        if self.options.ninja:
            self.build_requires("ninja/1.9.0")
        if self.options.get_safe("dll_sign"):
            self.build_requires("windows_signtool/[>=1.1]@%s/stable" % self.user)

    def requirements(self):
        self.requires("icu/[>=61.1]@odant/stable")

    def source(self):
        tools.patch(patch_file="build.patch")

    def build(self):
        build_type = "RelWithDebInfo" if self.settings.build_type == "Release" else "Debug"
        gen = "Ninja" if self.options.ninja == True else None
        cmake = CMake(self, build_type=build_type, generator=gen, msbuild_verbosity='normal')
        cmake.verbose = True
        #
        cmake.definitions["network:BOOL"] = "OFF"
        cmake.definitions["transcoder"] = "icu"
        cmake.definitions["message-loader"] = "inmemory"
        cmake.definitions["xmlch-type"] = self.options.xmlch
        if self.options.with_unit_tests:
            cmake.definitions["WITH_UNIT_TESTS"] = "ON"
            cmake.definitions["AXT_WORKING_DIRECTORY"] = os.path.join(self.source_folder, "src/samples/data").replace("\\", "/")
        #
        cmake.configure()
        cmake.build()
        cmake.install()
        if self.options.with_unit_tests and self.deps_cpp_info["icu"].bin_paths:
            if self.settings.os == "Windows":
                self.output.info("Import ICU DLLs")
                icu_dll = os.path.join(self.deps_cpp_info["icu"].bin_paths[0], "*.dll")
                build_bin = os.path.join(self.build_folder, "bin")
                self.output.info("icu_dll: %s" % icu_dll)
                self.output.info("build_bin: %s" % build_bin)
                for f in glob.glob(icu_dll):
                    self.output.info("Copy %s to %s" % (f, build_bin))
                    shutil.copy(f, build_bin)
                self.run("ctest --output-on-failure --build-config %s" % self.settings.build_type)
            else:
                with tools.environment_append({"LD_LIBRARY_PATH": self.deps_cpp_info["icu"].lib_paths[0]}):
                    self.run("ctest --output-on-failure")

    def package_id(self):
        self.info.options.with_unit_tests = "any"

    def package(self):
        self.copy("FindXercesC.cmake", dst=".", src=".", keep_path=False)
        self.copy("xerces-c*.pdb", dst="bin", src="bin", keep_path=False)
        # Sign DLL
        if self.options.get_safe("dll_sign"):
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
        if self.settings.os != "Windows" and not self.options.shared:
            self.cpp_info.libs.append("pthread")
