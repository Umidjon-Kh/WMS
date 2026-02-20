# WMS Enums Reference

This document provides a comprehensive reference for all enumeration classes used in the Warehouse Management System (WMS) data models. Each enum defines a set of constant values for specific attributes of products, helping to standardize data entry and enable consistent business logic.

---

## 1. `UnitOfMeasure`

Base units in which products are measured and tracked.

| Value | Description |
|-------|-------------|
| `PIECE` (`pc`) | Individual pieces (discrete count) |
| `KILOGRAM` (`kg`) | Kilograms |
| `GRAM` (`g`) | Grams |
| `LITER` (`l`) | Liters |
| `MILLILITER` (`ml`) | Milliliters |
| `METER` (`m`) | Meters (for roll/linear goods) |
| `CENTIMETER` (`cm`) | Centimeters |
| `SQUARE_METER` (`m2`) | Square meters |
| `CUBIC_METER` (`m3`) | Cubic meters (volume) |
| `BOX` (`box`) | Boxes (packaging unit) |
| `PALLET` (`pal`) | Pallets |
| `SET` (`set`) | Sets / kits |

---

## 2. `ProductPhysicalState`

Physical state of the product, influencing container type and handling methods.

| Value | Description |
|-------|-------------|
| `SOLID` | Solid goods (regular items, parts, furniture) |
| `BULK` | Bulk solids (sand, grain, granules) |
| `LIQUID` | Liquids (water, oil, chemicals) |
| `GAS` | Gases (propane, oxygen) |

---

## 3. `ProductStorageCondition`

General storage requirements for the product.

| Value | Description |
|-------|-------------|
| `PERISHABLE` | Perishable goods (require refrigeration/freezing) |
| `HAZARDOUS` | Hazardous materials (need special zones and safety measures) |
| `ELECTRONICS` | Electronics (sensitive to static, humidity) |
| `MEDICINE` | Medicines (strict temperature control, traceability) |
| `TEMPERATURE_CONTROLLED` | Requires specific temperature range |
| `VENTILATED` | Needs ventilation |
| `ODOR_SENSITIVE` | Absorbs odors – must not be stored near smelly items |
| `FOOD_SAFE` | Safe for contact with food products |

> **Note**: If the product is hazardous, detailed classification is provided by `HazardClass`.

---

## 4. `ProductSizeType`

Size/weight category, helping to choose appropriate storage locations.

| Value | Description |
|-------|-------------|
| `OVERSIZED` | Oversized (does not fit standard racks) |
| `HEAVY` | Heavy (requires reinforced shelving or floor storage) |
| `MEDIUM` | Medium-sized (standard racks) |
| `SMALL_PARTS` | Small parts (stored in bins, small boxes) |
| `BULKY` | Bulky but lightweight |
| `LIGHT` | Lightweight (can be stored on upper shelves) |
| `STANDARD` | Standard dimensions (default) |

---

## 5. `ProductMovingType`

Turnover characteristic, influencing storage placement (fast movers near shipping).

| Value | Description |
|-------|-------------|
| `FAST_MOVING` | High turnover (frequently shipped) |
| `NORMAL_MOVING` | Medium turnover |
| `SLOW_MOVING` | Low turnover |
| `HIGH_VALUE` | High-value items (may be stored in secured area) |
| `SEASONAL` | Seasonal goods |
| `PROMOTIONAL` | Promotional items (temporarily high turnover) |

---

## 6. `ProductTrackingType`

Method used to track inventory.

| Value | Description |
|-------|-------------|
| `PIECE` | Piece-level tracking |
| `WEIGHT_BASED` | Weight-based tracking |
| `KIT` | Kit (bundle of items) |
| `SERIALIZED` | Serial number tracking |
| `LOT_TRACKED` | Lot/batch tracking |
| `EXPIRY_TRACKED` | Expiry date tracking |

---

## 7. `ProductRoleType`

Role of the product in the production or logistics chain.

| Value | Description |
|-------|-------------|
| `RAW_MATERIAL` | Raw material for production |
| `COMPONENTS` | Components / subassemblies |
| `FINISHED_GOOD` | Finished product ready for sale |
| `RETURNS` | Returned items (awaiting disposition) |
| `WORK_IN_PROGRESS` | Work in progress (semi-finished) |
| `PACKAGING` | Packaging materials |
| `CONSUMABLE` | Consumable supplies |
| `TOOL` | Tools / equipment |
| `SPARE_PART` | Spare parts |
| `SCRAP` | Scrap / waste |
| `SAMPLE` | Samples (not for sale) |

---

## 8. `HazardClass`

International hazard class for dangerous goods (based on ADR/IMDG classifications).

| Value | Description |
|-------|-------------|
| `CLASS_1` | Explosives |
| `CLASS_2` | Gases |
| `CLASS_3` | Flammable liquids |
| `CLASS_4` | Flammable solids |
| `CLASS_5` | Oxidizing substances and organic peroxides |
| `CLASS_6` | Toxic and infectious substances |
| `CLASS_7` | Radioactive material |
| `CLASS_8` | Corrosive substances |
| `CLASS_9` | Miscellaneous dangerous substances |

---

## 9. `TemperatureRegime`

Generalized temperature requirements for storage.

| Value | Description |
|-------|-------------|
| `FROZEN` | Frozen (-18°C and below) |
| `DEEP_FROZEN` | Deep frozen (-30°C and below) |
| `CHILLED` | Chilled (0°C to +5°C) |
| `COOL` | Cool (+10°C to +15°C) |
| `AMBIENT` | Ambient room temperature |
| `WARM` | Warm (+20°C to +25°C) |
| `CONTROLLED` | Specific controlled range (defined separately) |

---

## 10. `ABCCategory`

ABC classification for inventory optimization (value and turnover).

| Value | Description |
|-------|-------------|
| `A` | High value / fast moving |
| `B` | Medium value / medium moving |
| `C` | Low value / slow moving |
| `D` | Obsolete / very slow moving |

---

## 11. `HandlingAttribute`

Special handling attributes that can be combined (usually implemented as separate boolean fields in the model, listed here for reference).

| Value | Description |
|-------|-------------|
| `FRAGILE` | Fragile – requires careful handling |
| `STACKABLE` | Can be stacked |
| `ODOR_SENSITIVE` | Absorbs odors |
| `REQUIRES_VENTILATION` | Needs ventilation |
| `REQUIRES_QUARANTINE` | Requires quarantine (e.g., after returns) |
| `MAGNETIC` | Magnetic properties |
| `STATIC_SENSITIVE` | Sensitive to static electricity |
| `HEAVY` | Heavy (if not covered by `ProductSizeType`) |
| `LARGE` | Large |
| `IRREGULAR_SHAPE` | Irregular shape |

---

## 12. `PackagingType`

Type of packaging used for storage or shipping.

| Value | Description |
|-------|-------------|
| `BAG` | Bag |
| `BOX` | Box |
| `CRATE` | Crate (wooden/plastic) |
| `DRUM` | Drum |
| `PALLET` | Pallet |
| `IBC` | Intermediate Bulk Container |
| `TOTE` | Tote / bin with lid |
| `CYLINDER` | Cylinder (for gases) |
| `CARDBOARD` | Cardboard packaging |
| `SHRINK_WRAP` | Shrink wrap / stretch film |
| `NONE` | No packaging / loose |

---

## 13. `ProductStatus`

Lifecycle status of the product in the catalog.

| Value | Description |
|-------|-------------|
| `ACTIVE` | Active, available for operations |
| `INACTIVE` | Inactive, temporarily not used |
| `DISCONTINUED` | Discontinued |
| `COMING_SOON` | Coming soon |
| `PENDING_APPROVAL` | Pending approval |
| `UNDER_REVIEW` | Under review |
| `RETURNED` | Returned (awaiting decision) |
| `DAMAGED` | Damaged |
| `QUARANTINED` | In quarantine |

---

*This reference is intended for developers and integrators working with the WMS data models.*