-- Petkit T4: remove implausible long-term statistics from the Home Assistant recorder.
-- Run in the "SQLite Web" add-on (or `sqlite3 /config/home-assistant_v2.db` via SSH).
-- Make a backup first (Settings → System → Backups). These deletes cannot be undone.
-- Cutoff 1791638220 = 2026-10-10 13:17 UTC, when firmware 0.12.0 went live.

-- Pet Body Mass: the old algorithm reported partial step-ins (0.05–1 kg), people
-- leaning on the unit (>10 kg) and a 1.5–2 kg sag caused by a stale litter
-- baseline. The cat measures ~3.3–3.6 kg whenever the baseline was valid.
DELETE FROM statistics WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_pet_body_mass')
  AND start_ts < 1791638220 AND (mean < 2.5 OR mean > 6);
DELETE FROM statistics_short_term WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_pet_body_mass')
  AND start_ts < 1791638220 AND (mean < 2.5 OR mean > 6);

-- Pet Weight: negative values (old firmware did not clamp) and loads > 15 kg.
DELETE FROM statistics WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_pet_weight')
  AND (min < -0.05 OR max > 15);
DELETE FROM statistics_short_term WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_pet_weight')
  AND (min < -0.05 OR max > 15);

-- Weight: -4 kg for weeks before the 2026-09-11 empty-toilet recalibration, and
-- the ±30 kg calibration chaos on 2025-12-04.
DELETE FROM statistics WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_weight')
  AND (min < -3 OR max > 15);
DELETE FROM statistics_short_term WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_weight')
  AND (min < -3 OR max > 15);

-- Distance: the calibration curve extrapolated to -3673 cm (fixed in firmware).
DELETE FROM statistics WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_distance')
  AND min < 0;
DELETE FROM statistics_short_term WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_distance')
  AND min < 0;

-- Waste Collected: 33 kg on 2025-12-04 (same calibration incident).
DELETE FROM statistics WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_waste_collected')
  AND max > 2000;
DELETE FROM statistics_short_term WHERE metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_waste_collected')
  AND max > 2000;
