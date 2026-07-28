# Docker Agent Installation

## Docker

The LimaCharlie agent can run in a Docker container and integrates with container environments. In a container, the agent is efficient to deploy and to manage, and it continues to do security monitoring and telemetry collection.

You can also deploy the agent on container cluster technologies such as Kubernetes. For the Kubernetes deployment details, see [Container Clusters](../containers/clusters.md).

## Host Visibility Requirements

The LimaCharlie agent needs these configurations for full visibility of the activity on the host system:

- The container must run in **privileged mode** to access host-level resources.
- The container must use **host networking** to see network activity.
- The container must use **host PID mode** to track the processes that run.
- You must mount **host-level directories** into the container. These include:

  - The root filesystem (`rootfs`)
  - Docker network namespaces (`netns`)
  - The directory that contains the kernel modules and the debug symbols

On newer Linux kernel versions (5.7+), the agent also uses **eBPF** for more visibility and telemetry collection.

## Agent Docker Image

Build your own agent image so you get the latest agent version and control the base distribution:

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
# are mounted within the container.
ENV HOST_FS=/rootfs
ENV NET_NS=/netns

CMD ["./lc_sensor", "-d", "-"]
```

Build the image again at regular intervals so that new deployments get the latest agent version.

!!! warning "eBPF requires a glibc-based image"
    Kernel-level telemetry on Linux is available only for **glibc-based x64 sensors** (Debian, Ubuntu, RHEL/Rocky, etc.). An Alpine (musl) image with the `alpine64` sensor binary always operates in usermode acquisition, without eBPF kernel visibility.

## Available Environment Variables

The agent supports several environment variables that control its behavior:

- `LC_INSTALLATION_KEY` - Gives the installation key that authenticates the agent.
- `HOST_FS` - Gives the path where the host root filesystem is mounted in the container. Example: `/rootfs`.
- `NET_NS` - Gives the path of the host network namespace directory. Example: `/netns`.

Set these variables correctly to make sure that the agent operates as expected.

## Running the Agent Using Docker CLI

To run the LimaCharlie agent in a Docker container, use this command:

```bash
docker run --privileged --net=host \
  -v /:/rootfs:ro \
  -v /var/run/docker/netns:/netns:ro \
  -v /sys/kernel/debug:/sys/kernel/debug:ro \
  -v /sys/kernel/btf:/sys/kernel/btf:ro \
  -v /lib/modules:/lib/modules:ro \
  --env LC_INSTALLATION_KEY=<your_key> \
  --env HOST_FS=/rootfs \
  --env NET_NS=/netns \
  your-registry.example.com/lc-sensor:your-tag
```

Replace `<your_key>` with your LimaCharlie installation key.

## Running the Agent Using Docker Compose

You can also manage the LimaCharlie agent with Docker Compose. This is a sample `docker-compose.yml` file:

```yaml
services:
  lc-sensor:
    image: your-registry.example.com/lc-sensor:your-tag
    restart: unless-stopped
    network_mode: "host"
    pid: "host"
    privileged: true
    environment:
      - HOST_FS=/rootfs
      - NET_NS=/netns
      - LC_INSTALLATION_KEY=<your key>
    deploy:
      resources:
        limits:
          cpus: "0.9"
          memory: "256M"
        reservations:
          cpus: "0.01"
          memory: "128M"
    cap_add:
      - SYS_ADMIN
    volumes:
      - /:/rootfs
      - /var/run/docker/netns:/netns
      - /sys/kernel/debug:/sys/kernel/debug
      - /sys/kernel/btf:/sys/kernel/btf
      - /lib/modules:/lib/modules
```

To start the container, run:

```bash
docker-compose up -d
```

With this setup, the agent runs as a privileged container and has full visibility of the host system. Docker Compose manages the container.
