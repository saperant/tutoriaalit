# Tutoriaalien yhteinen kehitysympäristö.
#
# Peruskuva sisältää make-, C- ja C++-työkalut sekä Pythonin. Kunkin
# tutoriaalin devcontainer.json lisää omat työkalunsa
# rakennusargumenteilla:
#
#   LISAPAKETIT     apt-paketit, esim. "verilator" tai "shellcheck bats"
#   PIP_PAKETIT     Python-paketit, esim. "ruff mypy pytest"
#   KIRJOITTAMINEN  true lisää pandocin, XeLaTeXin ja Graphvizin PDF:ien
#                   ja kaavioiden tuottamiseen

FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG KIRJOITTAMINEN=false
ARG LISAPAKETIT=""
ARG PIP_PAKETIT=""

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        make gcc-14 g++-14 clang-20 libclang-rt-20-dev gdb python3 \
        $LISAPAKETIT \
    && if [ "$KIRJOITTAMINEN" = "true" ]; then \
        apt-get install -y --no-install-recommends \
            pandoc graphviz texlive-xetex texlive-latex-recommended \
            texlive-latex-extra texlive-fonts-recommended \
            texlive-lang-european lmodern fonts-dejavu; \
    fi \
    && if [ -n "$PIP_PAKETIT" ]; then \
        apt-get install -y --no-install-recommends python3-pip \
        && pip3 install --break-system-packages --no-cache-dir $PIP_PAKETIT; \
    fi \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Ubuntun versioidut Go- ja Rust-työkalut omista hakemistoistaan.
ENV PATH="/usr/lib/go-1.23/bin:/usr/lib/rust-1.80/bin:${PATH}"
