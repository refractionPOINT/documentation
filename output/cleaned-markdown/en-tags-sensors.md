# Stdin

The Stdin adapter allows you to pipe data into the LimaCharlie sensor adapter from standard input.

## Basic Usage

```bash
cat data.log | limacharlie-adapter --type stdin
```

## Configuration

The stdin adapter accepts data line-by-line and forwards it to LimaCharlie for ingestion.

### Parameters

- `--type stdin`: Specifies the stdin adapter type
- Standard adapter parameters apply (API key, organization ID, etc.)

## Use Cases

- Quick testing and prototyping
- Integration with shell scripts
- Processing output from other commands
- One-time data imports

## Example

```bash
echo '{"event": "test"}' | limacharlie-adapter \
  --type stdin \
  --client-options '{"identity": {"oid": "your-org-id", "installation_key": "your-key"}}'
```

## Notes

- Input is processed line-by-line
- Each line should contain a complete event
- The adapter will continue reading until EOF is reached
- Suitable for streaming data sources