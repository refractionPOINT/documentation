# Amazon EKS on Bottlerocket

[Bottlerocket](https://github.com/bottlerocket-os/bottlerocket) is the container-optimized OS AWS offers for EKS node groups. Compared to a general-purpose distribution it has a few properties that affect host-level monitoring:

- The root filesystem is read-only and integrity-checked with dm-verity.
- SELinux runs in enforcing mode.
- There is no package manager and no shell on the host. You reach the host through the "control" and "admin" host containers.
- Pods run on containerd.

None of these prevent the sensor from running. The sensor never installs anything on the host. It runs as a privileged `DaemonSet` pod, reads the host through read-only mounts, and writes only inside its own container filesystem. The general approach is the one described in [Container Clusters](clusters.md). This page covers what is specific to Bottlerocket and gives a complete manifest.

## How the sensor fits Bottlerocket's protections

### Read-only root filesystem

The sensor does not need to write to the host. Everything it writes stays inside its own container:

| What | Default location inside the container |
|---|---|
| Sensor identity, configuration and status files | `/opt/limacharlie` (override with `LC_DATA_DIRECTORY`) |
| Temporary files used to load sensor modules | `/tmp` (override with `LC_MOD_LOAD_LOC`) |
| A private cgroup2 mount used by kernel-level network and DNS collection | The container's working directory |

The manifest below mounts the host's root filesystem, network namespaces and kernel BTF read-only. Only debugfs and tracefs are mounted read-write, because the eBPF loader needs them. The sensor loads modules from a file on disk, so the locations above must allow executing files. A container's own filesystem allows this by default.

!!! warning "Do not set `readOnlyRootFilesystem` on the sensor container"
    Bottlerocket's read-only root applies to the host, not to pods. The sensor container itself needs a writable filesystem for the files listed above. If a policy engine (Kyverno, OPA Gatekeeper, etc.) forces `readOnlyRootFilesystem: true` on every pod, either exempt the sensor's namespace, or mount writable `emptyDir` volumes at `/opt/limacharlie`, `/tmp` and the container's working directory (`/lc` with the sample Dockerfile, which means moving the sensor binary to a different directory such as `/usr/local/bin`).

### SELinux

Bottlerocket's SELinux policy gives each container a label based on how it was started:

- `container_t` for ordinary containers.
- `control_t` for privileged containers. Kubernetes pods with `privileged: true` get this label automatically.
- `super_t` for "superpowered" containers. You have to request this one explicitly.

The sensor needs only the default `control_t` label. Bottlerocket's policy lets that label read any file on the host, execute files from the container's own filesystem, use `bpf()` and `perf_event_open()`, and create mounts inside the container. That covers everything the sensor does. It cannot modify the host OS, which the sensor never attempts.

Leave `seLinuxOptions` unset in the pod spec:

- Do not request `super_t`. The sensor does not need it, and [Bottlerocket's security guidance](https://github.com/bottlerocket-os/bottlerocket/blob/develop/SECURITY_GUIDANCE.md#limit-use-of-privileged-selinux-labels) recommends against granting it.
- Do not force `container_t`. Under that label the sensor cannot read most of the host.

You do not need `LC_MOD_LOAD_LOC` on Bottlerocket. The [SELinux note](clusters.md#selinux) on the Container Clusters page applies to hardened distributions where the sensor runs directly on the host and the host's default temporary directory blocks loading shared objects. In a pod, the sensor's temporary directory is inside the container.

### Kernel lockdown

Bottlerocket supports three kernel lockdown modes, set with `settings.kernel.lockdown`:

| Mode | Effect on the sensor |
|---|---|
| `none` | No effect. NVIDIA variants use this mode by default. |
| `integrity` | No effect. This is the default on most variants and what Bottlerocket recommends. |
| `confidentiality` | Blocks the eBPF and perf features the sensor uses for kernel-level telemetry. The sensor still runs, but falls back to usermode collection. |

Keep `integrity` (or `none` on NVIDIA nodes). To check a node, open a session to its control container (for example with SSM Session Manager) and run:

```bash
apiclient get settings.kernel.lockdown
```

To pin the mode in your node group's user data:

```toml
[settings.kernel]
lockdown = "integrity"
```

### eBPF prerequisites

Current Bottlerocket kernels meet the [eBPF requirements](clusters.md#kubernetes-daemonset-ebpf) on their own:

- They are built with BTF (`/sys/kernel/btf/vmlinux`), kprobes and cgroup BPF support.
- Bottlerocket mounts debugfs at `/sys/kernel/debug` and tracefs at `/sys/kernel/tracing` on the host at boot.

Debugfs and tracefs are separate filesystems that a container does not see through its own `/sys` mount. The manifest below mounts both host paths into the pod. This differs from the generic manifest, which mounts only `/sys/kernel/debug`. On Bottlerocket tracefs has its own mount point, and mounting both lets the eBPF loader find tracefs at either location.

### Network namespaces

EKS nodes use containerd, which creates pod network namespaces under `/var/run/netns`. Mount that path and point `NET_NS` at it, as the manifest below does. The `/var/run/docker/netns` path shown in plain Docker examples does not exist on Bottlerocket.

## Deploying

### 1. Build and publish the sensor image

Build the image from the [glibc-based Dockerfile](clusters.md#building-the-container-image) on the Container Clusters page and push it to a registry your nodes can pull from. On EKS that is usually an ECR repository. The standard EKS node IAM role can already pull from ECR in the same account.

The manifest below targets x64 nodes (`kubernetes.io/arch: amd64`), matching the eBPF requirement described on the Container Clusters page. If your cluster also has Graviton (arm64) node groups, contact LimaCharlie support before rolling the sensor out to them.

### 2. Create the namespace and the installation key secret

```bash
kubectl create namespace lc-monitoring
kubectl create secret generic lc-sensor-enrollment \
  -n lc-monitoring \
  --from-literal=installation-key='<<<YOUR INSTALLATION KEY>>>'
```

If your cluster enforces [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/), the namespace must allow privileged pods:

```bash
kubectl label namespace lc-monitoring \
  pod-security.kubernetes.io/enforce=privileged \
  pod-security.kubernetes.io/warn=privileged \
  pod-security.kubernetes.io/audit=privileged
```

### 3. Deploy the DaemonSet

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: lc-sensor
  namespace: lc-monitoring
  labels:
    app: lc-monitoring
spec:
  minReadySeconds: 30
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      # Replace one node's sensor at a time. Do not set maxSurge: two sensor
      # pods on the same node at once cannot both run kernel-level collection.
      maxUnavailable: 1
  selector:
    matchLabels:
      app: lc-monitoring
  template:
    metadata:
      labels:
        app: lc-monitoring
    spec:
      hostNetwork: true
      hostPID: true
      dnsPolicy: ClusterFirstWithHostNet
      nodeSelector:
        kubernetes.io/os: linux
        kubernetes.io/arch: amd64
      # Run on every node, including tainted node groups.
      tolerations:
        - operator: Exists
      containers:
        - name: lc-sensor
          image: <account>.dkr.ecr.<region>.amazonaws.com/lc-sensor:<tag>
          imagePullPolicy: Always
          securityContext:
            privileged: true
            allowPrivilegeEscalation: true
            # No seLinuxOptions: Bottlerocket labels privileged pods
            # control_t, which is what the sensor needs.
          resources:
            requests:
              memory: 64Mi
              cpu: 0.01
            limits:
              memory: 512Mi
              cpu: 0.9
          env:
            - name: HOST_FS
              value: /rootfs
            - name: NET_NS
              value: /netns
            - name: LC_INSTALLATION_KEY
              valueFrom:
                secretKeyRef:
                  name: lc-sensor-enrollment
                  key: installation-key
            # If nodes reach the internet through an HTTP CONNECT proxy:
            # - name: LC_PROXY
            #   value: proxy.example.com:3128
          volumeMounts:
            - mountPath: /rootfs
              name: host-root
              readOnly: true
            - mountPath: /netns
              name: host-netns
              readOnly: true
            - mountPath: /sys/kernel/debug
              name: host-debugfs
            - mountPath: /sys/kernel/tracing
              name: host-tracefs
            - mountPath: /sys/kernel/btf
              name: host-btf
              readOnly: true
            - mountPath: /lib/modules
              name: host-libmodules
              readOnly: true
      volumes:
        - name: host-root
          hostPath:
            path: /
        - name: host-netns
          hostPath:
            path: /var/run/netns
        - name: host-debugfs
          hostPath:
            path: /sys/kernel/debug
        - name: host-tracefs
          hostPath:
            path: /sys/kernel/tracing
        - name: host-btf
          hostPath:
            path: /sys/kernel/btf
        - name: host-libmodules
          hostPath:
            path: /lib/modules
```

If the cluster autoscaler packs nodes tightly, add the `PriorityClass` described in [Scheduling on tightly-packed nodes](clusters.md#scheduling-on-tightly-packed-nodes).

### Optional: keep the same sensor identity across pod restarts

By default the sensor keeps its identity inside the container. Every new pod enrolls as a new sensor, including after a DaemonSet update or a pod eviction on the same node (see [Sensor identity lifecycle](clusters.md#sensor-identity-lifecycle)). That is usually fine for autoscaled node groups.

If you want one sensor per node for the node's whole lifetime, store the identity on the node's persistent `/var` volume. Add this to the container's `env` and `volumeMounts`, and to the pod's `volumes`:

```yaml
          env:
            - name: LC_DATA_DIRECTORY
              value: /lc-data
          volumeMounts:
            - mountPath: /lc-data
              name: lc-data
      volumes:
        - name: lc-data
          hostPath:
            path: /var/lib/limacharlie
            type: DirectoryOrCreate
```

Keep these points in mind:

- This directory holds the sensor's enrollment credentials. Only root on the node and pods that mount it can read it. Do not mount it into any other workload.
- Mount only this dedicated directory. Bottlerocket's guidance is to avoid mounting `/var`, `/local` or `/opt` as a whole into privileged containers.
- Replacing a node still produces a new sensor, because the new node starts with an empty disk. Use the [Sensor Cull extension](../../../5-integrations/extensions/limacharlie/sensor-cull.md) to clean up sensors from retired nodes.

## Network requirements

The sensor opens one outbound TLS connection, on port 443 by default, to your organization's LimaCharlie datacenter. The installation key determines which datacenter. It needs no inbound ports. With `hostNetwork: true` the connection uses the node's own network path, so the node's security groups and any egress firewall must allow it.

If nodes reach the internet only through an HTTP CONNECT proxy, set `LC_PROXY` to `host:port` (see the commented entry in the manifest and [Sensor Connectivity](../../connectivity.md#proxy-tunneling)). The sensor ignores `HTTP_PROXY` and `HTTPS_PROXY`.

## Verifying the deployment

1. Check that one pod is running on every node:

    ```bash
    kubectl get pods -n lc-monitoring -o wide
    ```

2. In the web app, confirm that one sensor per node shows as online.
3. Confirm the sensors are using kernel-level (eBPF) collection, as described in [Verifying eBPF is active](clusters.md#verifying-ebpf-is-active). The sensor selector `plat == linux and kernel == true` should match every node.

If a sensor connects but reports no kernel-level collection, check these causes, in order of likelihood on Bottlerocket:

| Cause | How to check |
|---|---|
| The node uses `confidentiality` lockdown | `apiclient get settings.kernel.lockdown` in the node's control container |
| The `/sys/kernel/debug` or `/sys/kernel/tracing` mount is missing | `kubectl get ds lc-sensor -n lc-monitoring -o yaml` |
| A policy engine changed the pod's SELinux label, or removed `privileged: true` | `kubectl get pod <pod> -n lc-monitoring -o yaml`, under `securityContext` |
| The image is Alpine-based | The image must use the `linux/64` sensor on a glibc distribution |
| An SELinux denial | From the admin container, run `sudo sheltie`, then look for `avc` messages in the `journalctl` output |

### Sensor logs

A release sensor writes no logs by default. Bottlerocket has no host shell, so the most practical way to troubleshoot is to have the sensor log to the pod's output. Temporarily add `RPAL_LOG_LEVEL=info` to the container's environment, then read the output with `kubectl logs -n lc-monitoring <pod>`. Without `RPAL_LOG_FILE` the sensor writes its logs to standard error, which is what `kubectl logs` shows. This needs sensor 5.3.9 or newer, which an image built from the sample Dockerfile always gets. Older sensors used `LC_VERBOSE=1` instead. Remove the variable when you are done, because the logs can contain operational details about the host.

## Environment variables used in this deployment

| Variable | Required | Value in this guide | Purpose |
|---|---|---|---|
| `LC_INSTALLATION_KEY` | Yes | From the `lc-sensor-enrollment` secret | Installation key used to enroll the sensor. |
| `HOST_FS` | Yes | `/rootfs` | Where the host's root filesystem is mounted in the container. The sensor reads host processes and files through it. |
| `NET_NS` | Yes | `/netns` | Where the host's network namespaces directory (`/var/run/netns`) is mounted, so the sensor can collect network activity from every pod. |
| `LC_PROXY` | No | Unset | HTTP CONNECT proxy (`host:port`) for the cloud connection. |
| `LC_DATA_DIRECTORY` | No | Unset (`/opt/limacharlie` in the container) | Where the sensor stores its identity and state. Set it only for the persistent identity option above. |
| `RPAL_LOG_LEVEL` | No | Unset | Set to `info` temporarily to log to the pod's output. |

The full list of sensor environment variables is in the [CLI reference](../cli-reference.md).
