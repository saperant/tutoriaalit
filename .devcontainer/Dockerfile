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
#   NODEJS          Node.js-versio, esim. "24.22.3" (nodejs.org)
#   NPM_PAKETIT     globaalit npm-paketit, esim. "typescript@7.0.2"
#   PLAYWRIGHT      Playwrightin versio; asentaa myös Chromiumin (vaatii
#                   NODEJS-argumentin)
#   ANDROID_SDK     Android SDK -paketit, esim. "platforms;android-36
#                   build-tools;36.0.0" (vaatii JDK:n). Rakentaminen
#                   hyväksyy Android SDK:n lisenssiehdot:
#                   https://developer.android.com/studio/terms
#   KOTLIN          Kotlin-kääntäjän versio, esim. "2.4.21" (vaatii
#                   LISAPAKETIT-listaan JDK:n)

FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG KIRJOITTAMINEN=false
ARG LISAPAKETIT=""
ARG PIP_PAKETIT=""
ARG NODEJS=""
ARG NPM_PAKETIT=""
ARG KOTLIN=""
ARG PLAYWRIGHT=""
ARG ANDROID_SDK=""
ENV ANDROID_HOME=/opt/android-sdk
ENV NODE_PATH=/usr/local/lib/node_modules \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        make gcc-14 g++-14 clang-20 libclang-rt-20-dev gdb python3 \
        curl ca-certificates xz-utils unzip \
        $LISAPAKETIT \
    && if [ "$KIRJOITTAMINEN" = "true" ]; then \
        apt-get install -y --no-install-recommends \
            pandoc graphviz texlive-xetex texlive-latex-recommended \
            texlive-latex-extra texlive-fonts-recommended \
            texlive-lang-european lmodern fonts-dejavu fonts-inter \
            fonts-jetbrains-mono; \
    fi \
    && if [ -n "$PIP_PAKETIT" ]; then \
        apt-get install -y --no-install-recommends python3-pip \
        && pip3 install --break-system-packages --no-cache-dir $PIP_PAKETIT; \
    fi \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN if [ -n "$NODEJS" ]; then \
        arkkitehtuuri=$(dpkg --print-architecture | sed 's/amd64/x64/') \
        && curl -fsSL "https://nodejs.org/dist/v$NODEJS/node-v$NODEJS-linux-$arkkitehtuuri.tar.xz" \
            | tar -xJ -C /usr/local --strip-components=1 \
            --exclude=CHANGELOG.md --exclude=LICENSE --exclude=README.md \
        && if [ -n "$NPM_PAKETIT" ]; then \
            npm install -g $NPM_PAKETIT && npm cache clean --force; \
        fi \
        && if [ -n "$PLAYWRIGHT" ]; then \
            npm install -g "playwright@$PLAYWRIGHT" \
            && playwright install --with-deps chromium \
            && npm cache clean --force && rm -rf /var/lib/apt/lists/*; \
        fi; \
    fi \
    && if [ -n "$KOTLIN" ]; then \
        curl -fsSL -o /tmp/kotlin.zip "https://github.com/JetBrains/kotlin/releases/download/v$KOTLIN/kotlin-compiler-$KOTLIN.zip" \
        && unzip -q /tmp/kotlin.zip -d /opt && rm /tmp/kotlin.zip; \
    fi \
    && if [ -n "$ANDROID_SDK" ]; then \
        curl -fsSL -o /tmp/sdk.zip https://dl.google.com/android/repository/commandlinetools-linux-16111833_latest.zip \
        && mkdir -p "$ANDROID_HOME/cmdline-tools" \
        && unzip -q /tmp/sdk.zip -d /tmp/sdk && rm /tmp/sdk.zip \
        && mv /tmp/sdk/cmdline-tools "$ANDROID_HOME/cmdline-tools/latest" \
        && yes | "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" --licenses > /dev/null \
        && "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" $ANDROID_SDK > /dev/null \
        && chmod -R a+rwX "$ANDROID_HOME"; \
    fi

# Ubuntun versioidut Go- ja Rust-työkalut omista hakemistoistaan sekä
# Kotlin-kääntäjä.
ENV PATH="/usr/lib/go-1.23/bin:/usr/lib/rust-1.80/bin:/opt/kotlinc/bin:${PATH}"
