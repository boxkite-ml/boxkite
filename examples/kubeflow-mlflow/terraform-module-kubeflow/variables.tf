variable "install_istio" {
  type        = bool
  default     = false
  description = "Should this module install istio"
}

variable "istio_version" {
  type        = string
  default     = "1.6.8"
  description = "The version of istio that will be installed"
}

variable "install_cert_manager" {
  type    = bool
  default = false
}

variable "istio_namespace" {
  type        = string
  default     = "istio-system"
  description = "The namespace for istio"
}

variable "istio_operator_namespace" {
  type        = string
  default     = "istio-operator"
  description = "The namespace for istio operator"
}

variable "cert_manager_namespace" {
  type        = string
  default     = "cert-manager"
  description = "The namespace for istio operator"
}

variable "kubeflow_operator_namespace" {
  type        = string
  default     = "kubeflow-operator"
  description = "The namespace for kubeflow operator"
}

variable "cert_manager_version" {
  type        = string
  default     = "v0.16.1"
  description = "The version of cert-manager"

}

variable "ingress_gateway_annotations" {
  type        = map(string)
  default     = {}
  description = "A map of key-value annotations for istio ingressgateway"
}

variable "ingress_gateway_ip" {
  type        = string
  default     = ""
  description = "The IP of istio ingressgateway"
}

variable "ingress_gateway_selector" {
  type        = string
  default     = "ingressgateway"
  description = "Istio ingressgateway selector"
}

variable "dns_record" {
  type        = string
  default     = "kubeflow"
  description = "The DNS record for Kubeflow's ingresses"
}

variable "domain_name" {
  type        = string
  default     = ""
  description = "The domain name for Kubeflow's ingresses DNS records"
}

variable "use_cert_manager" {
  type        = bool
  default     = false
  description = "Should we use cert-manager for ingresses certificates"
}

variable "certificate_name" {
  type        = string
  default     = ""
  description = "The secret where the pre-generated certificate is stored"
}

variable "letsencrypt_email" {
  type        = string
  default     = ""
  description = "The email to use for let's encrypt certificate requests"
}

variable "oidc_client_secret" {
  type        = string
  default     = "pUBnBOY80SnXgjibTYM9ZWNzY2xreNGQok"
  description = "The OIDC client secret. The default value is not safe !"
}

variable "oidc_userid_claim" {
  type        = string
  default     = "email"
  description = "The claim for OIDC auth flows"
}

variable "oidc_auth_url" {
  type        = string
  default     = "/dex/auth"
  description = "The auth url for OIDC"
}

variable "oidc_client_id" {
  type        = string
  default     = "kubeflow-oidc-authservice"
  description = "The Client ID for OIDC"
}

variable "oidc_issuer" {
  type        = string
  default     = "http://dex.auth.svc.cluster.local:5556/dex"
  description = "The OIDC issuer"
}

variable "oidc_redirect_url" {
  type        = string
  default     = "/login/oidc"
  description = "The OIDC redirect URL"
}

variable "kubeflow_components" {
  type        = list(string)
  default     = ["jupyter", "spark", "pytorch", "knative", "spartakus", "tensorflow", "katib", "pipelines", "seldon"]
  description = "The list of components to install. KF Operator does not support updates so changes after initial deployment will not be reflected."
}

variable "kubeflow_version" {
  type        = string
  default     = "1.1.0"
  description = "The version of kubeflow to install"
}

variable "kubeflow_operator_version" {
  type        = string
  default     = "1.0.0"
  description = "The version of kubeflow operator to install"
}