{{/* Yhteiset tunnisteet kaikille resursseille. */}}
{{- define "kaynnit.tunnisteet" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{- define "kaynnit.valitsin" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Kuvan nimi: tyhjä tagi tarkoittaa kaavion appVersionia. */}}
{{- define "kaynnit.kuva" -}}
{{- $tagi := .Values.kuva.tag | default .Chart.AppVersion -}}
{{ .Values.kuva.repository }}:{{ $tagi }}
{{- end }}

{{/* Asetusten tiiviste: muuttuu, kun ConfigMapin sisältö muuttuu. */}}
{{- define "kaynnit.asetustiiviste" -}}
{{ include (print .Template.BasePath "/configmap.yaml") . | sha256sum }}
{{- end }}
