# Petkit T4 ESPHome Firmware

https://github.com/user-attachments/assets/c50be11d-95dd-4898-9601-6adc21f130d6/#Firmware.Dreams.mp4


**Custom.** Fully replaces the stock firmware while introducing some extra neat features, as well as native Home Assistant integration.

It's able to work completely offline & without HA, with automatic correction of small weight-sensor zero drift.


## Extra features added

- Top (menu) button: Clean / Reboot
- Bottom (ok) button: Maintenance mode / Maintenance done & Level the litter
- Advanced status displaying
- Quieter functioning
- Collected waste amount tracking
- Beep after reaching set amount of litter in maintenance mode
- QR code with a Wi-Fi AP connection shortcut
- Optional [Improv-BLE](https://improv-wifi.com) support
- Various internal sensors exposed to HA
- Additional safety checks compared to the stock fw
- Manual motor controls
- Visit-based auto cleaning: only a confirmed cat visit can arm a clean
- Per-visit Pet Body Mass, Last Visit Duration, Last Visit Waste, Visits Today/Total
- Status text sensor (Ready, Cat inside, Clean pending, Cleaning, …)


## Yet to implement

* [x] Auto cleaning start (a.k.a. non-kitten mode)
* [x] Pet weight saving (per visit)
* [ ] Multiple pets support
* [ ] Extra unknown packets
* [ ] Better & more failsafe motor control
* [ ] Parametrized MCU init
* [x] Automatic zero-drift correction (existing scale retained)
* [ ] Dumping the stock calibration data from factory binaries (per-chip)
* [x] Weight as additional safety check
* [ ] Tune the timeouts and speeds


## Auto cleaning

A clean is armed only by a **confirmed visit**: Pet Inside (load ≥ Pet Threshold
above the settled idle weight) for at least **Min Visit Duration** (default 10 s)
with at least three steady readings. Paws on the rim, a hand on the unit, drum
swings, power-ups and slow weight drift no longer arm cleaning. After **Clean
After** minutes (waiting up to 30 more minutes if someone is nearby), the box
cleans only if the weight gained since just before the visit is at least
**Clean Threshold**. Otherwise the clean is skipped and logged. **Clean Times**
adds unconditional repeats after that first clean. Emptying the bin while a
clean is pending keeps it pending. Maintenance, **All Litter Removed** or
turning Auto Clean off cancels it.

## Automatic weight zeroing

There is no repeated zero-button / known-weight calibration routine. The firmware
preserves the existing scale and zero settings and automatically corrects small
zero drift after two minutes of stable readings with the drum level, tray closed,
cover/bin fitted, no approach, no pet, and both motors stopped. It waits at least
one minute after boot and restarts the stability window on missing samples or
activity. Litter and collected waste remain part of the expected load.

To avoid learning a pet or waste as empty, correction is limited to -20 g to
+4 g relative to the persisted commissioning baseline (set by Confirm Toilet
Empty, kept across reboots) (the positive limit is also capped
at one fifth of the cleaning threshold). Large offsets are deliberately not
zeroed automatically. Keep all four feet on a firm, level surface.

If the saved baseline is wrong or the unit is relocated, the disabled-by-default
**Confirm Toilet Empty** button establishes a new baseline with normal litter
loaded. Only use it after confirming no cat is inside. No reference weights or
repeated adjustments are needed. Routine drift correction is automatic afterward.
This unit was commissioned that way with the owner's empty-toilet confirmation.
Litter load is therefore reported relative to that starting load, not as an
absolute amount of litter. Internal accounting retains negative load changes
when litter is removed so pet detection still measures the full added cat weight.
The maintenance litter target also uses that relative baseline.

Automatic zeroing cannot determine load-cell gain. Existing calibrated kilogram
measurements are retained; on an uncalibrated device the default gain is only an
estimate. The disabled-by-default **Reference Weight (Optional)** diagnostic can
refine gain using a known added weight. It is not needed for routine drift
correction. No claim of absolute 0.01 kg accuracy is made without a reference.

## Build and verification

Use ESPHome 2025.12.5 (`esphome compile petkit.yaml`). The Arduino framework and
external RTC revision are pinned for compatibility. Upload with
`esphome upload petkit.yaml --device petkit-t4.local`.

Run the native drift regression suite with:

```sh
c++ -std=c++17 -Wall -Wextra -Werror -fsanitize=address,undefined tests/test_autozero.cpp -o /tmp/petkit-test-autozero
/tmp/petkit-test-autozero
c++ -std=gnu++17 -Wno-c99-extensions -fsanitize=address,undefined -fno-sanitize-recover=all -Itests/stubs tests/test_mcu.cpp -o /tmp/petkit-test-mcu
/tmp/petkit-test-mcu
```

All motor requests use a shared safety interlock; missing/stale weight data,
approach, cover removal, OTA, and Block Movement prevent motion. UART frames are
length-checked before decoding and partial frames are collected without blocking.

## Thanks to:

- @earlynerd with his [repo](https://github.com/earlynerd/petkit-pura-max-serial-bus) for the pioneering and _enormous_ help in the reverse engineering.
- @dwyschka for the idea and the upstart (earlynerd/petkit-pura-max-serial-bus#1).
- My loved girlfriend Sharea & my lovely kitty Xayah for the lots of testing.


---

https://github.com/user-attachments/assets/ad489f28-23f9-497a-a08b-c182428b3873/#Petkit.T4.ESPHome.Firmware.mp4
