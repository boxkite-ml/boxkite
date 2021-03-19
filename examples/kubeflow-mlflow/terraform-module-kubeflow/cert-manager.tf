resource "kubernetes_namespace" "cert_manager" {
  count = var.install_cert_manager ? 1 : 0
  metadata {
    annotations = {
      name = var.cert_manager_namespace
    }
    name = var.cert_manager_namespace
  }
}

resource "helm_release" "cert_manager" {
  count         = var.install_cert_manager ? 1 : 0
  name          = "cert-manager"
  repository    = "https://charts.jetstack.io"
  namespace     = kubernetes_namespace.cert_manager[0].metadata.0.name
  chart         = "cert-manager"
  keyring       = ""
  recreate_pods = true
  version       = var.cert_manager_version
  timeout       = 600

  set {
    name  = "installCRDs"
    value = "true"
  }
}

resource "null_resource" "wait_for_certs" {
  count      = var.install_cert_manager ? 1 : 0
  depends_on = [helm_release.cert_manager]
  triggers = {
    always_run = timestamp()
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = "sleep 180"
  }
}

resource "k8s_manifest" "selfsigned_issuer" {
  depends_on = [null_resource.wait_for_certs]
  content = templatefile(
    "${path.module}/manifests/cert-manager/self-signed.yaml",
    {}
  )
}

resource "k8s_manifest" "letsencrypt_issuer" {
  count      = var.use_cert_manager ? 1 : 0
  depends_on = [null_resource.wait_for_certs]
  content = templatefile(
    "${path.module}/manifests/cert-manager/letsencrypt-prod.yaml",
    {
      email = var.letsencrypt_email
    }
  )
}