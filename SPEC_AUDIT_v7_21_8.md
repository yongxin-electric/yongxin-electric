# SPEC AUDIT v7.21.8 — Fuji Electric contactors / starters / relays

- Baseline: v7.21.7 Full ZIP
- Added products: 21
- Product total: 247
- Technical articles: 10

## Key verified rules
1. Fuji official generation history lists SC-1N and SC-N1 separately; SW-1N and SW-N1 separately. Model token order is significant.
2. Fuji standard SC-N1 to SC-N5A do not use SUPER MAGNET. SC-N6 and above use IC-controlled SUPER MAGNET with AC-input / DC-operated concept and AC/DC input capability.
3. SC-N7 pages use actual nameplate voltage ranges from the supplied product photos.
4. SH-4 is treated as an industrial relay; SZ-A22 is 2NO+2NC according to Fuji official data.
5. Old SRC / SRCa / FMC / SRC50 products are not assigned modern coil architecture or direct replacement unless exact official evidence exists.
6. Suspected external/web images for SC-0, SC-N1, standalone SC-N2 AC110/220, SRC50-2F are excluded from public product photography; custom placeholders are used.

## Public technical article
`article-contactor-coil-architecture-abb-siemens-fuji.html` compares verified control/coil concepts without asserting cross-brand interchangeability.
