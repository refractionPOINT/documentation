# Docker Agent Installation
## Docker

The LimaCharlie agent is designed to run within a Docker container, providing seamless integration with containerized environments. Running the agent in a container allows for efficient deployment and management while ensuring security monitoring and telemetry collection.

Additionally, the agent can also be deployed on various container cluster technologies, such as Kubernetes. For Kubernetes deployment details, refer to [Container Clusters](https://docs.limacharlie.io/docs/container-clusters).

### Host Visibility Requirements

For the LimaCharlie agent to have full visibility into activities on the host system, the following configurations are required:

* The container must run in **privileged mode** to access host-level resources.
* The container must use **host networking** to observe network activity.
* The container must use **host PID mode** to track running processes.
* Various **host-level directories** must be mounted into the container, including:

  + The root filesystem (`rootfs`)
  + Docker network namespaces (`netns`)
  + The directory containing kernel modules and debug symbols

Additionally, on newer Linux kernel versions (5.7+), the agent leverages **eBPF** for enhanced visibility and telemetry collection.

#### Agent Docker Image

A publicly available Docker image for the LimaCharlie agent is hosted on [Docker Hub](https://hub.docker.com/r/refractionpoint/limacharlie_sensor):

```
docker pull refractionpoint/limacharlie_sensor:latest
```

##### Image Flavors

Docker image is available in different flavors based on specific distributions:

* `latest` - Default version based on CentOS Linux.
* `alpine` - Based on Alpine Linux (smaller image size).
* `centos` - Based on CentOS Linux.

#### Available Environment Variables

The agent supports several environment variables to control its behavior:

* `LC_INSTALLATION_KEY` - Specifies the installation key required to authenticate the agent.
* `HOST_FS` - Defines the path where the host's root filesystem is mounted within the container. Example: `/rootfs`.
* `NET_NS` - Specifies the path to the host's network namespace directory. Example: `/netns`.

These variables must be configured appropriately to ensure the agent functions as expected.

#### Running the Agent Using Docker CLI

To run the LimaCharlie agent in a Docker container, use the following command:

```
docker run --privileged --net=host \
  -v /:/rootfs:ro \
  -v /var/run/docker/netns:/netns:ro \
  -v /sys/kernel/debug:/sys/kernel/debug:ro \
  -v /sys/kernel/btf:/sys/kernel/btf:ro \
  -v /lib/modules:/lib/modules:ro \
  --env LC_INSTALLATION_KEY=<your_key> \
  --env HOST_FS=/rootfs \
  --env NET_NS=/netns \
  refractionpoint/limacharlie_sensor:latest
```

Ensure that you replace `<your_key>` with your actual LimaCharlie installation key.

#### Running the Agent Using Docker Compose

You can also manage the LimaCharlie agent using Docker Compose. Below is a sample `docker-compose.yml` file:

```
services:
  lc-sensor:
    image: refractionpoint/limacharlie_sensor:latest
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

```
docker-compose up -d
```

This setup ensures the agent runs as a privileged container, enabling full visibility into the host system while being managed through Docker Compose.

#### Building a Custom Docker Image

If you need to create a custom Docker image incorporating the LimaCharlie agent, you can use the following Dockerfile as a base:

```
FROM alpine

RUN mkdir /lc
WORKDIR /lc

RUN wget https://downloads.limacharlie.io/sensor/linux/alpine64 -O lc_sensor
RUN chmod 500 ./lc_sensor

CMD ["./lc_sensor", "-d", "-"]
```

Build the image using:

```
docker build -t my-lc-agent .
```

---

##### Related articles

* [Kubernetes Pods Logs](/docs/adapter-types-kubernetes-pods-logs)
* [Container Clusters](/docs/container-clusters)

---

###### What's Next

* [Edge Agent Installation](/docs/edge-agent-installation)

Tags

* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [linux](/docs/en/tags/linux)
* [sensors](/docs/en/tags/sensors)