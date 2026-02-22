# Validators Documentation

This document lists all validators in the `BaseProduct` model and its compositions. Validators ensure data consistency and enforce business rules.

## 1. Composition Validators

### 1.1. `Dimensions.calculato_vol`
- **Type:** `@model_validator`
- **Purpose:** Automatically calculates `volume_m3` from `width_cm`, `height_cm`, `depth_cm` if all three are provided and `volume_m3` is not set.

### 1.2. `HandlingAttributes.is_fragile_sctackable`
- **Type:** `@model_validator`
- **Purpose:** Ensures that if a product is fragile (`is_fragile = True`), it cannot be stackable (`is_stackable = False`).

### 1.3. `HandlingAttributes.recommendations_validator`
- **Type:** `@model_validator`
- **Purpose:** Prints a warning if an odor‑sensitive product does not have ventilation required (non‑blocking).

### 1.4. `Traceability.check_expiry_not_past`
- **Type:** `@field_validator('expiry_date')`
- **Purpose:** Raises `ValueError` if `expiry_date` is in the past.

### 1.5. `Traceability.check_dates_consistency`
- **Type:** `@model_validator`
- **Purpose:** Raises `ValueError` if both `production_date` and `expiry_date` are provided but `expiry_date` ≤ `production_date`.

### 1.6. `Traceability.check_expiry_tracking`
- **Type:** `@model_validator`
- **Purpose:** When `tracking_type = EXPIRY_TRACKED`, requires both `production_date` and `expiry_date`.

### 1.7. `StorageRequirements.check_hazard_consistency`
- **Type:** `@model_validator`
- **Purpose:** Ensures `hazard_class` is provided if and only if `storage_condition = HAZARDOUS`.

### 1.8. `StorageRequirements.check_temperature_required`
- **Type:** `@model_validator`
- **Purpose:** Requires `temperature_regime` when `storage_condition` is `PERISHABLE`, `TEMPERATURE_CONTROLLED` or `MEDICINE`.

### 1.9. `StorageRequirements.recommendations_validator`
- **Type:** `@model_validator`
- **Purpose:** Prints a warning if `storage_condition = ELECTRONICS` and `temperature_regime` is missing.

### 1.10. `Classification.validate_size_moving`
- **Type:** `@model_validator`
- **Purpose:** Prevents `FAST_MOVING` for `HEAVY` or `OVERSIZED` products.

### 1.11. `Classification.validate_category`
- **Type:** `@model_validator`
- **Purpose:** For `abc_category = A`, requires `moving_type` to be `FAST_MOVING` or `NORMAL_MOVING`.

---

## 2. Cross‑Validators in `BaseProduct`

All cross‑validators are `@model_validator(mode='after')` methods.

### 2.1. `validate_stgc_requirements`
- **Purpose:**
  - If `storage_condition` is `PERISHABLE` or `MEDICINE`, `tracking_type` must be `EXPIRY_TRACKED`.
  - If `storage_condition` is `ELECTRONICS`, `is_static_sensitive` must be `True`.

### 2.2. `check_timestamps`
- **Purpose:** Ensures `updated_at` is not earlier than `created_at`.

### 2.3. `validate_units`
- **Purpose:** Validates compatibility between `unit_of_measure`, `tracking_type`, `physical_state`, and `packaging_type`:
  - Weight‑based tracking → unit in `{kg, g}`.
  - Piece tracking → unit in `{pc, box, pallet, set}`.
  - Kit tracking → unit in `{set, pc}`.
  - Liquids → unit in `{l, ml}` and packaging not `box`.
  - Gases → unit in `{l, ml, m³}`, packaging must be `cylinder` or `drum`, and `requires_ventilation = True`.
  - Bulk → unit in weight or `m³`.

### 2.4. `validate_size_type`
- **Purpose:** Checks dimensional requirements based on `size_type`:
  - `HEAVY` → `weight_kg` provided and ≥ `HEAVY_MIN_KG`.
  - `OVERSIZED` → at least one dimension > `OVERSIZED_MIN_CM`.
  - `LIGHT` → `weight_kg` provided and ≤ `LIGHT_MAX_KG`.
  - `SMALL_PARTS` → at least one dimension < `SMALL_PARTS_MAX_CM`.

### 2.5. `validate_handlings`
- **Purpose:** If `size_type` is `HEAVY` or `OVERSIZED`, then `is_stackable` must be `False`.

### 2.6. `validate_role`
- **Purpose:** If `role_type = RETURNS`, then `requires_quarantine` must be `True`.