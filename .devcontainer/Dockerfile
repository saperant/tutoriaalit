# Tutoriaalien yhteinen kehitysympäristö.
#
# Peruskuva sisältää C- ja C++-esimerkkien kääntämiseen ja testaamiseen
# tarvittavat työkalut: GCC 14, Clang 20 sanitoijineen, gdb ja Python.
# Rakennusargumentti KIRJOITTAMINEN=true lisää tutoriaalien kirjoittajan
# työkalut: pandocin, XeLaTeXin ja Graphvizin PDF:ien ja kaavioiden
# tuottamiseen.

FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG KIRJOITTAMINEN=false

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        make gcc-14 g++-14 clang-20 libclang-rt-20-dev gdb python3 \
    && if [ "$KIRJOITTAMINEN" = "true" ]; then \
        apt-get install -y --no-install-recommends \
            pandoc graphviz texlive-xetex texlive-latex-recommended \
            texlive-latex-extra texlive-fonts-recommended \
            texlive-lang-european lmodern fonts-dejavu; \
    fi \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
