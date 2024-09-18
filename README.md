# Satisfactory Prometheus Exporter
![Satisfactory](https://raw.githubusercontent.com/wolveix/satisfactory-server/main/.github/logo.png "Satisfactory logo")

## What is this?

Based off the work done by [wolveix]("https://github.com/wolveix/satisfactory-server"), this work extends the kubernetes cluster with monitoring
support for prometheus. Using the built-in api server, we're capturing game metadata and exposing it to prometheus.

---

## How to use

This script is designed to run in a kubernetes cluster. However, you can run this locally for testing.
>Note: If your satisfactory server is running on the same network and you're developing on a Windows machine
> then network type host will work to see the server however you will not be able to view the metrics when running in docker.
> Therefore it is simpler to run the script native on the host machine using poetry.

### Testing Locally

#### Building the whl

```shell
poetry install
poetry build
```

#### Configure Local env
To test locally, setup an .env file with the following values:
```shell
1LASK_APP=app
FLASK_ENV=development
SATISFACTORY_PASSWORD=<admin password for the game server>
SATISFACTORY_URL=<Node port or LB IP>
SATISFACTORY_PORT=<Game server port>
```

Then run the following commands:

#### Running locally
```shell
poetry run flask run
```

---

## Alternating the wolvelix/satisfactory-server cluster

### Create a new seceret for the game server

> **Important:** You must of already initialised the game server and set a admin password.

> **Important:** Ensure to select the same namespace as the game server

```yaml
kind: Secret
apiVersion: v1
metadata:
  name: satisfactory-server
  namespace: game
type: Opaque
data:
  SATISFACTORY_URL: <base64 encoded url>
  SATISFACTORY_PORT: <base64 encoded port>
  SATISFACTORY_PASSWORD: <base64 encoded password>
  
```

### Change the StatefulSet kind to include the prometheus exporter

```yaml
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: satisfactory
  namespace: games
spec:
  selector:
    matchLabels:
      app: satisfactory
  serviceName: "satisfactory"
  replicas: 1
  template:
    metadata:
      labels:
        app: satisfactory
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: kubernetes.io/arch
                operator: In
                values:
                - amd64
      containers:
        - name: satisfactory
          image: wolveix/satisfactory-server:latest
          env:
            - name: DEBUG
              value: "false"
            - name: MAXPLAYERS
              value: "8"
            - name: PGID
              value: "1000"
            - name: PUID
              value: "1000"
            - name: SKIPUPDATE
              value: "false"
            - name: STEAMBETA
              value: "false"
              # max objects in the world
            - name: MAXOBJECTS
              value: "4162688"
          ports:
            - containerPort: 7777
              name: "game-tcp"
              protocol: TCP
            - containerPort: 7777
              name: "game-udp"
              protocol: UDP
          volumeMounts:
            - name: satisfactory-data
              mountPath: /config
        - name: prometheus-exporter
          image: ghcr.io/dfoulkes/satisfactory-prometheus-exporter:main
          ports:
            - containerPort: 8075
              name: "metrics"
              protocol: TCP
          env:
            # the IP of the nodeport or LB
             - name: SATISFACTORY_URL
               valueFrom:
                secretKeyRef:
                    name: satisfactory-server
                    key: SATISFACTORY_URL
            # the port exposed by the LB or NodePort
             - name: SATISFACTORY_PORT
               valueFrom:
                 secretKeyRef:
                    name: satisfactory-server
                    key: SATISFACTORY_PORT
            # the game server admin password
             - name: SATISFACTORY_PASSWORD
               valueFrom:
                  secretKeyRef:
                    name: satisfactory-server
                    key: SATISFACTORY_PASSWORD
  volumeClaimTemplates:
    - metadata:
        name: satisfactory-data
      spec:
        accessModes: [ "ReadWriteOnce" ]
        resources:
          requests:
            storage: 30Gi
        storageClassName: longhorn

```

---

##  Create Server Secrets

The following script will create the base64 encoded values for the SATISFACTORY_URL, SATISFACTORY_PORT and SATISFACTORY_PASSWORD.
The encoded values can then be pasted into the secret.yaml file in the next step.
```shell

```yaml


1. Generate base64 encoded values for the SATISFACTORY_URL, SATISFACTORY_PORT and SATISFACTORY_PASSWORD
```shell
echo -n "http://<nodeport or LB IP>" | base64
echo -n "<nodeport or LB port>" | base64
echo -n "<admin password for the game server>" | base64
```
2. Update the secret.yaml file with the values generated
```yaml
kind: Secret
apiVersion: v1
metadata:
  name: satisfactory-server
  namespace: game
type: Opaque
data:
  SATISFACTORY_URL: <base64 encoded url>
  SATISFACTORY_PORT: <base64 encoded port>
  SATISFACTORY_PASSWORD: <base64 encoded password>
```
3. Apply the secret
```shell
kubectl apply -f secret.yaml
```

4. Update the service.yaml file with the new service
```yaml
metadata:
  name: satisfactory
  namespace: games
  labels:
    app: satisfactory
spec:
  type: LoadBalancer
  ports:
    - port: 7777
      protocol: UDP
      name: "game"
      targetPort: 7777
    - port: 7777
      protocol: TCP
      name: "gametcp"
      targetPort: 7777
    - port: 8075
      protocol: TCP
      name: "prometheus"
      targetPort: 8075
  selector:
    app: satisfactory
```

## Apply Prometherus Operator Service

```bash
kubectl apply -f prometheus-operator-service.yaml
```

>Note: You will also need to update your prometheus operator to include the new service