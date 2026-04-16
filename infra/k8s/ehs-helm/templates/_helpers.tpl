{{/*
Expand the name of the chart.
*/}}
{{- define "ehs-helm.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ehs-helm.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and use as default for app labels
*/}}
{{- define "ehs-helm.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ehs-helm.labels" -}}
helm.sh/chart: {{ include "ehs-helm.chart" . }}
{{ include "ehs-helm.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ehs-helm.selectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/part-of: ehs-platform
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ehs-helm.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ehs-helm.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the ConfigMap
*/}}
{{- define "ehs-helm.configMapName" -}}
{{- printf "%s-config" (include "ehs-helm.fullname" .) }}
{{- end }}

{{/*
Create the name of the Secret
*/}}
{{- define "ehs-helm.secretName" -}}
{{- printf "%s-secrets" (include "ehs-helm.fullname" .) }}
{{- end }}

{{/*
Create the name of the ServiceMonitor
*/}}
{{- define "ehs-helm.serviceMonitorName" -}}
{{- printf "%s-monitor" (include "ehs-helm.fullname" .) }}
{{- end }}
