"""Palvelujen testit: oikeat HTTP-palvelimet satunnaisissa porteissa."""

from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import api
import laskuri
from yhteinen import palvelin


def kaynnista(palvelu: ThreadingHTTPServer) -> str:
    threading.Thread(target=palvelu.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{palvelu.server_address[1]}"


def hae(osoite: str) -> tuple[int, dict[str, object]]:
    try:
        with urllib.request.urlopen(osoite, timeout=5) as v:  # noqa: S310
            return v.status, json.load(v)
    except urllib.error.HTTPError as virhe:
        return virhe.code, json.load(virhe)


class Palvelut(unittest.TestCase):
    def setUp(self) -> None:
        self.hakemisto = tempfile.TemporaryDirectory()
        data = Path(self.hakemisto.name)
        self.laskuri = palvelin(0, laskuri.kasittelija(laskuri.Laskuri(data)))
        laskuri_url = kaynnista(self.laskuri)
        self.api = palvelin(0, api.kasittelija(laskuri_url, "1.0.0"))
        self.api_url = kaynnista(self.api)

    def tearDown(self) -> None:
        for p in (self.api, self.laskuri):
            p.shutdown()
            p.server_close()
        self.hakemisto.cleanup()

    def test_kaynnit_kasvavat(self) -> None:
        self.assertEqual(hae(self.api_url + "/")[1]["kaynnit"], 1)
        self.assertEqual(hae(self.api_url + "/")[1]["kaynnit"], 2)

    def test_arvo_sailyy_uudessa_laskurissa(self) -> None:
        hae(self.api_url + "/")
        uusi = laskuri.Laskuri(Path(self.hakemisto.name))
        self.assertEqual(uusi.arvo(), 1)

    def test_valmius_riippuu_laskurista(self) -> None:
        self.assertEqual(hae(self.api_url + "/valmius")[0], 200)
        self.laskuri.shutdown()
        self.laskuri.server_close()
        self.assertEqual(hae(self.api_url + "/valmius")[0], 503)
        self.assertEqual(hae(self.api_url + "/terveys")[0], 200)
        self.assertEqual(hae(self.api_url + "/")[0], 503)


if __name__ == "__main__":
    unittest.main()
