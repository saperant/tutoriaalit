// Rakenteinen lokitus log/slog-paketilla (Go 1.21).
package main

import (
	"errors"
	"log/slog"
	"os"
)

func main() {
	// @alku slog
	asetukset := &slog.HandlerOptions{
		Level: slog.LevelDebug,
		// Aikaleima poistetaan, jotta tuloste on toistettava.
		ReplaceAttr: func(ryhmat []string, a slog.Attr) slog.Attr {
			if a.Key == slog.TimeKey && len(ryhmat) == 0 {
				return slog.Attr{}
			}
			return a
		},
	}
	loki := slog.New(slog.NewTextHandler(os.Stdout, asetukset))
	// Tuotannossa yleensä JSON: slog.NewJSONHandler(os.Stdout, ...).

	pyynto := loki.With("pyynto", "a1b2") // jokaiseen riviin
	pyynto.Info("pyyntö alkoi", "kayttaja", 42)
	pyynto.Debug("välimuisti", slog.Bool("osuma", false))
	err := errors.New("aikakatkaisu")
	pyynto.Error("haku epäonnistui", "virhe", err,
		slog.Group("yritys", "nro", 3))
	// @loppu slog
}
