from distutils.core import setup, Extension

CFLAGS=[
    "-DMACOSX",
    "-DAPPLE_RUNTIME",
    "-no-cpp-precomp",
    "-Wno-long-double",
    "-g",

    # Loads of warning flags
    "-Wall", "-Wstrict-prototypes", "-Wmissing-prototypes",
    "-Wformat=2", "-W", "-Wshadow",
    "-Wpointer-arith", #"-Wwrite-strings",
    "-Wmissing-declarations",
    "-Wnested-externs",
    "-Wno-long-long",
    "-Wno-import",
    
    # Universal binary flags
    "-arch", "i386",
    "-arch", "ppc",
    "-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk",
    ]

BASE_LDFLAGS = [
    # Universal binary flags
    "-arch", "i386",
    "-arch", "ppc",
    "-isysroot", "/Developer/SDKs/MacOSX10.4u.sdk",
]

cSuperformula = Extension("cSuperformula", sources = ["superformula.c"], 
    extra_compile_args=CFLAGS, extra_link_args=BASE_LDFLAGS)

setup (name = "supershape",
       version = "1.0",
       author = "Frederik De Bleser. Superformula by Johan Gielis.",
       description = "Library for calculating the superformula.",
       ext_modules = [cSuperformula])