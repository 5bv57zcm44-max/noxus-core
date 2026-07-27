# Workflows and automation

Workflow templates contain a known DocType, explicit states, role-bound transitions, and audit
events. Services validate a transition against its current state before saving; direct API mutation
does not bypass permission checks.

Automation is declarative. The only supported actions are notification, assignment, allow-listed
field change, creation of a known document type, and signed webhook. Python source, dotted function
paths, shell commands, and templates that execute code are rejected. Blueprint application is a
queued, permission-protected operation with a site lock, idempotency key, staged Deployment Record,
resume token, and durable failure summary.
