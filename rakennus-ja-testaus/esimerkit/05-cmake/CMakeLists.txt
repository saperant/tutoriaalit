# Tilasto: kirjasto, komentoriviohjelma ja testit CMakella.
# @alku projekti
cmake_minimum_required(VERSION 3.25)
project(tilasto VERSION 1.2.0 LANGUAGES C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
# compile_commands.json analyysityökaluille (clang-tidy).
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
# @loppu projekti

# @alku kohteet
add_library(tilasto lahde/tilasto.c)
# PUBLIC: kirjaston käyttäjät tarvitsevat otsakkeen.
target_include_directories(tilasto PUBLIC lahde)
# PRIVATE: varoitusliput koskevat vain kirjaston omia lähteitä.
target_compile_options(tilasto PRIVATE -Wall -Wextra -Werror)
# libm on toteutuksen yksityiskohta; staattisen kirjaston käyttäjälle
# CMake lisää sen linkitykseen silti automaattisesti.
target_link_libraries(tilasto PRIVATE m)

add_executable(tilasto-cli lahde/main.c)
target_link_libraries(tilasto-cli PRIVATE tilasto)
set_target_properties(tilasto-cli PROPERTIES OUTPUT_NAME tilasto)
# @loppu kohteet

# @alku testit
enable_testing()
add_executable(testaa_tilasto testit/testaa_tilasto.c)
target_link_libraries(testaa_tilasto PRIVATE tilasto)
add_test(NAME yksikkotestit COMMAND testaa_tilasto)

set(syote ${CMAKE_CURRENT_SOURCE_DIR}/lahde/mittaukset.txt)
add_test(NAME komentorivi
         COMMAND sh -c "$<TARGET_FILE:tilasto-cli> < ${syote}")
set_tests_properties(komentorivi PROPERTIES
                     PASS_REGULAR_EXPRESSION "mediaani +22.000")
# @loppu testit
