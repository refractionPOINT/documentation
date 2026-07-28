# Container Clusters

You can run LimaCharlie at the host level in a container cluster system such as Kubernetes. One sensor then monitors all the containers that run on the host. This is the preferred method because it reduces the overhead of LC in each container.

A combination of techniques makes this possible:

1. A privileged container that runs LC.
2. LC runs with the `HOST_FS` environment variable set to the host root filesystem that is mounted in the container.
3. LC runs with the `NET_NS` environment variable set to the host directory that lists the network namespaces.
4. The container runs with the flags and mounts that give it the necessary access.

## Building the Container Image

Build your own sensor image and push it to a registry that your cluster nodes can pull from. When you build the image yourself, you get the latest sensor version and you control the base distribution.

!!! warning "eBPF requires a glibc-based image"
    An eBPF component supplies the kernel-level telemetry on Linux, and this component is available only for **glibc-based x64 sensors**. The `alpine64` (musl) sensor build does **not** get the eBPF component and always operates in usermode acquisition. Do not use Alpine if you want kernel-level visibility (real-time process, file, network and DNS events from eBPF). Your container must use a glibc-based distribution (Debian, Ubuntu, RHEL/Rocky, etc.) with the `linux/64` sensor binary.

This is a sample `Dockerfile` for a glibc-based sensor container:

```dockerfile
# Requires an LC_INSTALLATION_KEY environment variable at runtime
# specifying the installation key value.
FROM debian:12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /lc

# Fetch the latest official glibc x64 sensor at build time.
RUN curl -fsSL https://downloads.limacharlie.io/sensor/linux/64 -o lc_sensor \
    && chmod 500 ./lc_sensor

# Where the host's root filesystem and network namespaces directory
# are mounted within this container.
ENV HOST_FS=/rootfs
ENV NET_NS=/netns

CMD ["./lc_sensor", "-d", "-"]
```

Build this image again at regular intervals, or on a schedule in your CI, so that new deployments get the latest sensor version. Use a unique image tag for each build. If you use a tag again with an image pull policy that is not `Always`, the nodes can keep an old cached image.

## Plain Docker

On a host that runs dockerd, start the container like this:

```bash
docker run --privileged --net=host \
  -v /:/rootfs:ro \
  -v /var/run/docker/netns:/netns:ro \
  --env HOST_FS=/rootfs \
  --env NET_NS=/netns \
  --env LC_INSTALLATION_KEY=your_key \
  your-registry.example.com/lc-sensor:your-tag
```

The path `/var/run/docker/netns` applies to dockerd only. On hosts that use containerd with CNI, including most managed Kubernetes node images, the directory of the network namespaces is `/var/run/netns`.

## Kubernetes DaemonSet (eBPF)

The recommended deployment on Kubernetes is a `DaemonSet`, so that one sensor runs on each node. The manifest below is for clusters with kernels 5.8 and later that support eBPF. The manifest is validated on GKE.

The eBPF path needs these items. The manifest below supplies all of them:

- A **glibc-based** sensor image (see above).
- `privileged: true`, `hostPID: true` and `hostNetwork: true`.
- Kernel BTF (`/sys/kernel/btf/vmlinux`), that is, a kernel built with `CONFIG_DEBUG_INFO_BTF`. All current mainstream distributions and managed-Kubernetes node images include it.
- The `/sys/kernel/debug` directory of the host (debugfs/tracefs), mounted into the container. This item is important: debugfs and tracefs are separate filesystems that are **not** visible through the `/sys` mount of the container, and the eBPF loader needs tracefs to attach tracepoints. Without this mount, the sensor changes to usermode acquisition and gives no message.

First, create the namespace and put your installation key in a secret. Do not commit the key to source control:

```bash
kubectl create namespace lc-monitoring
kubectl create secret generic lc-sensor-enrollment \
  -n lc-monitoring \
  --from-literal=installation-key='<<<YOUR INSTALLATION KEY>>>'
```

Then deploy the DaemonSet:

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
      maxUnavailable: 1
  selector:
    matchLabels:
      app: lc-monitoring
  template:
    metadata:
      namespace: lc-monitoring
      labels:
        app: lc-monitoring
    spec:
      hostNetwork: true
      hostPID: true
      dnsPolicy: ClusterFirstWithHostNet
      nodeSelector:
        kubernetes.io/os: linux
        kubernetes.io/arch: amd64
      # Run on every node, including tainted node pools.
      tolerations:
        - operator: Exists
      containers:
        - name: lc-sensor
          # The image you built from the Dockerfile above, pushed to a
          # registry your nodes can pull from.
          image: your-registry.example.com/lc-sensor:your-tag
          imagePullPolicy: Always
          securityContext:
            allowPrivilegeEscalation: true
            privileged: true
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
          volumeMounts:
            - mountPath: /rootfs
              name: host-root
              readOnly: true
            # containerd/CNI network namespaces. On dockerd-based nodes
            # use /var/run/docker/netns as the hostPath instead.
            - mountPath: /netns
              name: host-netns
              readOnly: true
            # debugfs/tracefs, required for eBPF tracepoint attachment.
            - mountPath: /sys/kernel/debug
              name: host-debugfs
            # Kernel BTF for eBPF program loading.
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
        - name: host-btf
          hostPath:
            path: /sys/kernel/btf
        - name: host-libmodules
          hostPath:
            path: /lib/modules
```

### Scheduling on tightly-packed nodes

Cluster autoscalers that optimize utilization can leave nodes with almost no unallocated CPU. The DaemonSet pod cannot then schedule on those nodes. To correct this, give the sensor a `PriorityClass` with a high value. The sensor can then preempt workloads that have a lower priority:

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: node-monitoring-critical
value: 1000000
globalDefault: false
description: "Host-level security monitoring agents."
```

Then add `priorityClassName: node-monitoring-critical` to the DaemonSet pod spec.

!!! note
    Do not use the built-in `system-node-critical` or `system-cluster-critical` classes. On GKE and other managed platforms, a resource quota restricts them to the `kube-system` namespace, and pod creation fails with a `FailedCreate` quota error.

### Sensor identity lifecycle

The sensor keeps its identity in the container filesystem, which is ephemeral. Each pod start (node reboot, DaemonSet update, pod eviction) enrolls a **new** sensor with a new SID. This is the expected behavior for elastic node fleets, and the old registrations go offline. Use the [Sensor Cull extension](../../../5-integrations/extensions/limacharlie/sensor-cull.md) to delete the old registrations automatically. Make sure that your sensor quota is large enough for the number of nodes that are online at the same time.

## Google Kubernetes Engine (GKE)

The manifest above works without changes on **GKE Standard** clusters, and it is validated end-to-end (the sensors enroll and report that kernel/eBPF acquisition is active):

- The default node images (Container-Optimized OS and Ubuntu, containerd runtime) have kernels with BTF enabled and debugfs mounted on the host. They obey the eBPF requirements.
- GKE nodes use containerd, so the network namespaces hostPath is `/var/run/netns`, as in the manifest above. It is not the dockerd path that some older examples show.
- If your cluster uses the `optimize-utilization` autoscaling profile, add the custom `PriorityClass` above. Without it, some nodes can fail to schedule the sensor.

!!! warning "GKE Autopilot is not supported"
    Deploy on GKE Standard. Autopilot clusters reject privileged containers, `hostPath` volumes, `hostPID`, and `hostNetwork`, and host-level monitoring needs all of them.

Nodes that run gVisor-sandboxed pods (GKE Sandbox) can run the sensor. But the gVisor user-space kernel executes the activity in the sandboxed pods, and host-level kernel telemetry cannot see most of that activity.

## Verifying eBPF is active

After deployment, check that the sensors use kernel-level (eBPF) acquisition and not the usermode fallback:

- In the web app, the sensor details show if kernel acquisition is available.
- In the API/SDK, the sensor information includes `is_kernel_available: true`.
- Sensor selector expressions can filter on it: `plat == linux and kernel == true`.

If `is_kernel_available` is false on a Linux deployment, these are the usual causes: an Alpine-based image (no eBPF support), a missing `/sys/kernel/debug` mount, a kernel without BTF, or a container that is not privileged.

## Kubernetes DaemonSet (no eBPF)

For clusters with older kernels (before 5.8), or clusters that cannot obey the eBPF prerequisites, deploy the same DaemonSet without the `/sys/kernel/debug`, `/sys/kernel/btf` and `/lib/modules` mounts. The sensor then operates in usermode acquisition automatically. It gets the process events from the process-events netlink connector of the kernel, plus periodic state snapshots. Host-level visibility still needs `privileged`, `hostPID`, `hostNetwork` and the `HOST_FS` / `NET_NS` mounts.

## SELinux

On some hardened versions of Linux, some file paths cannot load `.so` (Shared Object) files. LimaCharlie needs a location where it can write `.so` files and load them. On these versions of Linux, set the `LC_MOD_LOAD_LOC` environment variable to the path of a directory that permits loading, for example `/lc`. Set this environment variable for the sensor executable (`rphcp`) at runtime.
