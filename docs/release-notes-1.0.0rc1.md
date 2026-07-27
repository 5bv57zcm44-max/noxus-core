# NOXUS CORE 1.0.0rc1

This local release candidate contains the cross-platform CLI, strict module/blueprint/release schemas,
selective Django generator, checksummed Frappe runtime payload, nine Frappe apps, pinned Compose
topology, and compiled bilingual Solution Builder. It has not been published.

Known release-candidate limits: full Frappe/ERPNext Docker acceptance and two-site isolation require
a Linux runner with sufficient disk/time and are CI integration gates; the current local host has not
completed those costly gates. React Router is upgraded to the patched 8.3.0 release and the frontend
dependency audit has no accepted security exceptions. Remote marketplace and cloud provisioning are
intentionally unavailable.
