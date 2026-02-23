# Compositions Documentation

This document describes all composition classes used inside `BaseProduct`. Each composition groups related attributes and contains its own validators.

---

## 1. `Dimensions`

File: `dimensions.py`

**Purpose:** Stores physical dimensions and weight of a product.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `weight_kg` | `Optional[POSITIVE_F]` | Weight in kilograms |
| `width_cm` | `Optional[POSITIVE_F]` | Width in centimeters |
| `height_cm` | `Optional[POSITIVE_F]` | Height in centimeters |
| `depth_cm` | `Optional[POSITIVE_F]` | Depth in centimeters |
| `volume_m3` | `Optional[POSITIVE_F]` | Volume in cubic meters |

**Validators:**

- `calculato_vol` (`@model_validator`): If all three dimensions (`width_cm`, `height_cm`, `depth_cm`) are provided and `volume_m3` is not set, the volume is automatically calculated as `(width*height*depth) / 1_000_000`.

---

## 2. `HandlingAttributes`

File: `handling.py`

**Purpose:** Flags that describe special handling requirements.

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `is_fragile` | `bool` | `False` | Fragile item |
| `is_stackable` | `bool` | `True` | Can be stacked |
| `is_odor_sensitive` | `bool` | `False` | Absorbs odors |
| `requires_ventilation` | `bool` | `False` | Needs ventilation |
| `requires_quarantine` | `bool` | `False` | Requires quarantine after return |
| `is_magnetic` | `bool` | `False` | Magnetic properties |
| `is_static_sensitive` | `bool` | `False` | Sensitive to static electricity |
| `irregular_shape` | `bool` | `False` | Irregular shape |

**Validators:**

- `is_fragile_sctackable` (`@model_validator`): If `is_fragile` is `True`, then `is_stackable` must be `False`.  
  *Raises* `ValueError` if both are `True`.
- `recommendations_validator` (`@model_validator`): If `is_odor_sensitive` is `True` and `requires_ventilation` is `False`, prints a warning (non‑blocking).

---

## 3. `Traceability`

File: `traceability.py`

**Purpose:** Tracks product through its lifecycle.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `tracking_type` | `ProductTrackingType` | How the product is tracked |
| `production_date` | `Optional[date]` | Date of production |
| `expiry_date` | `Optional[date]` | Date of expiry |

**Validators:**

- `check_expiry_not_past` (`@field_validator('expiry_date')`): Raises `ValueError` if `expiry_date` is in the past (and not `None`).
- `check_production_not_future` (`@field_validator('production_date')`): Raises `ValueError` if `production_date` is in the future (and not `None`).
- `check_expiry_tracking` (`@model_validator`): If `tracking_type = EXPIRY_TRACKED`, both `production_date` and `expiry_date` must be provided. Otherwise raises `ValueError`.

---

## 4. `StorageRequirements`

File: `storage_requires.py`

**Purpose:** Defines how the product should be stored.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `storage_condition` | `Optional[ProductStorageCondition]` | General storage requirements |
| `hazard_class` | `Optional[HazardClass]` | Dangerous goods class (if hazardous) |
| `temperature_regime` | `Optional[TemperatureRegime]` | Required temperature regime |
| `packaging_type` | `Optional[PackagingType]` | Type of packaging used |

**Validators:**

- `check_hazard_consistency` (`@model_validator`):  
  - If `storage_condition = HAZARDOUS`, then `hazard_class` must be provided.  
  - If `hazard_class` is provided, `storage_condition` must be `HAZARDOUS`.  
  *Raises* `ValueError` on mismatch.
- `check_temperature_required` (`@model_validator`):  
  If `storage_condition` is `PERISHABLE`, `TEMPERATURE_CONTROLLED` or `MEDICINE`, then `temperature_regime` is required.  
  *Raises* `ValueError` if missing.
- `recommendations_validator` (`@model_validator`):  
  If `storage_condition = ELECTRONICS` and `temperature_regime` is missing, prints a warning (non‑blocking).

---

## 5. `Classification`

File: `classification.py`

**Purpose:** Classifies the product for storage optimization.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `size_type` | `Optional[ProductSizeType]` | Size/weight category |
| `moving_type` | `Optional[ProductMovingType]` | Turnover characteristic |
| `abc_category` | `Optional[ABCCategory]` | ABC classification for inventory optimization |

**Validators:**

- `validate_size_moving` (`@model_validator`):  
  If `size_type` is `HEAVY` or `OVERSIZED`, then `moving_type` cannot be `FAST_MOVING`.  
  *Raises* `ValueError` otherwise.
- `validate_category` (`@model_validator`):  
  If `abc_category = A`, then `moving_type` must be either `FAST_MOVING` or `NORMAL_MOVING`.  
  *Raises* `ValueError` otherwise.