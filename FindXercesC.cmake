# Xerces-C++ Conan package
# Dmitriy Vetutnev, Odant, 2018


find_path(XercesC_INCLUDE_DIR
    NAMES xercesc/util/XercesVersion.hpp
    PATHS ${CONAN_INCLUDE_DIRS_XERCES-C}
    NO_DEFAULT_PATH
)

find_library(XercesC_LIBRARY
    NAMES xerces-c_3D xerces-c_3 xerces-c-3.2 xerces-c
    PATHS ${CONAN_LIB_DIRS_XERCES-C}
    NO_DEFAULT_PATH
)

if(XercesC_INCLUDE_DIR)

    file(STRINGS ${XercesC_INCLUDE_DIR}/xercesc/util/XercesVersion.hpp DEFINE_XercesC_MAJOR REGEX "^#define XERCES_VERSION_MAJOR")
    string(REGEX REPLACE "^.*XERCES_VERSION_MAJOR +([0-9]+).*$" "\\1" XercesC_VERSION_MAJOR "${DEFINE_XercesC_MAJOR}")

    file(STRINGS ${XercesC_INCLUDE_DIR}/xercesc/util/XercesVersion.hpp DEFINE_XercesC_MINOR REGEX "^#define XERCES_VERSION_MINOR")
    string(REGEX REPLACE "^.*XERCES_VERSION_MINOR +([0-9]+).*$" "\\1" XercesC_VERSION_MINOR "${DEFINE_XercesC_MINOR}")

    file(STRINGS ${XercesC_INCLUDE_DIR}/xercesc/util/XercesVersion.hpp DEFINE_XercesC_REVISION REGEX "^#define XERCES_VERSION_REVISION")
    string(REGEX REPLACE "^.*XERCES_VERSION_REVISION +([0-9]+).*$" "\\1" XercesC_VERSION_TWEAK "${DEFINE_XercesC_REVISION}")

    set(XercesC_VERSION_STRING "${XercesC_VERSION_MAJOR}.${XercesC_VERSION_MINOR}.${XercesC_VERSION_TWEAK}")
    set(XercesC_VERSION ${XercesC_VERSION_STRING})
    set(XercesC_VERSION_COUNT 3)

endif()


include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(XercesC
    REQUIRED_VARS XercesC_INCLUDE_DIR XercesC_LIBRARY
    VERSION_VAR XercesC_VERSION
)


if(XercesC_FOUND AND NOT TARGET XercesC::XercesC)

    include(CMakeFindDependencyMacro)
    find_dependency(ICU)
    find_dependency(Threads)

    add_library(XercesC::XercesC UNKNOWN IMPORTED)

    set_target_properties(XercesC::XercesC PROPERTIES
        IMPORTED_LOCATION "${XercesC_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${XercesC_INCLUDE_DIR}"
        INTERFACE_COMPILE_DEFINITIONS "${CONAN_COMPILE_DEFINITIONS_XERCES-C}"
        IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
    )
    set_property(TARGET XercesC::XercesC
        APPEND PROPERTY INTERFACE_LINK_LIBRARIES ICU::uc ICU::data Threads::Threads
    )

    mark_as_advanced(XercesC_INCLUDE_DIR XercesC_LIBRARY)

    set(XercesC_INCLUDE_DIRS ${XercesC_INCLUDE_DIR})
    set(XercesC_LIBRARIES ${XercesC_LIBRARY})
    set(XercesC_DEFINITIONS ${CONAN_COMPILE_DEFINITIONS_XERCES-C})

endif()

