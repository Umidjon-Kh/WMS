# Документация валидаторов

В этом документе перечислены все валидаторы в модели `BaseProduct` и её композициях. Валидаторы обеспечивают согласованность данных и соблюдение бизнес-правил.

## 1. Валидаторы композиций

### 1.1. `Dimensions.calculato_vol`
- **Тип:** `@model_validator`
- **Назначение:** Автоматически вычисляет `volume_m3` из `width_cm`, `height_cm`, `depth_cm`, если все три заданы, а `volume_m3` не указан.

### 1.2. `HandlingAttributes.is_fragile_sctackable`
- **Тип:** `@model_validator`
- **Назначение:** Гарантирует, что хрупкий товар (`is_fragile = True`) не может быть штабелируемым (`is_stackable = False`). Выбрасывает `ValueError`, если оба `True`.

### 1.3. `HandlingAttributes.recommendations_validator`
- **Тип:** `@model_validator`
- **Назначение:** Выводит предупреждение (неблокирующее), если товар, чувствительный к запахам (`is_odor_sensitive = True`), не требует вентиляции (`requires_ventilation = False`).

### 1.4. `Traceability.check_expiry_not_past`
- **Тип:** `@field_validator('expiry_date')`
- **Назначение:** Выбрасывает `ValueError`, если `expiry_date` в прошлом (и не `None`).

### 1.5. `Traceability.check_production_not_future`
- **Тип:** `@field_validator('production_date')`
- **Назначение:** Выбрасывает `ValueError`, если `production_date` в будущем (и не `None`).

### 1.6. `Traceability.check_expiry_tracking`
- **Тип:** `@model_validator`
- **Назначение:** Если `tracking_type = EXPIRY_TRACKED`, то обязательны `production_date` и `expiry_date`. Иначе `ValueError`.

### 1.7. `StorageRequirements.check_hazard_consistency`
- **Тип:** `@model_validator`
- **Назначение:**  
  - Если `storage_condition = HAZARDOUS`, то `hazard_class` обязателен.  
  - Если указан `hazard_class`, то `storage_condition` должно быть `HAZARDOUS`.  
  Выбрасывает `ValueError` при несоответствии.

### 1.8. `StorageRequirements.check_temperature_required`
- **Тип:** `@model_validator`
- **Назначение:** Если `storage_condition` равно `PERISHABLE`, `TEMPERATURE_CONTROLLED` или `MEDICINE`, то `temperature_regime` обязателен. Выбрасывает `ValueError` при отсутствии.

### 1.9. `StorageRequirements.recommendations_validator`
- **Тип:** `@model_validator`
- **Назначение:** Выводит предупреждение (неблокирующее), если `storage_condition = ELECTRONICS`, а `temperature_regime` не указан.

### 1.10. `Classification.validate_size_moving`
- **Тип:** `@model_validator`
- **Назначение:** Если `size_type` равен `HEAVY` или `OVERSIZED`, то `moving_type` не может быть `FAST_MOVING`. Выбрасывает `ValueError` в противном случае.

### 1.11. `Classification.validate_category`
- **Тип:** `@model_validator`
- **Назначение:** Если `abc_category = A`, то `moving_type` должен быть `FAST_MOVING` или `NORMAL_MOVING`. Выбрасывает `ValueError` иначе.

---

## 2. Кросс‑валидаторы в `BaseProduct`

Все кросс‑валидаторы — методы с декоратором `@model_validator(mode='after')`.

### 2.1. `validate_stgc_requirements`
- **Назначение:**  
  - Если `storage_requirements.storage_condition` равно `PERISHABLE` или `MEDICINE`, то `traceability.tracking_type` должен быть `EXPIRY_TRACKED`.  
  - Если `storage_requirements.storage_condition = ELECTRONICS`, то `handling.is_static_sensitive` должно быть `True`.  
  Выбрасывает `ValueError` при нарушении.

### 2.2. `validate_timestamps`
- **Назначение:** Проверяет, что `updated_at` не раньше `created_at`. Выбрасывает `ValueError`, если `updated_at < created_at`.

### 2.3. `validate_handlings`
- **Назначение:** Если `handling.is_stackable = True` и `classification.size_type` равен `HEAVY` или `OVERSIZED`, выбрасывает `ValueError` (тяжёлые/негабаритные товары нельзя штабелировать).

### 2.4. `validate_role`
- **Назначение:** Если `role_type = RETURNS`, то `handling.requires_quarantine` должно быть `True`. Иначе `ValueError`.

### 2.5. `validate_physical_state_units`
- **Назначение:** Проверяет совместимость `unit_of_measure` и `packaging_type` с физическим состоянием товара:
  - **LIQUID:** `unit_of_measure` должен быть `LITER` или `MILLILITER`; `packaging_type` не может быть `BOX`.
  - **GAS:** `unit_of_measure` должен быть `LITER`, `MILLILITER` или `CUBIC_METER`; `packaging_type` должен быть `CYLINDER` или `DRUM` (или `None`); `handling.requires_ventilation` должно быть `True`.
  - **BULK:** `unit_of_measure` должен быть `KILOGRAM`, `GRAM` или `CUBIC_METER`.
  - **SOLID:** без ограничений.  
  Выбрасывает `ValueError` при любом несоответствии.

### 2.6. `validate_tracking_type_units`
- **Назначение:** Проверяет, что `unit_of_measure` подходит для данного `traceability.tracking_type`:
  - **WEIGHT_BASED:** допустимые единицы: `KILOGRAM`, `GRAM`, `LITER`, `MILLILITER`, `CUBIC_METER`.
  - **PIECE:** допустимые единицы: `PIECE`, `BOX`, `PALLET`, `SET`.
  - **KIT:** допустимые единицы: `SET`, `PIECE`.  
  Выбрасывает `ValueError`, если единица не входит в разрешённый набор.

### 2.7. `validate_tracking_type_physical_state_compatibility`
- **Назначение:** Гарантирует, что некоторые типы отслеживания не используются с несовместимыми физическими состояниями:
  - Для `physical_state` из `(LIQUID, GAS, BULK)` тип отслеживания не может быть `PIECE` или `KIT`.  
  Выбрасывает `ValueError` при нарушении.

### 2.8. `validate_size_type_heavy`
- **Назначение:** Если `classification.size_type = HEAVY`:
  - `dimensions.weight_kg` обязателен.
  - `dimensions.weight_kg` должен быть ≥ `HEAVY_MIN_KG`.  
  Иначе `ValueError`.

### 2.9. `validate_size_type_oversized`
- **Назначение:** Если `classification.size_type = OVERSIZED`:
  - Хотя бы один из `dimensions.width_cm`, `height_cm`, `depth_cm` должен быть указан.
  - Хотя бы один из указанных габаритов должен быть > `OVERSIZED_MIN_CM`.  
  Иначе `ValueError`.

### 2.10. `validate_size_type_light`
- **Назначение:** Если `classification.size_type = LIGHT`:
  - `dimensions.weight_kg` обязателен.
  - `dimensions.weight_kg` должен быть ≤ `LIGHT_MAX_KG`.  
  Иначе `ValueError`.

### 2.11. `validate_size_type_small_parts`
- **Назначение:** Если `classification.size_type = SMALL_PARTS`:
  - Хотя бы один из `dimensions.width_cm`, `height_cm`, `depth_cm` должен быть указан.
  - Хотя бы один из указанных габаритов должен быть < `SMALL_PARTS_MAX_CM`.  
  Иначе `ValueError`.