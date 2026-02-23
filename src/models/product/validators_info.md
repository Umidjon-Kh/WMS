# Validators Documentation

This document lists all validators in the `BaseProduct` model and its compositions. Validators ensure data consistency and enforce business rules.

## 1. Composition Validators

### 1.1. `Dimensions.calculato_vol`
- **Type:** `@model_validator`
- **Purpose:** Automatically calculates `volume_m3` from `width_cm`, `height_cm`, `depth_cm` if all three are provided and `volume_m3` is not set.

### 1.2. `HandlingAttributes.is_fragile_sctackable`
- **Type:** `@model_validator`
- **Purpose:** Ensures that if a product is fragile (`is_fragile = True`), it cannot be stackable (`is_stackable = False`). Raises `ValueError` if both are `True`.

### 1.3. `HandlingAttributes.recommendations_validator`
- **Type:** `@model_validator`
- **Purpose:** Prints a warning (non‑blocking) if an odor‑sensitive product (`is_odor_sensitive = True`) does not have ventilation required (`requires_ventilation = False`).

### 1.4. `Traceability.check_expiry_not_past`
- **Type:** `@field_validator('expiry_date')`
- **Purpose:** Raises `ValueError` if `expiry_date` is in the past (and not `None`).

### 1.5. `Traceability.check_production_not_future`
- **Type:** `@field_validator('production_date')`
- **Purpose:** Raises `ValueError` if `production_date` is in the future (and not `None`).

### 1.6. `Traceability.check_expiry_tracking`
- **Type:** `@model_validator`
- **Purpose:** When `tracking_type = EXPIRY_TRACKED`, requires both `production_date` and `expiry_date`. Raises `ValueError` if any is missing.

### 1.7. `StorageRequirements.check_hazard_consistency`
- **Type:** `@model_validator`
- **Purpose:**  
  - If `storage_condition = HAZARDOUS`, `hazard_class` must be provided.  
  - If `hazard_class` is provided, `storage_condition` must be `HAZARDOUS`.  
  Raises `ValueError` on mismatch.

### 1.8. `StorageRequirements.check_temperature_required`
- **Type:** `@model_validator`
- **Purpose:** If `storage_condition` is `PERISHABLE`, `TEMPERATURE_CONTROLLED` or `MEDICINE`, then `temperature_regime` is required. Raises `ValueError` if missing.

### 1.9. `StorageRequirements.recommendations_validator`
- **Type:** `@model_validator`
- **Purpose:** Prints a warning (non‑blocking) if `storage_condition = ELECTRONICS` and `temperature_regime` is missing.

### 1.10. `Classification.validate_size_moving`
- **Type:** `@model_validator`
- **Purpose:** If `size_type` is `HEAVY` or `OVERSIZED`, then `moving_type` cannot be `FAST_MOVING`. Raises `ValueError` otherwise.

### 1.11. `Classification.validate_category`
- **Type:** `@model_validator`
- **Purpose:** For `abc_category = A`, requires `moving_type` to be either `FAST_MOVING` or `NORMAL_MOVING`. Raises `ValueError` otherwise.

---

## 2. Cross‑Validators in `BaseProduct`

All cross‑validators are `@model_validator(mode='after')` methods.

### 2.1. `validate_stgc_requirements`
- **Purpose:**  
  - If `storage_requirements.storage_condition` is `PERISHABLE` or `MEDICINE`, then `traceability.tracking_type` must be `EXPIRY_TRACKED`.  
  - If `storage_requirements.storage_condition` is `ELECTRONICS`, then `handling.is_static_sensitive` must be `True`.  
  Raises `ValueError` on violation.

### 2.2. `validate_timestamps`
- **Purpose:** Ensures that `updated_at` is not earlier than `created_at`. Raises `ValueError` if `updated_at < created_at`.

### 2.3. `validate_handlings`
- **Purpose:** If `handling.is_stackable` is `True` and `classification.size_type` is `HEAVY` or `OVERSIZED`, raises `ValueError` because heavy/oversized products cannot be stackable.

### 2.4. `validate_role`
- **Purpose:** If `role_type = RETURNS`, then `handling.requires_quarantine` must be `True`. Raises `ValueError` otherwise.

### 2.5. `validate_physical_state_units`
- **Purpose:** Validates compatibility of `unit_of_measure` and `packaging_type` with the product's `physical_state`:
  - **LIQUID:** `unit_of_measure` must be `LITER` or `MILLILITER`; `packaging_type` cannot be `BOX`.
  - **GAS:** `unit_of_measure` must be `LITER`, `MILLILITER`, or `CUBIC_METER`; `packaging_type` must be `CYLINDER` or `DRUM` (or `None`); `handling.requires_ventilation` must be `True`.
  - **BULK:** `unit_of_measure` must be `KILOGRAM`, `GRAM`, or `CUBIC_METER`.
  - **SOLID:** no restrictions.
  Raises `ValueError` on any mismatch.

### 2.6. `validate_tracking_type_units`
- **Purpose:** Validates that `unit_of_measure` is appropriate for the given `traceability.tracking_type`:
  - **WEIGHT_BASED:** allowed units: `KILOGRAM`, `GRAM`, `LITER`, `MILLILITER`, `CUBIC_METER`.
  - **PIECE:** allowed units: `PIECE`, `BOX`, `PALLET`, `SET`.
  - **KIT:** allowed units: `SET`, `PIECE`.
  Raises `ValueError` if `unit_of_measure` is not in the allowed set.

### 2.7. `validate_tracking_type_physical_state_compatibility`
- **Purpose:** Ensures that certain tracking types are not used with incompatible physical states:
  - For `physical_state` in `(LIQUID, GAS, BULK)`, `tracking_type` cannot be `PIECE` or `KIT`.
  Raises `ValueError` if violated.

### 2.8. `validate_size_type_heavy`
- **Purpose:** If `classification.size_type = HEAVY`:
  - `dimensions.weight_kg` must be provided.
  - `dimensions.weight_kg` must be ≥ `HEAVY_MIN_KG`.
  Raises `ValueError` otherwise.

### 2.9. `validate_size_type_oversized`
- **Purpose:** If `classification.size_type = OVERSIZED`:
  - At least one of `dimensions.width_cm`, `height_cm`, `depth_cm` must be provided.
  - At least one of those must be > `OVERSIZED_MIN_CM`.
  Raises `ValueError` otherwise.

### 2.10. `validate_size_type_light`
- **Purpose:** If `classification.size_type = LIGHT`:
  - `dimensions.weight_kg` must be provided.
  - `dimensions.weight_kg` must be ≤ `LIGHT_MAX_KG`.
  Raises `ValueError` otherwise.

### 2.11. `validate_size_type_small_parts`
- **Purpose:** If `classification.size_type = SMALL_PARTS`:
  - At least one of `dimensions.width_cm`, `height_cm`, `depth_cm` must be provided.
  - At least one of those must be < `SMALL_PARTS_MAX_CM`.
  Raises `ValueError` otherwise.