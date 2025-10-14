# Mitigation

The following sensor commands perform mitigation actions against EDR sensors.

## deny_tree

Tells the sensor that all activity starting at a specific process (and its children) should be denied and killed. This particular command is excellent for ransomware mitigation.

**Platforms:**

**Usage:**

```
usage: deny_tree [-h] atom [atom ...]

positional arguments:
  atom        atoms to deny from
```

## rejoin_network

Tells the sensor to allow network connectivity again (after it was segregated).

**Platforms:**

**Return Event:**
 [REJOIN_NETWORK](/v1/docs/reference-events-responses-mitigation#REJOIN_NETWORK)

**Usage:**

```
usage: rejoin_network [-h]
```

## segregate_network

Tells the sensor to stop all network connectivity on the host except LC comms to the backend. So it's network isolation, great to stop lateral movement.

Note that you should never upgrade a sensor version while the network is isolated through this mechanism. Doing so may result in the agent not regaining connectivity to the cloud, requiring a reboot to undo.

This command primitive is NOT persistent, meaning a sensor you segregate from the network using this command alone, upon reboot will rejoin the network. To achieve isolation from the network in a persistent way, see the `isolate network` and `rejoin network` [Detection & Response rule actions](/v1/docs/detection-and-response).

**Platforms:**

**Return Event:**
 [SEGREGATE_NETWORK](/v1/docs/reference-events-responses-mitigation#SEGREGATE_NETWORK)

**Usage:**

```
usage: segregate_network [-h]
```