# Kesto-projekti. Samat komennot toimivat kehityskontissa, CI:ssä ja
# omalla koneella, kunhan työkalut on asennettu.
#
#   make ymparisto   tarkistaa, että työkalut löytyvät
#   make testaa      ajaa testit

.PHONY: ymparisto testaa

ymparisto:
	@python3 -c "import sys; assert sys.version_info >= (3, 12)" \
	    || { echo "Python 3.12 tai uudempi puuttuu"; exit 1; }
	@python3 -c "import pytest" 2>/dev/null \
	    || { echo "pytest puuttuu"; exit 1; }
	@echo "ympäristö kunnossa"

testaa:
	@python3 -m pytest -q -p no:cacheprovider
