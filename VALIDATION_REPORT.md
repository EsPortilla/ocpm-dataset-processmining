# OCEL Pharma Manufacturing Dataset - Validation Report

**Generation Date:** 2025-12-12
**Generator Version:** 2.0 (Scaled)
**Validation Status:** ✓ PASSED

## Dataset Statistics

### Object Counts
- **Batch:** 10,000
- **Deviation:** 1,637
- **Equipment:** 31
- **MarketOrder:** 10,000
- **MaterialLot:** 25,000
- **ProductionLine:** 11
- **QCSample:** 10,405

**Total Objects:** 57,084

### Event Statistics
- **Total Events:** 148,394
- **Total Event-Object Links:** 381,942

### Events by Area
- **Maintenance:** 565
- **Packaging:** 21,235
- **Planning:** 20,500
- **Production:** 58,336
- **QA:** 17,070
- **QC_Lab:** 20,405
- **Warehouse:** 10,283

## Integrity Validation Results

All Module 9 integrity constraints passed successfully:

### ✓ 1. Start/End Pairing
Every batch has properly paired Start/End events for all manufacturing operations.
No timing violations detected across 148,394 events.

### ✓ 2. Cancellation Constraint
Cancelled batches have no Start_* manufacturing events.
All early cancellations occur after staging only.

### ✓ 3. QC Decision Constraint
- Non-cancelled batches: Exactly 1 QP Decision event (9,500 batches)
- Cancelled batches: 0 QP Decision events (500 batches)

### ✓ 4. QC Sample Linkage
Every QC Result event is properly linked to an existing QCSample object.
10,405 QC samples created across all batches.
Re-test loops correctly create new QCSample objects.

### ✓ 5. Deviation Lifecycle
All 1,637 Deviation objects have complete lifecycle:
- Deviation Opened
- Investigation
- Deviation Closed (or appropriate closure event)

### ✓ 6. No Orphan Objects
All required objects (Batch, QCSample, Deviation, Equipment) appear in at least one event.
Inventory objects (MaterialLot, MarketOrder) and static objects (ProductionLine) allowed to be unused.

### ✓ 7. No Orphan Events
Every event links to at least one object across 381,942 event-object linkages.

## Scenario Distribution

The dataset includes all required scenario families plus additional variants across 10,000 batches:

### Required Scenarios
1. **Happy path** (~4,000 batches) - Clean backbone, conforming QC, release
2. **Deviation after major unit** (~1,000 batches) - With rework and IPC sampling
3. **Machine downtime** (~800 batches) - Causing delays during operations
4. **Early cancellation** (~500 batches) - After staging, before manufacturing
5. **QC OOS → rejection** (~500 batches) - End-of-flow rejection
6. **Complex** (~400 batches) - Combined downtime + deviation + extended QA

### Additional Scenarios (Module 7 A-F)
- **A. Material substitution** (~700 batches) - Mid-flow material change + deviation + QA review
- **B. Line change** (~600 batches) - Operations across different lines
- **C. Split packaging** (~500 batches) - One batch, two packaging runs
- **D. Re-test loop** (~500 batches) - New QCSample after OOS, potential recovery
- **E. Documentation deviation** (~300 batches) - Post-packaging, no physical rework
- **F. Preventive maintenance** (~200 batches) - Queueing across multiple batches on same equipment

## File Outputs

### OCEL Files
1. **ocel_events.csv** (14 MB) - 148,394 events
2. **ocel_objects.csv** (1.2 MB) - 57,084 objects
3. **ocel_event_objects.csv** (7.3 MB) - 381,942 linkages
4. **ocel_object_attributes.csv** (3.5 MB) - All object attributes

### Case-Centric Projection (Full Dataset)
1. **case_centric_events.csv** (15 MB) - 148,304 events for all 10,000 batches
2. **case_centric_attributes.csv** (882 KB) - Batch attributes for all 10,000 batches

**Note:** Case-centric projection now includes the FULL dataset (all batches), not a subset.
Every event includes the batch's assigned production line for complete traceability.

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

## Activity Catalog

### Planning & Release (Area: Planning)
- **Plan Batch** - Initial batch planning and scheduling based on demand
- **Release Batch** - Authorization to begin manufacturing operations
- **Batch Cancelled (Material Issue)** - Early termination due to material unavailability or issues

### Material Staging (Area: Warehouse)
- **Stage Materials** - Preparation and staging of raw materials and excipients for production
- **Stage Components** - Preparation and staging of device components for assembly

### Manufacturing - Solids: Tablets & Capsules (Area: Production)
- **Start Granulation** - Begin granulation process for solid dosage forms
- **End Granulation** - Complete granulation process
- **Start Compression** - Begin tablet compression or capsule filling
- **End Compression** - Complete compression or filling operation
- **Start Coating** - Begin coating process for tablets/capsules
- **End Coating** - Complete coating operation
- **Start Packaging** - Begin primary and secondary packaging
- **End Packaging** - Complete packaging operation

### Manufacturing - Injectables (Area: Production)
- **Start Solution Preparation** - Begin preparation of injectable solution
- **End Solution Preparation** - Complete solution preparation
- **Sterile Filtration** - Sterile filtration of prepared solution
- **Start Filling** - Begin aseptic filling of vials/syringes
- **End Filling** - Complete filling operation
- **Capping** - Seal vials/syringes with caps or stoppers
- **Lyophilization** - Freeze-drying process for lyophilized products
- **Visual Inspection** - Manual or automated visual inspection for defects

### Manufacturing - Hormonals (Area: Production)
- **Segregated Area Cleaning** - Pre-production cleaning of dedicated hormonal area
- **Extended QA Review** - Additional quality review for hormonal products

### Manufacturing - Devices (Area: Production)
- **Start Component Assembly** - Begin assembly of device components
- **End Component Assembly** - Complete component assembly
- **Start Device Calibration** - Begin calibration and functional testing
- **End Device Calibration** - Complete calibration process
- **Final Assembly** - Final device assembly and integration
- **IFU Insertion Check** - Verification of Instructions For Use insertion

### Quality Control (Area: QC_Lab)
- **QC FP Sampling** - Final product sampling for quality testing
- **QC IPC Sampling** - In-process control sampling during manufacturing
- **QC Result (Conforming)** - Test results meet specifications
- **QC Result (OOS)** - Test results out of specification (OOS)

### Quality Assurance (Area: QA)
- **QP Decision (Release)** - Qualified Person authorizes batch release
- **QP Decision (Reject)** - Qualified Person rejects batch
- **Extended QA Review** - Additional QA review for complex issues

### Deviation Management (Area: QA)
- **Deviation Opened** - Initiation of deviation investigation
- **Investigation** - Root cause analysis and investigation activities
- **Deviation Closed** - Closure of deviation with approved corrective actions

### Maintenance (Area: Maintenance)
- **Equipment Downtime** - Unplanned equipment failure or breakdown
- **Preventive Maintenance** - Scheduled preventive maintenance activities

### Rework (Area: Production)
- **Start Rework** - Begin rework operations to address quality issues
- **End Rework** - Complete rework operations

## Process Mining Suitability

This dataset is suitable for:
- **Process discovery** - Clear backbone flows with variants across 10K cases
- **Conformance checking** - Known process models vs. actual executions
- **Performance analysis** - Realistic durations, bottlenecks, queueing across large scale
- **Object-centric analysis** - Multi-object interactions (Batch, Equipment, Materials, QC, Deviations)
- **Deviation analysis** - 1,637 deviations with complete lifecycles
- **Resource analysis** - Equipment utilization, line changes, capacity planning
- **Root cause analysis** - Statistical patterns across deviations, rework, downtimes
- **Variant analysis** - Sufficient volume for clustering and pattern mining
- **Predictive modeling** - Large training dataset for ML/AI applications

## Technical Details

- **Time span:** 48 months (2023-01-01 to 2026-12-31)
- **Timestamp format:** ISO8601 (YYYY-MM-DDTHH:MM:SS)
- **Random seed:** 42 (reproducible)
- **Event ID format:** EVT000001 - EVT148394
- **Batch ID format:** BATCH00001 - BATCH10000
- **Deviation ID format:** DEVIAT0001 - DEVIAT1637
- **QC Sample ID format:** QCS00001 - QCS10405

## Scale Configuration

```python
TARGET_BATCHES = 10000
TARGET_MATERIAL_LOTS = 25000
TARGET_MARKET_ORDERS = 10000
TIME_WINDOW_MONTHS = 48
```

## Performance Characteristics

- **Generation time:** ~8 minutes for full dataset
- **Validation time:** ~2 minutes for 148K events
- **Memory footprint:** ~500 MB during generation
- **CSV total size:** ~42 MB (highly compressible)

---

**Validation Conclusion:** Large-scale dataset successfully generated and validated. All integrity constraints satisfied across 10,000 batches and 148,394 events. Ready for industrial-scale process mining analysis, machine learning training, and academic research.
