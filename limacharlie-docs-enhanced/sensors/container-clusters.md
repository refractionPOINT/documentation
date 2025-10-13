# Requires an LC_INSTALLATION_KEY environment variable
# specifying the installation key value.
# Requires a HOST_FS environment variable that specifies where
# the host's root filesystem is mounted within the container
# like "/rootfs".
# Requires a NET_NS environment variable that specific where
# the host's namespaces directory is mounted within the container
# like "/netns".
# Example:
# export ENV HOST_FS=/rootfs
# docker run --privileged --net=host -v /:/rootfs:ro -v /var/run/docker/netns:/netns:ro --env HOST_FS=/rootfs --env NET_NS=/netns --env LC_INSTALLATION_KEY=your_key refractionpoint/limacharlie_sensor

FROM alpine

RUN mkdir lc
WORKDIR /lc

RUN wget https://downloads.limacharlie.io/sensor/linux/alpine64 -O lc_sensor
RUN chmod 500 ./lc_sensor

CMD ./lc_sensor -d -
```

And this is a sample Kubernetes `deployment` on

a cluster supporting eBPF (kernel > 5.7):

```
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
      containers:
        - name: lc-sensor
          image: refractionpoint/limacharlie_sensor:latest
          imagePullPolicy: IfNotPresent
          securityContext:
            allowPrivilegeEscalation: true
            privileged: true
            capabilities:
              add: ['CAP_SYS_ADMIN']
          resources:
            requests:
              memory: 128M
              cpu: 0.01
            limits:
              memory: 256M
              cpu: 0.9
          volumeMounts:
            - mountPath: /rootfs
              name: all-host
            - mountPath: /netns
              name: all-host-ns
            - mountPath: /sys/kernel/debug
              name: all-host-krnl
            - mountPath: /sys/kernel/btf
              name: btf
            - mountPath: /lib/modules
              name: libmodules
          env:
            - name: HOST_FS
              value: /rootfs
            - name: NET_NS
              value: /netns
            - name: LC_INSTALLATION_KEY
              value: <<<< YOUR INSTALLATION KEY GOES HERE >>>>
      volumes:
        - name: all-host
          hostPath:
            path: /
        - name: all-host-ns
          hostPath:
            path: /var/run/docker/netns
        - name: all-host-krnl
          hostPath:
            path: /sys/kernel/debug
        - name: btf
          hostPath:
            path: /sys/kernel/btf
        - name: libmodules
          hostPath:
            path: /lib/modules
```

a cluster not supporting eBPF (kernel < 5.7):

```
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
      containers:
        - name: lc-sensor
          image: refractionpoint/limacharlie_sensor:latest
          imagePullPolicy: IfNotPresent
          securityContext:
            allowPrivilegeEscalation: true
            privileged: true
          resources:
            requests:
              memory: 128M
              cpu: 0.01
            limits:
              memory: 256M
              cpu: 0.9
          volumeMounts:
            - mountPath: /rootfs
              name: all-host-fs
            - mountPath: /netns
              name: all-host-ns
          env:
            - name: HOST_FS
              value: /rootfs
            - name: NET_NS
              value: /netns
            - name: LC_INSTALLATION_KEY
              value: <<<< YOUR INSTALLATION KEY GOES HERE >>>>
      volumes:
        - name: all-host-fs
          hostPath:
            path: /
        - name: all-host-ns
          hostPath:
            path: /var/run/docker/netns
      hostNetwork: true
```

#### SELinux

On some hardened versions of Linux, certain file paths are prevented from loading `.so` (Shared Object) files. LimaCharlie requires a location where
 it can write `.so` files and load them. To enable this on hardened versions of Linux, you can specify a `LC_MOD_LOAD_LOC` environment variable containing
 a path to a valid directory for loading, like `/lc` for example. This environment variable needs to be set for the sensor executable (`rphcp`) at runtime.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.