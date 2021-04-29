mlflow
======

[MLFlow](https://mlflow.org/) is an open source platform specialized in tracking ML experiments, and packaging and deploying ML models.


Current chart version is `1.0.1`

---

## Install Chart

To install the MLFlow chart in your Kubernetes cluster, add the `larribas` repository (see main [README](../README.md)), and then run:

```bash
helm install --namespace mlflow --name mlflow larribas/mlflow
```


After the installation succeeds, you can get the Chart's status via:

```bash
helm status mlflow
```


You can delete the Chart anytime via:

```bash
helm delete --purge mlflow
```


## Known limitations of this Chart

I've created this Chart to use it in a production-ready environment in my company. We are using MLFlow with a Postgres backend store.

Therefore, the following capabilities have been left out of the Chart:

- Using persistent volumes as a backend store.
- Using other database engines like MySQL or SQLServer.

__I would happily accept contributions to this Chart__


## Local vs. Remote backend stores

By default, MLFlow will store data and artifacts in the local filesystem. If you're deploying a production-ready MLFlow cluster, I would recommend you to point your backend store to a remote database.

At the moment, the only database engine supported by this Chart is Postgres. This means you can add the following values:

```yaml
backendStore:
  postgres:
    username: my_user
    password: my_password
    host: my_host
    port: 5342
    database: my_db
```

And (provided the right network and security setup) the Chart will work seamlessly with that database.

Supporting other database engine is not in my plans, but if you're planning to fork this repository and/or contribute to it, this is what you would need to do in order to add support to another DB engine:

* Fork the [repository](https://github.com/larribas/docker-production-mlflow) where the docker image is defined and install the system and python libraries that MLFlow would require to connect to the database.
* Publish a new docker image with the right dependencies installed.
* Fork this repository and modify the
  - [values.yaml](values.yaml) - add configuration for the new engine
  - [secret.yaml](templates/secret.yaml) - add a new secret for your engine 
  - [deployment.yaml](templates/deployment.yaml) - inject the right secret and pass the right argument to the container


## Service Accounts / RBAC

By default, this Chart creates a new ServiceAccount and runs the deployment under it. You can disable this behavior setting `serviceAccount.create = false`.


## Ingress controller

By default, the ingress controller is disabled. You can, however, instruct the Chart to create an Ingress resource for you with the values you specify.


## Chart Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| backendStore | object | `{"filepath":null,"postgres":null}` | Either a filepath, a database or the default value. At present, postgres is the only database engine supported by the official image. Should you want to connect to any other database, please refer to the README. |
| backendStore.filepath | string | `nil` | A local or remote filesystem path (e.g. /mnt/persistent-disk) |
| backendStore.postgres | string | `nil` | A map with the values for (username, password, host, port and database). |
| defaultArtifactRoot | string | `nil` | A local or remote filepath (e.g. s3://my-bucket). It is mandatory when specifying a database backend store |
| extraArgs | object | `{}` | A map of arguments and values to pass to the `mlflow server` command |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"larribas/mlflow"` | The fully qualified name of the docker image to use |
| image.tag | string | `nil` | The tag for the repository (e.g. 'latest') |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations | object | `{}` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts[0].host | string | `"chart-example.local"` |  |
| ingress.hosts[0].paths | list | `[]` | A list of objects. Each object should contain a `path` key, and may contain a `serviceNameOverride` and a `servicePortOverride` key. If you do not specify any overrides, the Chart will use the ones for the service it creates automatically. We allow overrides to allow advanced behavior like SSL redirection on the AWS ALB Ingress Controller. |
| ingress.tls | list | `[]` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| service.port | int | `5000` |  |
| service.type | string | `"NodePort"` |  |
| serviceAccount.annotations | object | `{}` | Annotations to add to the service account |
| serviceAccount.create | bool | `true` | Specifies whether a service account should be created |
| serviceAccount.name | string | `nil` | The name of the service account to use. If not set and create is true, a name is generated using the fullname template |
| tolerations | list | `[]` |  |
