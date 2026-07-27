# Security scanner dispositions

There are no accepted dependency-vulnerability exceptions for the 1.0 release candidate. React
Router was moved from 7.18.1 to the patched 8.3.0 package on 2026-07-27 in response to
`GHSA-qwww-vcr4-c8h2`; NOXUS does not use the affected unstable RSC APIs, but production artifacts
must still pass the complete audit without relying on that reachability argument.
