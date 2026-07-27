# Tutorial: VPS deployment

Use a supported Linux amd64/arm64 host, install Docker/Compose, configure DNS and TLS at a trusted
front proxy, transfer the generated project, populate root/admin secrets with mode 600, and start the
production profile. Restrict ports to 80/443, schedule encrypted off-host backups, monitor health,
and rehearse restore before serving production traffic.
