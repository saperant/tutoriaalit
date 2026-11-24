# Android-esimerkit: käännös, lint ja JVM-testit (Robolectric) Gradle
# Wrapperilla. Ensimmäinen ajo lataa Gradlen ja riippuvuudet.
#
#   make           kääntää (myös laitetestit), tarkistaa ja testaa
#   make testit    vain yksikkötestit
#
# ANDROID_HOME osoittaa Android SDK:hon; kehityskontissa se on valmiina.

ANDROID_HOME ?= /opt/android-sdk
export ANDROID_HOME
GRADLE := ./gradlew --no-daemon --console=plain -q

.PHONY: kaikki testit siivoa
kaikki:
	$(GRADLE) assembleDebug assembleDebugAndroidTest lintDebug \
	    testDebugUnitTest

testit:
	$(GRADLE) testDebugUnitTest

# Käännöstuotteet jäävät välimuistiksi; ne eivät kuulu repositorioon.
siivoa:
	@true
