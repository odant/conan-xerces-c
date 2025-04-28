# Xerces-C++ Conan package
# Dmitriy Vetutnev, ODANT, 2018, 2020


from conan import ConanFile, tools
import os, glob, shutil


class XercesConan(ConanFile):
    name = "xerces-c"
    version = "3.3.0+1"
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
    #generators = "cmake"
    exports_sources = "src/*", "build.patch", "XMLDateTime.patch"
    #no_copy_source = True
    build_policy = "missing"
    package_type = "library"
    python_requires = "windows_signtool/[>=1.2]@odant/stable"

    def layout(self):
        tools.cmake.cmake_layout(self, src_folder="src") 

    def configure(self):
        # MT(d) static library
        if self.settings.os == "Windows" and self.settings.compiler == "msvc":
            if self.settings.compiler.runtime == "static":
                self.options.shared=False
        # DLL sign, only Windows and shared
        if self.settings.os != "Windows" or self.options.shared == False:
            del self.options.dll_sign
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        if self.options.ninja:
            self.build_requires("ninja/[>=1.12.1]")

    def requirements(self):
        self.requires("icu/[>=61.1]@odant/stable")

    def source(self):
        tools.files.patch(self, patch_file="build.patch")
        tools.files.patch(self, patch_file="XMLDateTime.patch")
        
    def generate(self):
        benv = tools.env.VirtualBuildEnv(self)
        benv.generate()        
        renv = tools.env.VirtualRunEnv(self)
        renv.generate()        
        if tools.microsoft.is_msvc(self):
            vcvars = tools.microsoft.VCVars(self);
            vcvars.generate();
        deps = tools.cmake.CMakeDeps(self)
        deps.generate()
        gen = "Ninja" if self.options.ninja == True else None
        tc = tools.cmake.CMakeToolchain(self, generator=gen)
        tc.variables["network"] = "OFF"
        tc.variables["transcoder"] = "icu"
        tc.variables["message-loader"] = "inmemory"
        tc.variables["xmlch-type"] = self.options.xmlch
        if self.options.with_unit_tests:
            tc.variables["WITH_UNIT_TESTS"] = "ON"
            tc.variables["AXT_WORKING_DIRECTORY"] = os.path.join(self.source_folder, "src", "samples", "data").replace("\\", "/")
        tc.generate()    

    def build(self):
        cmake = tools.cmake.CMake(self)
        cmake.configure()
        cmake.build()

    def package_id(self):
        self.info.options.with_unit_tests = "any"
        self.info.options.ninja = "any"

    def package(self):
        cmake = tools.cmake.CMake(self)
        cmake.install()
        tools.files.copy(self, "xerces-c*.pdb", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.build_folder, "src"), keep_path=False)
        # Sign DLL
        if self.options.get_safe("dll_sign"):
            self.python_requires["windows_signtool"].module.sign(self, [os.path.join(self.package_folder, "bin", "*.dll")])

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.libs = tools.files.collect_libs(self)
        if self.settings.os != "Windows" and not self.options.shared:
            self.cpp_info.libs.append("pthread")
