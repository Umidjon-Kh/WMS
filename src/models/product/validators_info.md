# Документация валидаторов

В этом документе перечислены все валидаторы в модели `BaseProduct` и её композициях. Валидаторы обеспечивают согласованность данных и соблюдение бизнес-правил.

## 1. Валидаторы композиций

### 1.1. `Dimensions.calculato_vol`
- **Тип:** `@model_validator`
- **Назначение:** Автоматически вычисляет `volume_m3` из `width_cm`, `height_cm`, `depth_cm`, если все три заданы, а `volume_m3` не указан.

### 1.2. `HandlingAttributes.is_fragile_sctackable`
- **Тип:** `@model_validator`
- **Назначение:** Гарантирует, что хрупкий товар (`is_fragile = True`) не может быть штабелируемым (`is_stackable = False`).

### 1.3. `HandlingAttributes.recommendations_validator`
- **Тип:** `@model_validator`
- **Назначение:** Выводит предупреждение, если товар, чувствительный к запахам, не требует вентиляции (неблокирующее).

### 1.4. `Traceability.check_expiry_not_past`
- **Тип:** `@field_validator('expiry_date')`
- **Назначение:** Вызывает `ValueError`, если `expiry_date` в прошлом.

### 1.5. `Traceability.check_dates_consistency`
- **Тип:** `@model_validator`
- **Назначение:** Вызывает `ValueError`, если указаны обе даты, но `expiry_date` ≤ `production_date`.

### 1.6. `Traceability.check_expiry_tracking`
- **Тип:** `@model_validator`
- **Назначение:** При `tracking_type = EXPIRY_TRACKED` требует наличия `production_date` и `expiry_date`.

### 1.7. `StorageRequirements.check_hazard_consistency`
- **Тип:** `@model_validator`
- **Назначение:** Обеспечивает, что `hazard_class` указан тогда и только тогда, когда `storage_condition = HAZARDOUS`.

### 1.8. `StorageRequirements.check_temperature_required`
- **Тип:** `@model_validator`
- **Назначение:** Требует `temperature_regime`, когда `storage_condition` равно `PERISHABLE`, `TEMPERATURE_CONTROLLED` или `MEDICINE`.

### 1.9. `StorageRequirements.recommendations_validator`
- **Тип:** `@model_validator`
- **Назначение:** Выводит предупреждение, если `storage_condition = ELECTRONICS`, а `temperature_regime` не указан.

### 1.10. `Classification.validate_size_moving`
- **Тип:** `@model_validator`
- **Назначение:** Запрещает `FAST_MOVING` для товаров с размером `HEAVY` или `OVERSIZED`.

### 1.11. `Classification.validate_category`
- **Тип:** `@model_validator`
- **Назначение:** Для `abc_category = A` требует, чтобы `moving_type` был `FAST_MOVING` или `NORMAL_MOVING`.

---

## 2. Кросс‑валидаторы в `BaseProduct`

Все кросс‑валидаторы — методы с декоратором `@model_validator(mode='after')`.

### 2.1. `validate_stgc_requirements`
- **Назначение:**
  - Если `storage_condition` равно `PERISHABLE` или `MEDICINE`, то `tracking_type` должен быть `EXPIRY_TRACKED`.
  - Если `storage_condition = ELECTRONICS`, то `is_static_sensitive` должно быть `True`.

### 2.2. `check_timestamps`
- **Назначение:** Проверяет, что `updated_at` не раньше `created_at`.

### 2.3. `validate_units`
- **Назначение:** Проверяет совместимость `unit_of_measure`, `tracking_type`, `physical_state` и `packaging_type`:
  - Весовой учёт → единица в `{кг, г}`.
  - Поштучный учёт → единица в `{шт, кор, пал, компл}`.
  - Комплекты → единица в `{компл, шт}`.
  - Жидкости → единица в `{л, мл}`, упаковка не `коробка`.
  - Газы → единица в `{л, мл, м³}`, упаковка `баллон` или `бочка`, `requires_ventilation = True`.
  - Насыпные → единица веса или `м³`.

### 2.4. `validate_size_type`
- **Назначение:** Проверяет требования к габаритам в зависимости от `size_type`:
  - `HEAVY` → `weight_kg` указан и ≥ `HEAVY_MIN_KG`.
  - `OVERSIZED` → хотя бы один габарит > `OVERSIZED_MIN_CM`.
  - `LIGHT` → `weight_kg` указан и ≤ `LIGHT_MAX_KG`.
  - `SMALL_PARTS` → хотя бы один габарит < `SMALL_PARTS_MAX_CM`.

### 2.5. `validate_handlings`
- **Назначение:** Если `size_type` равен `HEAVY` или `OVERSIZED`, то `is_stackable` должно быть `False`.

### 2.6. `validate_role`
- **Назначение:** Если `role_type = RETURNS`, то `requires_quarantine` должно быть `True`.