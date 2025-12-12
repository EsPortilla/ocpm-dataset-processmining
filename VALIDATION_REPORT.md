# OCEL Pharma Manufacturing Dataset - Validation Report

**Generation Date:** 2025-12-12
**Generator Version:** 1.0
**Validation Status:** ✓ PASSED

## Dataset Statistics

### Object Counts
- **Batch:** 1,500
- **Deviation:** 240
- **Equipment:** 31
- **MarketOrder:** 1,500
- **MaterialLot:** 4,000
- **ProductionLine:** 11
- **QCSample:** 1,554

**Total Objects:** 8,836

### Event Statistics
- **Total Events:** 22,284
- **Total Event-Object Links:** 57,378

### Events by Area
- **Maintenance:** 85
- **Packaging:** 3,204
- **Planning:** 3,075
- **Production:** 8,771
- **QA:** 2,555
- **QC_Lab:** 3,054
- **Warehouse:** 1,540

## Integrity Validation Results

All Module 9 integrity constraints passed successfully:

### ✓ 1. Start/End Pairing
Every batch has properly paired Start/End events for all manufacturing operations.
No timing violations detected.

### ✓ 2. Cancellation Constraint
Cancelled batches have no Start_* manufacturing events.
All early cancellations occur after staging only.

### ✓ 3. QC Decision Constraint
- Non-cancelled batches: Exactly 1 QP Decision event
- Cancelled batches: 0 QP Decision events (expected)

### ✓ 4. QC Sample Linkage
Every QC Result event is properly linked to an existing QCSample object.
Re-test loops correctly create new QCSample objects.

### ✓ 5. Deviation Lifecycle
All Deviation objects have complete lifecycle:
- Deviation Opened
- Investigation
- Deviation Closed (or appropriate closure event)

### ✓ 6. No Orphan Objects
All required objects (Batch, QCSample, Deviation, Equipment) appear in at least one event.
Inventory objects (MaterialLot, MarketOrder) and static objects (ProductionLine) allowed to be unused.

### ✓ 7. No Orphan Events
Every event links to at least one object.

## Scenario Distribution

The dataset includes all required scenario families plus additional variants:

### Required Scenarios
1. **Happy path** (~40%) - Clean backbone, conforming QC, release
2. **Deviation after major unit** (~10%) - With rework and IPC sampling
3. **Machine downtime** (~8%) - Causing delays during operations
4. **Early cancellation** (~5%) - After staging, before manufacturing
5. **QC OOS → rejection** (~5%) - End-of-flow rejection
6. **Complex** (~4%) - Combined downtime + deviation + extended QA

### Additional Scenarios (Module 7 A-F)
- **A. Material substitution** (~7%) - Mid-flow material change + deviation + QA review
- **B. Line change** (~6%) - Operations across different lines
- **C. Split packaging** (~5%) - One batch, two packaging runs
- **D. Re-test loop** (~5%) - New QCSample after OOS, potential recovery
- **E. Documentation deviation** (~3%) - Post-packaging, no physical rework
- **F. Preventive maintenance** (~2%) - Queueing across multiple batches

## File Outputs

### OCEL Files
1. **ocel_events.csv** (2.1 MB) - 22,284 events
2. **ocel_objects.csv** (178 KB) - 8,836 objects
3. **ocel_event_objects.csv** (1.1 MB) - 57,378 linkages
4. **ocel_object_attributes.csv** (550 KB) - All object attributes

### Case-Centric Projection (50-100 batches)
1. **case_centric_events_small.csv** (111 KB) - 1,117 events for 75 batches
2. **case_centric_attributes_small.csv** (6.7 KB) - Batch attributes

## Fixed Infrastructure

### Plants (3)
- PLANT_SOLIDS
- PLANT_PARENTERAL
- PLANT_SPECIAL

### Production Lines (11)
- **Tablets:** TL1, TL2, TL3 (PLANT_SOLIDS)
- **Capsules:** CL1, CL2 (PLANT_SOLIDS)
- **Injectables:** INJ1, INJ2 (PLANT_PARENTERAL)
- **Hormonals:** HORM1, HORM2 (PLANT_SPECIAL)
- **Devices:** DEV1, DEV2 (PLANT_SPECIAL)

### Product Catalog (10)
- **Tablets:** PARA500TAB, IBUP400TAB
- **Capsules:** AMOX500CAP, OMEP20CAP
- **Injectables:** CEF1GIV, HEP5000SC
- **Hormonals:** EE30TAB, LEVOHORMIMPL
- **Devices:** INSUPEN, INHALER

## Process Mining Suitability

This dataset is suitable for:
- **Process discovery** - Clear backbone flows with variants
- **Conformance checking** - Known process models vs. actual executions
- **Performance analysis** - Realistic durations, bottlenecks, queueing
- **Object-centric analysis** - Multi-object interactions (Batch, Equipment, Materials, QC, Deviations)
- **Deviation analysis** - Various deviation types with complete lifecycles
- **Resource analysis** - Equipment utilization, line changes
- **Root cause analysis** - Deviations, rework, downtimes

## Technical Details

- **Time span:** 24 months (2023-01-01 to 2024-12-31)
- **Timestamp format:** ISO8601 (YYYY-MM-DDTHH:MM:SS)
- **Random seed:** 42 (reproducible)
- **Event ID format:** EVT000001 - EVT022284
- **Batch ID format:** BATCH00001 - BATCH01500

---

**Validation Conclusion:** Dataset successfully generated and validated. All integrity constraints satisfied. Ready for process mining analysis and training.
