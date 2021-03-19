# Terraform module Kubeflow

This is a module deploying kubeflow purely in Terraform. Versioning is following Terraform's own versions : 0.12.x and 0.13.x. The active development will be now done on Terraform 0.13, 0.12 will be "frozen".

[![maintained by dataroots](https://img.shields.io/badge/maintained%20by-dataroots-%2300b189)](https://dataroots.io)
[![Terraform 0.13](https://img.shields.io/badge/terraform-0.13-%23623CE4)](https://www.terraform.io)
[![Terraform Registry](https://img.shields.io/badge/terraform-registry-%23623CE4)](https://registry.terraform.io/modules/datarootsio/kubeflow/module/)
[![tests](https://github.com/datarootsio/terraform-module-kubeflow/workflows/tests/badge.svg?branch=master)](https://github.com/datarootsio/terraform-module-kubeflow/actions)
[![Go Report Card](https://goreportcard.com/badge/github.com/datarootsio/terraform-module-kubeflow)](https://goreportcard.com/report/github.com/datarootsio/terraform-module-kubeflow)

## Usage

Due to the difficulties to have proper optional dependencies, with TF 0.12 you need to install istio and cert-manager as part of the process (as intended by Kubeflow). With Terraform 0.13 it is possible to reuse an existing installation of cert-manager and istio.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| cert\_manager\_namespace | The namespace for istio operator | `string` | `"cert-manager"` | no |
| cert\_manager\_version | The version of cert-manager | `string` | `"v0.16.1"` | no |
| certificate\_name | The secret where the pre-generated certificate is stored | `string` | `""` | no |
| dns\_record | The DNS record for Kubeflow's ingresses | `string` | `"kubeflow"` | no |
| domain\_name | The domain name for Kubeflow's ingresses DNS records | `string` | `""` | no |
| ingress\_gateway\_annotations | A map of key-value annotations for istio ingressgateway | `map(string)` | `{}` | no |
| ingress\_gateway\_ip | The IP of istio ingressgateway | `string` | `""` | no |
| ingress\_gateway\_selector | Istio ingressgateway selector | `string` | `"ingressgateway"` | no |
| install\_cert\_manager | n/a | `bool` | `false` | no |
| install\_istio | Should this module install istio | `bool` | `false` | no |
| istio\_namespace | The namespace for istio | `string` | `"istio-system"` | no |
| istio\_operator\_namespace | The namespace for istio operator | `string` | `"istio-operator"` | no |
| kubeflow\_components | The list of components to install. KF Operator does not support updates so changes after initial deployment will not be reflected. | `list(string)` | <pre>[<br>  "jupyter",<br>  "spark",<br>  "pytorch",<br>  "knative",<br>  "spartakus",<br>  "tensorflow",<br>  "katib",<br>  "pipelines",<br>  "seldon"<br>]</pre> | no |
| kubeflow\_operator\_namespace | The namespace for kubeflow operator | `string` | `"kubeflow-operator"` | no |
| kubeflow\_operator\_version | The version of kubeflow operator to install | `string` | `"1.1.0"` | no |
| kubeflow\_version | The version of kubeflow to install | `string` | `"1.1.0"` | no |
| letsencrypt\_email | The email to use for let's encrypt certificate requests | `string` | `""` | no |
| oidc\_auth\_url | The auth url for OIDC | `string` | `"/dex/auth"` | no |
| oidc\_client\_id | The Client ID for OIDC | `string` | `"kubeflow-oidc-authservice"` | no |
| oidc\_client\_secret | The OIDC client secret. The default value is not safe ! | `string` | `"pUBnBOY80SnXgjibTYM9ZWNzY2xreNGQok"` | no |
| oidc\_issuer | The OIDC issuer | `string` | `"http://dex.auth.svc.cluster.local:5556/dex"` | no |
| oidc\_redirect\_url | The OIDC redirect URL | `string` | `"/login/oidc"` | no |
| oidc\_userid\_claim | The claim for OIDC auth flows | `string` | `"email"` | no |
| use\_cert\_manager | Should we use cert-manager for ingresses certificates | `bool` | `false` | no |

## Examples

```hcl
module "kubeflow" {
  providers = {
    kubernetes = kubernetes
    k8s        = k8s
    helm       = helm
  }

  source  = "datarootsio/kubeflow/module"
  version = "~>0.12"

  ingress_gateway_ip  = "10.20.30.40"
  use_cert_manager    = true
  domain_name         = "foo.local"
  letsencrypt_email   = "foo@bar.local"
  kubeflow_components = ["pipelines"]
}
```

```hcl
module "kubeflow" {
  providers = {
    kubernetes = kubernetes
    k8s        = k8s
    helm       = helm
  }

  source  = "datarootsio/kubeflow/module"
  version = "~>0.13"

  ingress_gateway_ip   = "10.20.30.40"
  use_cert_manager     = true
  install_istio        = false
  install_cert_manager = false
  domain_name          = "foo.local"
  letsencrypt_email    = "foo@bar.local"
  kubeflow_components  = ["pipelines"]
}
```

## Outputs

No output.

## Contributing

Contributions to this repository are very welcome! Found a bug or do you have a suggestion? Please open an issue. Do you know how to fix it? Pull requests are welcome as well! To get you started faster, a Makefile is provided.

Make sure to install [Terraform](https://learn.hashicorp.com/terraform/getting-started/install.html), [Go](https://golang.org/doc/install) (for automated testing) and Make (optional, if you want to use the Makefile) on your computer. Install [tflint](https://github.com/terraform-linters/tflint) to be able to run the linting.

* Setup tools & dependencies: `make tools`
* Format your code: `make fmt`
* Linting: `make lint`
* Run tests: `make test` (or `go test -timeout 2h ./...` without Make)

To run the automated tests, you need to be logged in to a kubernetes cluster. We use [k3s](https://k3s.io/) in the test pipelines.

## License

MIT license. Please see [LICENSE](LICENSE.md) for details.