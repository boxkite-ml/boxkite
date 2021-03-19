terraform {
  required_version = "~> 0.13"
  required_providers {
    helm = {
      source = "hashicorp/helm"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
    }
    k8s = {
      source  = "banzaicloud/k8s"
      version = "0.8.2"
    }
  }
}

resource "kubernetes_namespace" "istio_namespace" {
  metadata {
    name = var.istio_namespace

    labels = {
      istio-injection        = "disabled"
      istio-operator-managed = "Reconcile"
    }
  }
}

resource "k8s_manifest" "istio_deployment" {
  depends_on = [kubernetes_deployment.istio_operator, k8s_manifest.operator_crd, kubernetes_cluster_role_binding.istio_operator]
  content = templatefile(
    "${path.module}/manifests/istio-deployment.yaml",
    {
      namespace                = kubernetes_namespace.istio_namespace.metadata.0.name,
      ingress_gateway_selector = var.ingress_gateway_selector
      annotations              = var.ingress_gateway_annotations,
      lb_ip                    = var.ingress_gateway_ip
    }
  )
}

resource "null_resource" "wait_crds" {
  depends_on = [k8s_manifest.istio_deployment]

  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = "while [[ \"$(kubectl get crds | grep 'istio.io' | wc -l)\" -ne \"25\" ]]; do echo \"Waiting for CRDs\";  sleep 5; done"
  }
}