# Monivaiheinen rakennus: kääntäjä on vain ensimmäisessä vaiheessa,
# lopullisessa kuvassa on pelkkä binääri.
FROM docker.io/library/golang:1.23-alpine@sha256:\
383395b794dffa5b53012a212365d40c8e37109a626ca30d6151c8348d380b5f \
    AS rakennus
WORKDIR /src
# Riippuvuustiedot ensin: kerros pysyy välimuistissa, kun vain koodi
# muuttuu.
COPY go.mod ./
RUN go mod download
COPY main.go ./
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /palvelu .

FROM gcr.io/distroless/static-debian12:nonroot@sha256:\
afa5c872c891853ca7fcf1f12c3edb23f7eeef36189728842dd51042ff57f7ab
COPY --from=rakennus /palvelu /palvelu
# Distroless-kuvan valmis nonroot-käyttäjä (UID 65532).
USER 65532:65532
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=2s CMD ["/palvelu", "-terveys"]
ENTRYPOINT ["/palvelu"]
