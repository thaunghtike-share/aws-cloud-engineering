# Kubernetes Liveness and Readiness Probes Lab

## API Routes

```text
/         200 or 500
/healthz  200 or 500
/readyz   200 or 503
```

## 1. Open Lab

```bash
cd /Users/mac/Desktop/workspace/class/health-probes-app
```

## 2. Check Cluster

```bash
kubectl get nodes -o wide
kubectl get pods -A
kubectl get storageclass
```

## 3. Create PostgreSQL YAML

```bash
cat > psql.yaml <<'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: probes-lab
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: probes-lab
type: Opaque
stringData:
  POSTGRES_DB: appdb
  POSTGRES_USER: appuser
  POSTGRES_PASSWORD: apppassword
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: probes-lab
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
    - name: postgres
      port: 5432
      targetPort: postgres
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: probes-lab
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:17
          imagePullPolicy: IfNotPresent
          envFrom:
            - secretRef:
                name: postgres-secret
          ports:
            - name: postgres
              containerPort: 5432
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
              subPath: pgdata
          readinessProbe:
            exec:
              command:
                - pg_isready
                - -U
                - appuser
                - -d
                - appdb
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 6
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
  volumeClaimTemplates:
    - metadata:
        name: postgres-data
      spec:
        accessModes:
          - ReadWriteOnce
        storageClassName: longhorn
        resources:
          requests:
            storage: 2Gi
EOF
```

## 4. Deploy PostgreSQL

```bash
kubectl apply -f psql.yaml
kubectl get pvc -n probes-lab
kubectl get pod -n probes-lab -l app=postgres -w
```

## 5. Create App YAML Without Probes

```bash
cat > 00-app-no-probe.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: flask-api-env
  namespace: probes-lab
type: Opaque
stringData:
  DB_HOST: postgres
  DB_PORT: "5432"
  DB_NAME: appdb
  DB_USER: appuser
  DB_PASSWORD: apppassword
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-health-api
  namespace: probes-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask-health-api
  template:
    metadata:
      labels:
        app: flask-health-api
    spec:
      containers:
        - name: api
          image: learndevopsnow123/flask-health-api:1.0
          imagePullPolicy: IfNotPresent
          envFrom:
            - secretRef:
                name: flask-api-env
          ports:
            - name: http
              containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: flask-health-api
  namespace: probes-lab
spec:
  selector:
    app: flask-health-api
  ports:
    - name: http
      port: 80
      targetPort: http
EOF
```

## 6. Deploy App Without Probes

```bash
kubectl apply -f 00-app-no-probe.yaml
kubectl rollout status deployment/flask-health-api -n probes-lab
kubectl get pod -n probes-lab -l app=flask-health-api -w
```

## 7. Test App Routes

```bash
kubectl port-forward --address 172.20.20.10 -n probes-lab svc/flask-health-api 8080:80
```

On Worker Node

```bash
curl -i http://172.20.20.10:8080/
curl -i http://172.20.20.10:8080/healthz
curl -i http://172.20.20.10:8080/readyz
```

## 8. Break DB Without Probes

```bash
kubectl scale statefulset/postgres -n probes-lab --replicas=0
kubectl get pod -n probes-lab -l app=postgres -w
```

```bash
curl -i http://172.20.20.10:8080/
curl -i http://172.20.20.10:8080/healthz
curl -i http://172.20.20.10:8080/readyz
```

```bash
kubectl get pod -n probes-lab -l app=flask-health-api
kubectl describe pod -n probes-lab -l app=flask-health-api
```

```text
Hint:
- no probes = Kubernetes does not know app is unhealthy
- pod still shows READY 1/1
- RESTARTS does not increase
- / returns 500
- /healthz returns 500
- /readyz returns 503
```

```bash
kubectl scale statefulset/postgres -n probes-lab --replicas=1
kubectl get pod -n probes-lab -l app=postgres -w
kubectl delete -f 00-app-no-probe.yaml
```

## 9. Create Liveness Probe YAML

```bash
cat > 01-liveness-probe.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: flask-api-env
  namespace: probes-lab
type: Opaque
stringData:
  DB_HOST: postgres
  DB_PORT: "5432"
  DB_NAME: appdb
  DB_USER: appuser
  DB_PASSWORD: apppassword
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-health-api
  namespace: probes-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask-health-api
  template:
    metadata:
      labels:
        app: flask-health-api
    spec:
      containers:
        - name: api
          image: learndevopsnow123/flask-health-api:1.0
          imagePullPolicy: IfNotPresent
          envFrom:
            - secretRef:
                name: flask-api-env
          ports:
            - name: http
              containerPort: 8080
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            initialDelaySeconds: 15
            periodSeconds: 10
            failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: flask-health-api
  namespace: probes-lab
spec:
  selector:
    app: flask-health-api
  ports:
    - name: http
      port: 80
      targetPort: http
EOF
```
...

## 10. Liveness Probe Demo

### How it checks

```bash
curl http://<<POD_ID>>:8080/healthz
```

```text
0s    Container Started
15s   Liveness Check
25s   Liveness Check
35s   Liveness Check
45s   Liveness Check
```

```bash
kubectl apply -f 01-liveness-probe.yaml
kubectl rollout status deployment/flask-health-api -n probes-lab
kubectl get pod -n probes-lab -l app=flask-health-api -w
```

```bash
kubectl scale statefulset/postgres -n probes-lab --replicas=0
kubectl get pod -n probes-lab -l app=flask-health-api -w
kubectl describe pod -n probes-lab -l app=flask-health-api
```

```text
Hint:
- livenessProbe failed = kubelet restarts the container
- RESTARTS count increases
- pod may show Running, Error, or CrashLoopBackOff
- READY may still show 1/1 because this demo has no readinessProbe
```

```bash
kubectl scale statefulset/postgres -n probes-lab --replicas=1
kubectl get pod -n probes-lab -l app=postgres -w
```

## 11. Reset App Before Readiness Demo

```bash
kubectl delete -f 01-liveness-probe.yaml
```

## 12. Create Readiness Probe YAML

```bash
cat > 02-readiness-probe.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: flask-api-env
  namespace: probes-lab
type: Opaque
stringData:
  DB_HOST: postgres
  DB_PORT: "5432"
  DB_NAME: appdb
  DB_USER: appuser
  DB_PASSWORD: apppassword
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-health-api
  namespace: probes-lab
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask-health-api
  template:
    metadata:
      labels:
        app: flask-health-api
    spec:
      containers:
        - name: api
          image: learndevopsnow123/flask-health-api:1.0
          imagePullPolicy: IfNotPresent
          envFrom:
            - secretRef:
                name: flask-api-env
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 2
---
apiVersion: v1
kind: Service
metadata:
  name: flask-health-api
  namespace: probes-lab
spec:
  selector:
    app: flask-health-api
  ports:
    - name: http
      port: 80
      targetPort: http
EOF
```

## 13. Readiness Probe Demo

```bash
kubectl apply -f 02-readiness-probe.yaml
kubectl rollout status deployment/flask-health-api -n probes-lab
kubectl get pod -n probes-lab -l app=flask-health-api -w
```

```bash
kubectl scale statefulset/postgres -n probes-lab --replicas=0
kubectl get pod -n probes-lab -l app=flask-health-api -w
kubectl describe pod -n probes-lab -l app=flask-health-api

kubectl describe svc flask-health-api -n probes-lab
kubectl get endpoints flask-health-api -n probes-lab
```

```text
Hint:
- readinessProbe failed = pod is not ready
- READY changes to 0/1
- container does not restart
- service removes this pod from endpoints
```

```bash
kubectl scale statefulset/postgres -n probes-lab --replicas=1
kubectl get pod -n probes-lab -l app=postgres -w
kubectl get pod -n probes-lab -l app=flask-health-api -w
```

## 14. Clean Up

```bash
kubectl delete namespace probes-lab
```
