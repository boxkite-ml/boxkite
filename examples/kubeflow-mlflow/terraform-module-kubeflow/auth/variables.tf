variable "domain_name" {
  type = string
}

variable "application_secret" {
  type    = string
  default = "pUBnBOY80SnXgjibTYM9ZWNzY2xreNGQok"
}

variable "userid_claim" {
  type = string
  default = "email"
}

variable "oidc_auth_url" {
  type = string
  default = "/dex/auth"
}

variable "client_id" {
  type    = string
  default = "kubeflow-oidc-authservice"
}

variable "issuer" {
  type    = string
  default = "http://dex.auth.svc.cluster.local:5556/dex"
}

variable "oidc_redirect_url" {
  type    = string
  default = "/login/oidc"
}

variable "static_email" {
  type    = string
  default = "admin@kubeflow.org"
}

variable "static_password_hash" {
  type    = string
  default = "$2y$12$ruoM7FqXrpVgaol44eRZW.4HWS8SAvg6KYVVSCIwKQPBmTpCm.EeO"
}

variable "static_user_id" {
  type    = string
  default = "08a8684b-db88-4b73-90a9-3cd1661f5466"
}

variable "static_username" {
  type    = string
  default = "admin"
}

variable "istio_namespace" {
  type = string
}

variable "auth_depends_on" {
  type    = any
  default = null
}