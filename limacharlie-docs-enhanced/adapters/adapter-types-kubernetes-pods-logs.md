# Kubernetes Pods Specific Docs: https://docs.limacharlie.io/docs/adapter-types-k8s-pods

sensor_type: "k8_pods"
k8s_pods:
 В  В client_options:
 В  В  В identity:
 В  В  В  В oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
 В  В  В  В installation_key: "YOUR_LC_INSTALLATION_KEY_K8SPODS"
 В  В  В hostname: "k8s-worker-node"
 В  В  В platform: "k8s_pods"
 В  В  В sensor_seed_key: "k8s-pods-sensor"
 В  В root: "/var/log/pods" В  В  В  В  В  В  В  В  В  В  В  В  В  В  В # Required: Pod logs directory
 В  В write_timeout_sec: 600 В  В  В  В  В  В  В  В  В  В  В  В  В  В  # Optional: defaults to 600
 В  В include_pods_re: "^production_.*" В  В  В  В  В  В  В  В  В # Optional: include filter
 В  В exclude_pods_re: "^kube-system_kube-proxy-.*$" В  В # Optional: exclude filter
```

## Sample Kubernetes Configuration

An example Daemon Set configuration for Kubernetes:

```
apiVersion: apps/v1
kind: DaemonSet
metadata:
 В name: lc-adapter-k8s-pods
 В namespace: default
spec:
 В minReadySeconds: 30
 В selector:
 В  В matchLabels:
 В  В  В name: lc-adapter-k8s-pods
 В template:
 В  В metadata:
 В  В  В labels:
 В  В  В  В name: lc-adapter-k8s-pods
 В  В spec:
 В  В  В containers:
 В  В  В - image: refractionpoint/lc-adapter-k8s-pods
 В  В  В  В name: lc-adapter-k8s-pods
 В  В  В  В volumeMounts:
 В  В  В  В - mountPath: /k8s-pod-logs
 В  В  В  В  В name: pod-logs
 В  В  В  В env:
 В  В  В  В - name: K8S_POD_LOGS
 В  В  В  В  В value: /k8s-pod-logs
 В  В  В  В - name: OID
 В  В  В  В  В value: aaaaaaaa-bfa1-bbbb-cccc-138cd51389cd
 В  В  В  В - name: IKEY
 В  В  В  В  В value: aaaaaaaa-9ae6-bbbb-cccc-5e42b854adf5
 В  В  В  В - name: NAME
 В  В  В  В  В value: k8s-pods
 В  В  В volumes:
 В  В  В - hostPath:
 В  В  В  В  В path: /var/log/pods
 В  В  В  В name: pod-logs
 В updateStrategy:
 В  В rollingUpdate:
 В  В  В maxUnavailable: 1
 В  В type: RollingUpdate
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.В

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.