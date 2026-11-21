# Step-by-Step Walkthrough

This page takes an extension from an empty directory to a working action in one of your organizations. It uses the Go SDK and the example extension from [Getting Started](building-extensions.md#a-complete-extension). Nothing here depends on a particular cloud provider. Any host that serves HTTPS will do.

The steps:

1. Decide what the extension does
2. Write the code
3. Test it locally
4. Package it
5. Host it
6. Register it
7. Subscribe an organization
8. Call it
9. Debug it when it does not answer
10. Ship changes

## 1. Decide What the Extension Does

Answer these before writing code. Each answer maps onto a part of the extension, and changing some of them later costs more than it looks.

| Question | What it becomes |
| --- | --- |
| What can a user, a D&R rule or another extension ask it to do? | One action per verb in the request schema |
| What does an organization need to set up once? | The config schema, plus a `ValidateConfig` callback |
| Does it create anything inside the organization (rules, lookups, adapters)? | `subscribe`, `unsubscribe` and `update` event handlers |
| Which LimaCharlie API calls does it make? | The permissions in the extension definition |
| Does any single piece of work run longer than about a minute? | Continuations, or a queue and a worker (see [Common Patterns](patterns.md#long-running-work)) |
| Does it charge for usage? | Metric SKUs on responses |

Keep the permission list short. Every subscribed organization grants it, and growing it later needs action from each of those organizations (see [step 10](#10-ship-changes)).

## 2. Write the Code

```bash
mkdir my-extension && cd my-extension
go mod init example.com/my-extension
go get github.com/refractionPOINT/lc-extension@latest
go get github.com/refractionPOINT/go-limacharlie/limacharlie@latest
```

Start from the [complete example](building-extensions.md#a-complete-extension) as `main.go`. Two changes make it deployable:

- Read the shared secret from the environment rather than hard-coding it. The secret is what proves a webhook came from LimaCharlie, so it belongs in your host's secret store, not in the image.
- Pick a name for `ExtensionName`. It must match the name you register in [step 6](#6-register-it).

```go
func main() {
    secret := os.Getenv("LC_SHARED_SECRET")
    if secret == "" {
        panic("LC_SHARED_SECRET is not set")
    }
    ext := buildExtension(secret)
    if err := ext.Init(); err != nil {
        panic(err)
    }
    webserver.RunExtension(ext)
}
```

`webserver.RunExtension` listens on the port in the `PORT` environment variable (80 if it is unset). It answers `POST` on any path.

## 3. Test It Locally

Before anything is deployed, run the extension through a full lifecycle in a unit test. The simulator plays the LimaCharlie side, signing and compressing webhooks exactly as the platform does, and a mock server replaces the LimaCharlie API. No credentials or test organization are needed.

```bash
go test ./...
```

[Testing Extensions](testing.md) has the lifecycle test worth writing first. It catches the two mistakes that otherwise only show up after deployment: an action missing from the advertised schema, and an event handler you forgot to register.

## 4. Package It

Any packaging works. A container is the most portable:

```dockerfile title="Dockerfile"
FROM golang:1 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /extension .

FROM alpine:3
# The extension calls the LimaCharlie API over HTTPS, so it needs CA certificates.
RUN apk add --no-cache ca-certificates
COPY --from=build /extension /extension
ENV PORT=8080
EXPOSE 8080
USER nobody
ENTRYPOINT ["/extension"]
```

!!! note "Python"
    The Python SDK returns a Flask app from `getApp()` and serves only `POST /`. If you run it under gunicorn, raise the worker timeout (for example `--timeout 150`). Gunicorn's default of 30 seconds kills a handler long before the platform's 2-minute limit, and the platform sees a failed call.

## 5. Host It

LimaCharlie calls your extension from the internet. The host has to meet these requirements:

| Requirement | Why |
| --- | --- |
| HTTPS, with a certificate that chains to a public root CA | The platform refuses plain HTTP and self-signed certificates |
| A hostname that resolves to a public IP address | Destinations that resolve to private or internal addresses are refused, and the platform does not retry them |
| A request timeout of at least 2 minutes | That is how long the platform waits for an answer. A host that cuts requests off sooner turns slow calls into failures |
| The shared secret available as an environment variable or mounted secret | So the image carries no credentials |
| More than one instance, or a managed service that restarts it | Requests that arrive while the extension is down fail. Requests from D&R rules are not queued for later (see [Design Considerations](design-considerations.md#availability)) |

Container platforms, serverless functions and a VM behind a load balancer all work. If your platform scales to zero, expect the first request after an idle period to pay the cold-start time out of its 2-minute budget.

While developing, you can point the definition at your own machine through a tunnelling service that gives you a public HTTPS URL. Run the extension locally with `PORT` set to the port the tunnel forwards to. Do not leave a production definition pointed at a tunnel.

A request without an `lc-ext-sig` header gets an empty `200` from the Go SDK, so a plain `GET` against the URL works as a health check.

## 6. Register It

Generate a shared secret and store it in your host's secret store as `LC_SHARED_SECRET`:

```bash
openssl rand -hex 32
```

Then create the definition from [your published add-ons page](https://app.limacharlie.io/add-ons/published). The fields are described in [Getting Started](building-extensions.md#registering-the-extension). For the example extension, the only permission needed is `sensor.list`.

The definition is private to you until you ask for it to be made public. You can subscribe any organization you administer, which is what the next step does.

## 7. Subscribe an Organization

Use an organization you can experiment in, not a production tenant.

```bash
limacharlie extension subscribe --name my-extension --oid <oid>
```

Subscribing does three things, in order:

1. Creates an API key in the organization for your extension, with the permissions in the definition.
2. Fetches your schema.
3. Sends your extension the `subscribe` event and waits for the answer.

If your `subscribe` handler returns an error or takes longer than about a minute, the subscription fails and the user sees an error. Keep that handler short. Work that can wait should go into a continuation (see [Common Patterns](patterns.md#installing-and-maintaining-resources-in-the-organization)).

Check that LimaCharlie sees the schema you expect:

```bash
limacharlie extension schema --name my-extension --oid <oid> --output yaml
```

The extension now also appears in the organization's web app, with a page generated from the schema.

## 8. Call It

From the CLI:

```bash
limacharlie extension request \
  --name my-extension \
  --action list_sensors \
  --data '{"selector": "plat == windows"}' \
  --oid <oid> --output yaml
```

From a D&R rule, for example to run it every day:

```yaml
detect:
  target: schedule
  event: 24h_per_org
  op: exists
  path: /
respond:
  - action: extension request
    extension name: my-extension
    extension action: list_sensors
    extension request:
      selector: '{{ "*" }}'
```

A request from a D&R rule is fire-and-forget. The rule does not wait for your answer and the response is discarded. If the extension needs to produce something people can see or act on, it has to write it somewhere itself: a detection, an event through an [extension adapter](runtime-contract.md#pushing-telemetry-into-an-organization), a case, a ticket.

## 9. Debug It When It Does Not Answer

Look at the organization's errors first. Failed calls, including requests rejected by schema validation before they reached your code, are filed there:

```bash
limacharlie org errors --oid <oid> --output yaml
```

Then work down this list:

1. **Does the schema load?** `limacharlie extension schema --name my-extension`. If it fails, every request and event fails too, because the platform needs the schema to validate them.
2. **Is the organization subscribed?** `limacharlie extension list --oid <oid>`.
3. **Does the action name match** the one in your request schema?
4. **Do the parameters satisfy the schema?** Unknown fields are rejected, not ignored. The [troubleshooting table](runtime-contract.md#troubleshooting) lists the exact messages.
5. **Does the signature check pass?** An `invalid signature` error means the secret in the definition and the one your service runs with differ.
6. **Did the handler time out?** Check your own logs for calls that took close to 2 minutes.

Log the organization ID, action and idempotency key on every call. When a customer reports a problem, those three values are what you search for.

## 10. Ship Changes

**Code changes** deploy like any other service. Keep the old and new versions able to run side by side, because during a rollout both receive traffic.

**Schema changes** take effect within about a minute, which is how long the platform caches your schema. Add fields freely. Removing a config field silently strips the stored value from the config your extension receives, so remove a field only once nothing reads it. See [Design Considerations](design-considerations.md#changing-the-extension-after-launch).

**Permission changes** apply to new subscriptions only. Organizations that are already subscribed keep the key they were given. Each of them has to re-key the subscription to pick up the new permissions:

```bash
limacharlie extension rekey --name my-extension --oid <oid>
```

Plan for that before you ship a feature that needs a new permission: until an organization re-keys, the calls that need it fail with a permission error.

**Rotating the shared secret** without downtime needs a release of your extension that accepts both secrets. In Go, set the new value as `SecretKey` and the old one in `PreviousSecretKeys`, deploy, change the secret in the definition, then remove the old value and deploy again. The Python SDK accepts a single secret. If your extension uses an [extension adapter](runtime-contract.md#pushing-telemetry-into-an-organization), note that each adapter's secret is derived from the shared secret, so rotating it affects those adapters too.

**Making it public** happens through `answers@limacharlie.io`, as described in [Getting Started](building-extensions.md#public-and-private-extensions).

## Next Steps

- [Common Patterns](patterns.md): how existing extensions solve recurring problems
- [Design Considerations & Gotchas](design-considerations.md): what to think about before real customers depend on it
- [Runtime Contract](runtime-contract.md): timeouts, retries, continuations and metrics in detail
