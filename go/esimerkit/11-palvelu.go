// JSON-rajapinta net/http-paketilla: reititys (Go 1.22 -mallit),
// validointi, virhevastaukset ja välikerros. Ohjelma testaa itsensä
// httptest-palvelimella, joten verkkoa ei tarvita.

// Moduulin go.mod-tiedostossa "go 1.22" tai uudempi ottaa uudet
// reitityssäännöt käyttöön. Ilman moduulia ne valitaan direktiivillä:
//
//go:debug httpmuxgo121=0
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"sync"
	"time"
)

// @alku tyypit
type Muistiinpano struct {
	ID      int      `json:"id"`
	Otsikko string   `json:"otsikko"`
	Tagit   []string `json:"tagit,omitempty"`
}

type palvelu struct {
	mu       sync.Mutex
	seuraava int
	muistio  map[int]Muistiinpano
}

// @loppu tyypit

// @alku reitit
func (p *palvelu) reitit() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /muistiinpanot", p.luo)
	mux.HandleFunc("GET /muistiinpanot/{id}", p.hae)
	return valikerros(mux)
}

// @loppu reitit

// @alku kasittelijat
func (p *palvelu) luo(w http.ResponseWriter, r *http.Request) {
	r.Body = http.MaxBytesReader(w, r.Body, 1<<20) // rajaa koon
	var m Muistiinpano
	d := json.NewDecoder(r.Body)
	d.DisallowUnknownFields()
	if err := d.Decode(&m); err != nil {
		virhe(w, http.StatusBadRequest, "virheellinen JSON: "+err.Error())
		return
	}
	if strings.TrimSpace(m.Otsikko) == "" {
		virhe(w, http.StatusUnprocessableEntity, "otsikko puuttuu")
		return
	}
	p.mu.Lock()
	p.seuraava++
	m.ID = p.seuraava
	p.muistio[m.ID] = m
	p.mu.Unlock()
	w.Header().Set("Location", fmt.Sprintf("/muistiinpanot/%d", m.ID))
	vastaa(w, http.StatusCreated, m)
}

func (p *palvelu) hae(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil {
		virhe(w, http.StatusBadRequest, "id ei ole luku")
		return
	}
	p.mu.Lock()
	m, ok := p.muistio[id]
	p.mu.Unlock()
	if !ok {
		virhe(w, http.StatusNotFound, "ei löydy")
		return
	}
	vastaa(w, http.StatusOK, m)
}

func vastaa(w http.ResponseWriter, tila int, arvo any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(tila)
	_ = json.NewEncoder(w).Encode(arvo) // asiakas voi olla jo poissa
}

func virhe(w http.ResponseWriter, tila int, viesti string) {
	vastaa(w, tila, map[string]string{"virhe": viesti})
}

// @loppu kasittelijat

// @alku valikerros
// valikerros kirjaa pyynnöt ja muuttaa paniikin vastaukseksi 500.
func valikerros(seuraava http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if p := recover(); p != nil {
				virhe(w, http.StatusInternalServerError,
					"sisäinen virhe")
			}
		}()
		fmt.Printf("  palvelin: %s %s\n", r.Method, r.URL.Path)
		seuraava.ServeHTTP(w, r)
	})
}

// @loppu valikerros

func main() {
	// @alku asiakas
	p := &palvelu{muistio: map[int]Muistiinpano{}}
	srv := httptest.NewServer(p.reitit())
	defer srv.Close()
	asiakas := &http.Client{Timeout: 5 * time.Second} // ei oletusta!

	pyynto := func(metodi, polku, runko string) {
		req, err := http.NewRequest(metodi, srv.URL+polku,
			strings.NewReader(runko))
		if err != nil {
			fmt.Println(err)
			return
		}
		vastaus, err := asiakas.Do(req)
		if err != nil {
			fmt.Println(err)
			return
		}
		defer vastaus.Body.Close() // aina, muuten yhteys ei vapaudu
		data, err := io.ReadAll(vastaus.Body)
		if err != nil {
			fmt.Println(err)
			return
		}
		fmt.Printf("%d %s", vastaus.StatusCode, data)
	}
	pyynto("POST", "/muistiinpanot", `{"otsikko":"Osta maitoa",
		"tagit":["kauppa"]}`)
	pyynto("GET", "/muistiinpanot/1", "")
	pyynto("GET", "/muistiinpanot/9", "")
	pyynto("POST", "/muistiinpanot", `{"otsikko":" "}`)
	pyynto("POST", "/muistiinpanot", `{"nimi":"x"}`)
	pyynto("DELETE", "/muistiinpanot/1", "")
	// @loppu asiakas
}
