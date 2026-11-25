cmake_minimum_required(VERSION 3.28)
project(mittaus LANGUAGES CXX)

# Kirjasto: toteutus ja sen julkinen otsikkohakemisto.
add_library(mittausloki mittausloki.cpp)
target_compile_features(mittausloki PUBLIC cxx_std_23)
target_include_directories(mittausloki PUBLIC .)
target_compile_options(mittausloki PRIVATE -Wall -Wextra -Wpedantic)

# Ohjelma, joka käyttää kirjastoa.
add_executable(mittaus main.cpp)
target_link_libraries(mittaus PRIVATE mittausloki)

# ctest ajaa ohjelman; nollasta poikkeava paluuarvo on virhe.
enable_testing()
add_test(NAME mittaus COMMAND mittaus)
