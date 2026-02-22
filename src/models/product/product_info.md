# Product Model Documentation

The `BaseProduct` class is the core model representing a product in the Warehouse Management System. It consists of several compositions that group related attributes.

## Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `sku` | `SKU_VALID` (annotated string) | Stock Keeping Unit – unique product identifier | Yes |
| `name` | `NAME_VALID` (annotated string) | Product name | Yes |
| `unit_of_measure` | `UnitOfMeasure` (enum) | Base unit of measure (piece, kg, liter, etc.) | Yes |
| `physical_state` | `ProductPhysicalState` (enum) | Physical state (solid, liquid, gas, bulk) | Yes |
| `role_type` | `ProductRoleType` (enum) | Role in production/logistic chain | Yes |
| `status` | `ProductStatus` (enum) | Current lifecycle status | Yes |
| `description` | `Optional[DES_VALID]` | Optional product description | No |

## Compositions

| Composition | Description |
|-------------|-------------|
| `dimensions` | Physical dimensions and weight |
| `handling` | Handling flags (fragile, stackable, etc.) |
| `traceability` | Tracking type, production and expiry dates |
| `storage_requirements` | Storage conditions (hazardous, temperature, packaging) |
| `classification` | Size type, moving type, ABC category |

Each composition is defined in its own module and contains its own validations.

## Technical Fields

| Field | Type | Description |
|-------|------|-------------|
| `created_at` | `datetime` | Timestamp of creation (auto-set) |
| `updated_at` | `datetime` | Timestamp of last update (auto-set) |

## Cross-Validations

The `BaseProduct` class includes several cross‑validators that ensure consistency between different compositions. See the `Validators.md` file for details.