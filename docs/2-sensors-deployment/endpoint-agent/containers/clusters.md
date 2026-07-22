# Container Clusters

You can run LimaCharlie at the host level in a container cluster system like Kubernetes in order to monitor all running containers on the host with a single Sensor. This is the preferred method as it reduces the overhead of running LC within every single container.

This is accomplished by a combination of a few techniques:

1. A privileged container running LC.
2. LC runs with the `HOST_FS` environment variable pointing to the host's root filesystem mounted within the container.
3. LC runs with the `NET_NS` environment variable pointing to the host's directory listing network namespaces.
4. Running the container with the required flags and mounts to make sure it can have proper access.

## Building the Container Image

Build your own sensor image and push it to a registry your cluster nodes can pull from. Building the image yourself guarantees you get the latest sensor version and lets you control the base distribution.

!!! warning "eBPF requires a glibc-based image"
    Kernel-level telemetry on Linux is delivered by an eBPF component that is only available for **glibc-based x64 sensors**. The `alpine64` (musl) sensor build does **not** receive the eBPF component and will always operate in usermode acquisition. If you want kernel-level visibility (real-time process, file, network and DNS events from eBPF), your container must use a glibc-based distribution (Debian, Ubuntu, RHEL/Rocky, etc.) with the `linux/64` sensor binary — do not use Alpine.

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

Rebuild this image regularly (or on a schedule in your CI) so new deployments pick up the latest sensor version, and use a unique image tag per build — reusing a tag combined with a non-`Always` image pull policy can leave nodes running a stale cached image.

## Plain Docker

On a host running dockerd, start the container like:

```bash
docker run --privileged --net=host \
  -v /:/rootfs:ro \
  -v /var/run/docker/netns:/netns:ro \
  --env HOST_FS=/rootfs \
  --env NET_NS=/netns \
  --env LC_INSTALLATION_KEY=your_key \
  your-registry.example.com/lc-sensor:your-tag
```

Note that `/var/run/docker/netns` is specific to dockerd. On hosts using containerd with CNI (including most managed Kubernetes node images), the network namespaces directory is `/var/run/netns` instead.

## Kubernetes DaemonSet (eBPF)

The recommended deployment on Kubernetes is a `DaemonSet` so that one sensor runs on every node. The manifest below is suitable for clusters with modern kernels (5.8+) supporting eBPF, and has been validated on GKE.

Requirements for the eBPF path, all handled by the manifest below:

- A **glibc-based** sensor image (see above).
- `privileged: true`, `hostPID: true` and `hostNetwork: true`.
- Kernel BTF (`/sys/kernel/btf/vmlinux`), i.e. a kernel built with `CONFIG_DEBUG_INFO_BTF`. All modern mainstream distributions and managed-Kubernetes node images ship this.
- The host's `/sys/kernel/debug` (debugfs/tracefs) mounted into the container. This one matters: debugfs and tracefs are separate filesystems that are **not** visible through the container's own `/sys` mount, and the eBPF loader needs tracefs to attach tracepoints. Without this mount the sensor silently falls back to usermode acquisition.

First, create the namespace and store your installation key in a secret (avoid committing the key to source control):

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

Cluster autoscalers that optimize for utilization can leave nodes with almost no unallocated CPU, preventing the DaemonSet pod from scheduling there. The fix is to give the sensor a `PriorityClass` with a high value so it can preempt lower-priority workloads:

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
    Do not use the built-in `system-node-critical` / `system-cluster-critical` classes: on GKE (and other managed platforms) they are restricted by resource quota to the `kube-system` namespace, and pod creation will fail with a `FailedCreate` quota error.

### Sensor identity lifecycle

The sensor stores its identity inside the container filesystem, which is ephemeral: every pod start (node reboot, DaemonSet update, pod eviction) enrolls as a **new** sensor with a new SID. This is the expected behavior for elastic node fleets — old registrations simply go offline. Use the [Sensor Cull extension](../../../5-integrations/extensions/limacharlie/sensor-cull.md) to automatically clean up stale registrations, and make sure your sensor quota accommodates the number of concurrently online nodes.

## Google Kubernetes Engine (GKE)

The manifest above works as-is on **GKE Standard** clusters and has been validated end-to-end (sensors enroll and report kernel/eBPF acquisition active):

- Default node images (Container-Optimized OS and Ubuntu, containerd runtime) ship kernels with BTF enabled and debugfs mounted on the host, satisfying the eBPF requirements.
- GKE nodes use containerd, so the network namespaces hostPath is `/var/run/netns` as in the manifest above (not the dockerd path shown in some older examples).
- If your cluster uses the `optimize-utilization` autoscaling profile, add the custom `PriorityClass` described above or some nodes may never schedule the sensor.

!!! warning "GKE Autopilot is not supported"
    Autopilot clusters reject privileged containers, `hostPath` volumes, `hostPID` and `hostNetwork`, all of which are required for host-level monitoring. Deploy on GKE Standard.

Nodes running gVisor-sandboxed pods (GKE Sandbox) can run the sensor, but activity inside the sandboxed pods is executed by the gVisor user-space kernel and is largely invisible to host-level kernel telemetry.

## Verifying eBPF is active

After deployment, verify that sensors are using kernel-level (eBPF) acquisition and not the usermode fallback:

- In the web app, the sensor details show whether kernel acquisition is available.
- Via the API/SDK, the sensor information includes `is_kernel_available: true`.
- Sensor selector expressions can filter on it: `plat == linux and kernel == true`.

If `is_kernel_available` is false on a Linux deployment, the usual causes are: an Alpine-based image (no eBPF support), a missing `/sys/kernel/debug` mount, a kernel without BTF, or a non-privileged container.

## Kubernetes DaemonSet (no eBPF)

For clusters with older kernels (before 5.8) or where the eBPF prerequisites cannot be met, deploy the same DaemonSet without the `/sys/kernel/debug`, `/sys/kernel/btf` and `/lib/modules` mounts. The sensor will automatically operate in usermode acquisition (process events via the kernel's process-events netlink connector, plus periodic state snapshots); `privileged`, `hostPID`, `hostNetwork` and the `HOST_FS` / `NET_NS` mounts are still required for host-level visibility.

## SELinux

On some hardened versions of Linux, certain file paths are prevented from loading `.so` (Shared Object) files. LimaCharlie requires a location where it can write `.so` files and load them. To enable this on hardened versions of Linux, you can specify a `LC_MOD_LOAD_LOC` environment variable containing a path to a valid directory for loading, like `/lc` for example. This environment variable needs to be set for the sensor executable (`rphcp`) at runtime.
