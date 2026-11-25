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
# Jos testi epäonnistuu, sen virheilmoitus näytetään JUnitin raportista
# (-q piilottaisi Gradlen oman testilokin).
RAPORTIT := app/build/test-results/testDebugUnitTest
NAYTA_VIRHEET := { grep -h -A25 '<failure' $(RAPORTIT)/*.xml; exit 1; }

kaikki:
	$(GRADLE) assembleDebug assembleDebugAndroidTest lintDebug \
	    testDebugUnitTest || $(NAYTA_VIRHEET)

testit:
	$(GRADLE) testDebugUnitTest || $(NAYTA_VIRHEET)

# Käännöstuotteet jäävät välimuistiksi; ne eivät kuulu repositorioon.
siivoa:
	@true
