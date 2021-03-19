variable "istio_namespace" {
  type    = string
  default = "istio-system"
}

variable "istio_operator_namespace" {
  type    = string
  default = "istio-operator"
}

variable "ingress_gateway_annotations" {
  type    = map(string)
  default = {}
}

variable "ingress_gateway_selector" {
  type    = string
  default = "ingressgateway"
}

variable "ingress_gateway_ip" {
  type    = string
  default = ""
}

variable "domain_name" {
  type    = string
  default = ""
}

variable "use_cert_manager" {
  type    = bool
  default = false
}

variable "certificate_name" {
  type    = string
  default = ""
}

variable "istio_version" {
  type = string
  default = "1.6.8"
}