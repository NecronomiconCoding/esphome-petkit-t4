-- Petkit T4: remove implausible long-term statistics from the Home Assistant recorder.
-- SQLite Web runs one statement per Execute: run statement 1, then statement 2.
-- Back up first (Settings → System → Backups). These deletes cannot be undone.
-- Cutoff 1791638220 = 2026-10-10 13:17 UTC, when firmware 0.12.0 went live.
--   Pet Body Mass  <2.5 or >6 kg before 0.12.0 (step-ins, people, stale-baseline sag; cat ~3.3–3.6 kg)
--   Pet Weight     <0 kg (unclamped old firmware) or >15 kg
--   Weight         <-3 kg (pre-recalibration zero) or >15 kg
--   Distance       <0 cm (curve extrapolation, fixed in firmware)
--   Waste Collected >2 kg (2025-12-04 calibration incident)

-- 1) hourly statistics
DELETE FROM statistics WHERE
     (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_pet_body_mass') AND start_ts < 1791638220 AND (mean < 2.5 OR mean > 6))
  OR (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_pet_weight') AND (min < -0.05 OR max > 15))
  OR (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_weight') AND (min < -3 OR max > 15))
  OR (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_distance') AND min < 0)
  OR (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_waste_collected') AND max > 2000);

-- 2) 5-minute statistics
DELETE FROM statistics_short_term WHERE
     (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_pet_body_mass') AND start_ts < 1791638220 AND (mean < 2.5 OR mean > 6))
  OR (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_pet_weight') AND (min < -0.05 OR max > 15))
  OR (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_weight') AND (min < -3 OR max > 15))
  OR (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_distance') AND min < 0)
  OR (metadata_id = (SELECT id FROM statistics_meta WHERE statistic_id = 'sensor.petkit_t4_waste_collected') AND max > 2000);
