# Deployment verification — 2026-09-11

Deployed `0.11.4-autozero` to `petkit-t4` at `192.168.1.118` using ESPHome OTA.
The final device reports ESPHome 2025.12.5, compiled Sep 11 2026 at 00:17:12.
Firmware SHA-256: `a50ec58e8537ce1cbe4b34fbf4026d3c40b916ca4dc56dcbcc67eb7b262c3c93`.

- ESPHome compilation passed.
- Native automatic-zero tests passed under AddressSanitizer and UndefinedBehaviorSanitizer: stable drift, pet/waste loads, interrupted samples, unstable samples, invalid gain, cumulative bounds, and signed load references.
- Native MCU tests passed under both sanitizers: fragmented and corrupt frames, truncated payloads, invalid lengths/counts, oversized transmit payloads, random traffic, denied motor requests, active interlock stops, and timeout stops.
- Both OTA uploads succeeded. The final reboot retained the commissioned zero offset of 7,264,568 and existing scale factor of approximately -0.00001524658.
- Fresh raw load-cell reports resumed after restoring the previously commented-out reporting configuration.
- With the owner confirming the toilet empty of cats and normal litter loaded, the saved offset was corrected from 7,096,379. Idle weight changed from approximately -2.56 kg to less than 0.001 kg (displayed as 0.00 kg).
- At 00:21:04 the device logged `Automatic zero drift correction applied`, adjusting the saved offset from 7,264,568 to 7,264,487 after the quiet stability window.
- Block Movement was restored to OFF; the final firmware also passed its successful-boot checkpoint.
- Final sensor snapshot: cover/bin fitted, tray closed, drum level, no approach, no pet, no cleaning pending. Auto Clean remained enabled with the existing 60-minute delay.

The new baseline includes the litter present during commissioning. Litter changes
are tracked relative to it; negative changes must remain signed internally so a
refill or litter removal cannot subtract from a subsequent cat measurement.

No forced physical cleaning cycle or known-mass accuracy test was performed.
Absolute kilogram accuracy depends on the preserved gain; automatic zeroing does
not identify gain without a reference mass. Drift correction was exercised in
native tests and subsequently observed on the live device.

# Deployment verification — 2026-10-10 (0.12.0)

The live log before the upgrade (uptime 29.7 days) showed **Pet Weight 0.079–0.084 kg with the
toilet idle**: leftover weight above the 25 g Clean Threshold. Pet Weight arms cleaning whenever
it passes through the band between Clean Threshold and Pet Threshold. That happens on boot,
with paws on the rim, with a hand on the unit and with drum swings. With this leftover, the next
approach release could then clean with no cat. Also logged: `Invalid RTC time`. The external
bm8563 driver swaps the day and weekday registers, so a written date reads back as day 00.

Changes: visit-confirmed auto cleaning against a pre-visit weight baseline; `waste_pending`
persisted and captured once per cycle; drum-up during Maintenance no longer wipes collected
waste; litter re-measured after leveling; autozero bound anchored to a persisted commissioning
zero; MCU stop frames resent, state reset on MCU reset, CRC errors no longer drop following
frames; RTC switched to the core `pcf8563` driver plus SNTP fallback; new visit/status sensors.

- Native autozero and MCU suites pass under ASan/UBSan, including new reboot-anchor,
  stop-retry, deinit and CRC-resync regressions.
- `esphome compile` passed; OTA to 192.168.1.118 succeeded; device reports 0.12.0, Status `Ready`,
  no warnings or errors after boot.
- No forced cleaning cycle or real cat visit was exercised during deployment.
