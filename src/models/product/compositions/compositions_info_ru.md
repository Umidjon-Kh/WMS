# Документация композиций

## 1. Dimensions

Файл: `dimensions.py`

**Назначение:** Хранит физические размеры и вес товара.

**Поля:**

| Поле | Тип | Описание |
|------|-----|----------|
| `weight_kg` | `Optional[POSITIVE_F]` | Вес в килограммах |
| `width_cm` | `Optional[POSITIVE_F]` | Ширина в сантиметрах |
| `height_cm` | `Optional[POSITIVE_F]` | Высота в сантиметрах |
| `depth_cm` | `Optional[POSITIVE_F]` | Глубина в сантиметрах |
| `volume_m3` | `Optional[POSITIVE_F]` | Объём в кубических метрах |

**Валидации:**
- Если указаны все три габарита (`width_cm`, `height_cm`, `depth_cm`), а `volume_m3` не задан, объём вычисляется автоматически.

---

## 2. HandlingAttributes

Файл: `handling.py`

**Назначение:** Флаги, описывающие особые требования к обращению.

**Поля:**

| Поле | Тип | По умолч. | Описание |
|------|-----|-----------|----------|
| `is_fragile` | `bool` | `False` | Хрупкий товар |
| `is_stackable` | `bool` | `True` | Можно штабелировать |
| `is_odor_sensitive` | `bool` | `False` | Впитывает запахи |
| `requires_ventilation` | `bool` | `False` | Требуется вентиляция |
| `requires_quarantine` | `bool` | `False` | Требуется карантин после возврата |
| `is_magnetic` | `bool` | `False` | Магнитные свойства |
| `is_static_sensitive` | `bool` | `False` | Чувствителен к статическому электричеству |
| `irregular_shape` | `bool` | `False` | Неправильная форма |

**Валидации:**
- Если `is_fragile = True`, то `is_stackable` должно быть `False`.
- Если `is_odor_sensitive = True`, а `requires_ventilation = False`, выводится предупреждение.

---

## 3. Traceability

Файл: `traceability.py`

**Назначение:** Отслеживает товар на протяжении жизненного цикла.

**Поля:**

| Поле | Тип | Описание |
|------|-----|----------|
| `tracking_type` | `ProductTrackingType` | Способ отслеживания |
| `production_date` | `Optional[date]` | Дата производства |
| `expiry_date` | `Optional[date]` | Срок годности |

**Валидации:**
- `expiry_date` (если указан) не может быть в прошлом.
- Если указаны обе даты, `expiry_date` должна быть позже `production_date`.
- Если `tracking_type = EXPIRY_TRACKED`, обязательны `production_date` и `expiry_date`.

---

## 4. StorageRequirements

Файл: `storage_requires.py`

**Назначение:** Определяет условия хранения товара.

**Поля:**

| Поле | Тип | Описание |
|------|-----|----------|
| `storage_condition` | `Optional[ProductStorageCondition]` | Общие требования к хранению |
| `hazard_class` | `Optional[HazardClass]` | Класс опасного груза (если опасный) |
| `temperature_regime` | `Optional[TemperatureRegime]` | Требуемый температурный режим |
| `packaging_type` | `Optional[PackagingType]` | Тип используемой упаковки |

**Валидации:**
- Если `storage_condition = HAZARDOUS`, то `hazard_class` обязателен; если указан `hazard_class`, то `storage_condition` должно быть `HAZARDOUS`.
- Если `storage_condition` равно `PERISHABLE`, `TEMPERATURE_CONTROLLED` или `MEDICINE`, то `temperature_regime` обязателен.
- Если `storage_condition = ELECTRONICS`, а `temperature_regime` не указан, выводится предупреждение.

---

## 5. Classification

Файл: `classification.py`

**Назначение:** Классифицирует товар для оптимизации размещения на складе.

**Поля:**

| Поле | Тип | Описание |
|------|-----|----------|
| `size_type` | `Optional[ProductSizeType]` | Категория размера/веса |
| `moving_type` | `Optional[ProductMovingType]` | Характеристика оборачиваемости |
| `abc_category` | `Optional[ABCCategory]` | ABC‑классификация для оптимизации запасов |

**Валидации:**
- Если `size_type` равен `HEAVY` или `OVERSIZED`, то `moving_type` не может быть `FAST_MOVING`.
- Если `abc_category = A`, то `moving_type` должен быть `FAST_MOVING` или `NORMAL_MOVING`.