#!/usr/bin/env python3
"""
OCEL Generator for Pharmaceutical Manufacturing
Generates object-centric event log with 24 months of operations
"""

import csv
import random
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Tuple, Set
import os

# Set random seed for reproducibility
random.seed(42)

# Module 2: Fixed Infrastructure
PLANTS = {
    'PLANT_SOLIDS': ['TL1', 'TL2', 'TL3', 'CL1', 'CL2'],
    'PLANT_PARENTERAL': ['INJ1', 'INJ2'],
    'PLANT_SPECIAL': ['HORM1', 'HORM2', 'DEV1', 'DEV2']
}

LINE_TO_PLANT = {}
LINE_TO_DOSAGE = {}

# Tablets
for line in ['TL1', 'TL2', 'TL3']:
    LINE_TO_PLANT[line] = 'PLANT_SOLIDS'
    LINE_TO_DOSAGE[line] = 'Tablet'

# Capsules
for line in ['CL1', 'CL2']:
    LINE_TO_PLANT[line] = 'PLANT_SOLIDS'
    LINE_TO_DOSAGE[line] = 'Capsule'

# Injectables
for line in ['INJ1', 'INJ2']:
    LINE_TO_PLANT[line] = 'PLANT_PARENTERAL'
    LINE_TO_DOSAGE[line] = 'Injectable'

# Hormonals
for line in ['HORM1', 'HORM2']:
    LINE_TO_PLANT[line] = 'PLANT_SPECIAL'
    LINE_TO_DOSAGE[line] = 'Hormonal'

# Devices
for line in ['DEV1', 'DEV2']:
    LINE_TO_PLANT[line] = 'PLANT_SPECIAL'
    LINE_TO_DOSAGE[line] = 'Device'

# Module 3: Product Catalog
PRODUCTS = {
    'PARA500TAB': {'dosage': 'Tablet', 'lines': ['TL1', 'TL2', 'TL3'], 'market': 'ES', 'client_type': 'OwnBrand', 'api_risk': 'Low'},
    'IBUP400TAB': {'dosage': 'Tablet', 'lines': ['TL1', 'TL2', 'TL3'], 'market': 'FR', 'client_type': 'OwnBrand', 'api_risk': 'Medium'},
    'AMOX500CAP': {'dosage': 'Capsule', 'lines': ['CL1', 'CL2'], 'market': 'DE', 'client_type': 'Contract', 'api_risk': 'High'},
    'OMEP20CAP': {'dosage': 'Capsule', 'lines': ['CL1', 'CL2'], 'market': 'IT', 'client_type': 'OwnBrand', 'api_risk': 'Low'},
    'CEF1GIV': {'dosage': 'Injectable', 'lines': ['INJ1', 'INJ2'], 'market': 'UK', 'client_type': 'Contract', 'api_risk': 'High'},
    'HEP5000SC': {'dosage': 'Injectable', 'lines': ['INJ1', 'INJ2'], 'market': 'FR', 'client_type': 'OwnBrand', 'api_risk': 'Medium'},
    'EE30TAB': {'dosage': 'Hormonal', 'lines': ['HORM1', 'HORM2'], 'market': 'PT', 'client_type': 'OwnBrand', 'api_risk': 'Low'},
    'LEVOHORMIMPL': {'dosage': 'Hormonal', 'lines': ['HORM1', 'HORM2'], 'market': 'ES', 'client_type': 'Contract', 'api_risk': 'Medium'},
    'INSUPEN': {'dosage': 'Device', 'lines': ['DEV1', 'DEV2'], 'market': 'DE', 'client_type': 'OwnBrand', 'api_risk': 'Medium'},
    'INHALER': {'dosage': 'Device', 'lines': ['DEV1', 'DEV2'], 'market': 'UK', 'client_type': 'Contract', 'api_risk': 'Low'},
}

# Equipment types by dosage form
EQUIPMENT_TYPES = {
    'Tablet': [
        ('COMP', 'Compression'),
        ('COAT', 'Coating'),
        ('PACK', 'Packaging')
    ],
    'Capsule': [
        ('FILL', 'Filling'),
        ('PACK', 'Packaging')
    ],
    'Injectable': [
        ('FILL', 'Filling'),
        ('LYO', 'Lyophilization'),
        ('PACK', 'Packaging')
    ],
    'Hormonal': [
        ('COMP', 'Compression'),
        ('COAT', 'Coating'),
        ('PACK', 'Packaging')
    ],
    'Device': [
        ('ASSEMBLY', 'Assembly'),
        ('CALIB', 'Calibration'),
        ('PACK', 'Packaging')
    ]
}

# Global counters
event_counter = 0
batch_counter = 0
material_lot_counter = 0
qc_sample_counter = 0
deviation_counter = 0
market_order_counter = 0

# Data structures
events = []
objects = []
event_objects = []
object_attributes = []

# Start date: 2023-01-01
START_DATE = datetime(2023, 1, 1, 8, 0, 0)
END_DATE = START_DATE + timedelta(days=730)  # 24 months


def generate_event_id():
    global event_counter
    event_counter += 1
    return f"EVT{event_counter:06d}"


def generate_batch_id():
    global batch_counter
    batch_counter += 1
    return f"BATCH{batch_counter:05d}"


def generate_material_lot_id():
    global material_lot_counter
    material_lot_counter += 1
    return f"MAT{material_lot_counter:05d}"


def generate_qc_sample_id():
    global qc_sample_counter
    qc_sample_counter += 1
    return f"QCS{qc_sample_counter:05d}"


def generate_deviation_id():
    global deviation_counter
    deviation_counter += 1
    return f"DEVIAT{deviation_counter:04d}"


def generate_market_order_id():
    global market_order_counter
    market_order_counter += 1
    return f"MO{market_order_counter:05d}"


def format_timestamp(dt):
    """Format datetime to ISO8601 without microseconds"""
    return dt.strftime('%Y-%m-%dT%H:%M:%S')


def create_event(activity, area, start_dt, end_dt, linked_objects):
    """Create an event and its object linkages"""
    event_id = generate_event_id()

    events.append({
        'event_id': event_id,
        'activity': activity,
        'area': area,
        'event_start': format_timestamp(start_dt),
        'event_end': format_timestamp(end_dt),
        'event_timestamp': format_timestamp(start_dt)
    })

    for obj_id in linked_objects:
        event_objects.append({
            'event_id': event_id,
            'object_id': obj_id
        })

    return event_id, end_dt


def create_production_lines():
    """Create ProductionLine objects"""
    for plant, lines in PLANTS.items():
        for line in lines:
            objects.append({
                'object_id': line,
                'object_type': 'ProductionLine'
            })
            object_attributes.append({
                'object_id': line,
                'plant': plant,
                'dosage_specialization': LINE_TO_DOSAGE[line]
            })


def create_equipment():
    """Create Equipment objects (2-3 per line)"""
    equipment_list = []

    for line in LINE_TO_PLANT.keys():
        dosage = LINE_TO_DOSAGE[line]
        equip_types = EQUIPMENT_TYPES[dosage]

        for eq_code, eq_name in equip_types:
            equip_id = f"{line}_{eq_code}"
            equipment_list.append(equip_id)

            objects.append({
                'object_id': equip_id,
                'object_type': 'Equipment'
            })
            object_attributes.append({
                'object_id': equip_id,
                'line_id': line,
                'equipment_type': eq_code
            })

    return equipment_list


def create_material_lots(count):
    """Create MaterialLot objects"""
    material_lots = []

    for _ in range(count):
        mat_id = generate_material_lot_id()
        material_lots.append(mat_id)

        objects.append({
            'object_id': mat_id,
            'object_type': 'MaterialLot'
        })

        mat_type = random.choice(['API', 'API', 'Excipient', 'Component'])
        supplier_risk = random.choice(['Low', 'Low', 'Medium', 'High'])
        expiry = START_DATE + timedelta(days=random.randint(365, 1095))

        object_attributes.append({
            'object_id': mat_id,
            'material_type': mat_type,
            'supplier_risk': supplier_risk,
            'expiry_date': format_timestamp(expiry)
        })

    return material_lots


def create_market_orders(count):
    """Create MarketOrder objects"""
    market_orders = []

    for _ in range(count):
        mo_id = generate_market_order_id()
        market_orders.append(mo_id)

        objects.append({
            'object_id': mo_id,
            'object_type': 'MarketOrder'
        })

        market = random.choice(['ES', 'FR', 'DE', 'IT', 'PT', 'UK'])
        req_qty = random.randint(5000, 100000)
        due_date = START_DATE + timedelta(days=random.randint(30, 730))

        object_attributes.append({
            'object_id': mo_id,
            'market': market,
            'requested_qty': str(req_qty),
            'due_date': format_timestamp(due_date)
        })

    return market_orders


def get_equipment_for_line(line, equip_type):
    """Get equipment ID for a line and type"""
    return f"{line}_{equip_type}"


class BatchGenerator:
    def __init__(self, material_lots, market_orders, equipment_list):
        self.material_lots = material_lots
        self.market_orders = market_orders
        self.equipment_list = equipment_list
        self.qc_samples = []
        self.deviations = []

    def generate_batch(self, product_code, start_time, scenario_type='happy_path'):
        """Generate a complete batch with events"""
        batch_id = generate_batch_id()
        product_info = PRODUCTS[product_code]
        dosage = product_info['dosage']
        line = random.choice(product_info['lines'])
        plant = LINE_TO_PLANT[line]

        # Create Batch object
        objects.append({
            'object_id': batch_id,
            'object_type': 'Batch'
        })

        # Determine quantities
        if dosage in ['Tablet', 'Capsule']:
            planned_qty = random.randint(50000, 500000)
            uom = 'TabletsCaps'
        else:
            planned_qty = random.randint(1000, 50000)
            uom = 'Units'

        # Create batch attributes
        object_attributes.append({
            'object_id': batch_id,
            'product_code': product_code,
            'dosage_form': dosage,
            'plant': plant,
            'line': line,
            'market': product_info['market'],
            'client_type': product_info['client_type'],
            'campaign_flag': random.choice(['Yes', 'No', 'No', 'No']),
            'priority': random.choice(['High', 'Medium', 'Medium', 'Low']),
            'planned_qty': str(planned_qty),
            'uom': uom,
            'api_supplier_risk': product_info['api_risk']
        })

        # Generate events based on scenario
        if scenario_type == 'happy_path':
            self._generate_happy_path(batch_id, dosage, line, start_time)
        elif scenario_type == 'deviation_rework':
            self._generate_deviation_rework(batch_id, dosage, line, start_time)
        elif scenario_type == 'downtime':
            self._generate_downtime(batch_id, dosage, line, start_time)
        elif scenario_type == 'early_cancel':
            self._generate_early_cancel(batch_id, dosage, line, start_time)
        elif scenario_type == 'oos_reject':
            self._generate_oos_reject(batch_id, dosage, line, start_time)
        elif scenario_type == 'complex':
            self._generate_complex(batch_id, dosage, line, start_time)
        elif scenario_type == 'material_substitution':
            self._generate_material_substitution(batch_id, dosage, line, start_time)
        elif scenario_type == 'line_change':
            self._generate_line_change(batch_id, dosage, line, start_time)
        elif scenario_type == 'split_packaging':
            self._generate_split_packaging(batch_id, dosage, line, start_time)
        elif scenario_type == 'retest_loop':
            self._generate_retest_loop(batch_id, dosage, line, start_time)
        elif scenario_type == 'doc_deviation':
            self._generate_doc_deviation(batch_id, dosage, line, start_time)
        elif scenario_type == 'preventive_maintenance':
            self._generate_preventive_maintenance(batch_id, dosage, line, start_time)

        return batch_id

    def _generate_happy_path(self, batch_id, dosage, line, start_time):
        """Generate happy path scenario"""
        current_time = start_time

        # Planning
        mo_id = random.choice(self.market_orders) if random.random() < 0.7 else None
        plan_objs = [batch_id, mo_id] if mo_id else [batch_id]
        _, current_time = create_event(
            'Plan Batch', 'Planning', current_time,
            current_time + timedelta(hours=random.uniform(0.25, 2)),
            plan_objs
        )

        # Release
        current_time += timedelta(hours=random.uniform(1, 8))
        _, current_time = create_event(
            'Release Batch', 'Planning', current_time,
            current_time + timedelta(hours=random.uniform(0.25, 1)),
            [batch_id]
        )

        # Stage Materials
        current_time += timedelta(hours=random.uniform(0.5, 4))
        mat_lots = random.sample(self.material_lots, random.randint(2, 5))
        _, current_time = create_event(
            'Stage Materials' if dosage != 'Device' else 'Stage Components',
            'Warehouse', current_time,
            current_time + timedelta(hours=random.uniform(1, 6)),
            [batch_id, line] + mat_lots
        )

        # Manufacturing backbone
        if dosage in ['Tablet', 'Capsule']:
            current_time = self._generate_solids_backbone(batch_id, line, current_time, dosage)
        elif dosage == 'Injectable':
            current_time = self._generate_injectable_backbone(batch_id, line, current_time)
        elif dosage == 'Hormonal':
            current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
        elif dosage == 'Device':
            current_time = self._generate_device_backbone(batch_id, line, current_time)

        # QC and Release
        self._generate_qc_release(batch_id, current_time, conforming=True)

    def _generate_solids_backbone(self, batch_id, line, start_time, dosage):
        """Solids (Tablet/Capsule) backbone - both use same flow per Module 5"""
        current_time = start_time

        # Granulation
        current_time += timedelta(hours=random.uniform(0.5, 2))
        gran_equip = get_equipment_for_line(line, 'FILL' if dosage == 'Capsule' else 'COMP')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
        create_event('Start Granulation', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, gran_equip])
        _, current_time = create_event('End Granulation', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, gran_equip])

        # Compression
        current_time += timedelta(hours=random.uniform(0.5, 2))
        comp_equip = get_equipment_for_line(line, 'FILL' if dosage == 'Capsule' else 'COMP')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(3, 8))
        create_event('Start Compression', 'Production',
                    start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, comp_equip])
        _, current_time = create_event('End Compression', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, comp_equip])

        # Coating
        current_time += timedelta(hours=random.uniform(0.5, 2))
        coat_equip = get_equipment_for_line(line, 'FILL' if dosage == 'Capsule' else 'COAT')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
        create_event('Start Coating', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, coat_equip])
        _, current_time = create_event('End Coating', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, coat_equip])

        # Packaging
        current_time += timedelta(hours=random.uniform(0.5, 2))
        pack_equip = get_equipment_for_line(line, 'PACK')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(3, 10))
        create_event('Start Packaging', 'Packaging', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, pack_equip])
        _, current_time = create_event('End Packaging', 'Packaging', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, pack_equip])

        return current_time

    def _generate_injectable_backbone(self, batch_id, line, start_time):
        """Injectable backbone"""
        current_time = start_time

        # Solution Preparation
        current_time += timedelta(hours=random.uniform(0.5, 2))
        fill_equip = get_equipment_for_line(line, 'FILL')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
        create_event('Start Solution Preparation', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, fill_equip])
        _, current_time = create_event('End Solution Preparation', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, fill_equip])

        # Sterile Filtration
        current_time += timedelta(minutes=30)
        _, current_time = create_event('Sterile Filtration', 'Production', current_time,
                    current_time + timedelta(hours=random.uniform(1, 3)),
                    [batch_id, line, fill_equip])

        # Filling
        current_time += timedelta(hours=random.uniform(0.5, 1))
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(3, 8))
        create_event('Start Filling', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, fill_equip])
        _, current_time = create_event('End Filling', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, fill_equip])

        # Capping
        current_time += timedelta(minutes=30)
        _, current_time = create_event('Capping', 'Production', current_time,
                    current_time + timedelta(hours=random.uniform(1, 2)),
                    [batch_id, line, fill_equip])

        # Lyophilization
        current_time += timedelta(hours=1)
        lyo_equip = get_equipment_for_line(line, 'LYO')
        _, current_time = create_event('Lyophilization', 'Production', current_time,
                    current_time + timedelta(hours=random.uniform(12, 24)),
                    [batch_id, line, lyo_equip])

        # Visual Inspection
        current_time += timedelta(hours=2)
        _, current_time = create_event('Visual Inspection', 'Production', current_time,
                    current_time + timedelta(hours=random.uniform(2, 4)),
                    [batch_id, line])

        # Packaging
        current_time += timedelta(hours=random.uniform(0.5, 2))
        pack_equip = get_equipment_for_line(line, 'PACK')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(3, 8))
        create_event('Start Packaging', 'Packaging', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, pack_equip])
        _, current_time = create_event('End Packaging', 'Packaging', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, pack_equip])

        return current_time

    def _generate_hormonal_backbone(self, batch_id, line, start_time):
        """Hormonal backbone"""
        current_time = start_time

        # Segregated Area Cleaning
        current_time += timedelta(hours=random.uniform(0.5, 2))
        _, current_time = create_event('Segregated Area Cleaning', 'Production', current_time,
                    current_time + timedelta(hours=random.uniform(2, 4)),
                    [batch_id, line])

        # Granulation
        current_time += timedelta(hours=1)
        comp_equip = get_equipment_for_line(line, 'COMP')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
        create_event('Start Granulation', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, comp_equip])
        _, current_time = create_event('End Granulation', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, comp_equip])

        # Compression
        current_time += timedelta(hours=random.uniform(0.5, 2))
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(3, 8))
        create_event('Start Compression', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, comp_equip])
        _, current_time = create_event('End Compression', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, comp_equip])

        # Coating
        current_time += timedelta(hours=random.uniform(0.5, 2))
        coat_equip = get_equipment_for_line(line, 'COAT')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
        create_event('Start Coating', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, coat_equip])
        _, current_time = create_event('End Coating', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, coat_equip])

        # Packaging
        current_time += timedelta(hours=random.uniform(0.5, 2))
        pack_equip = get_equipment_for_line(line, 'PACK')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(3, 10))
        create_event('Start Packaging', 'Packaging', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, pack_equip])
        _, current_time = create_event('End Packaging', 'Packaging', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, pack_equip])

        # Extended QA Review (hormonal specific)
        current_time += timedelta(hours=random.uniform(2, 8))
        _, current_time = create_event('Extended QA Review', 'QA', current_time,
                    current_time + timedelta(hours=random.uniform(4, 24)),
                    [batch_id])

        return current_time

    def _generate_device_backbone(self, batch_id, line, start_time):
        """Device backbone"""
        current_time = start_time

        # Component Assembly
        current_time += timedelta(hours=random.uniform(0.5, 2))
        asm_equip = get_equipment_for_line(line, 'ASSEMBLY')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
        create_event('Start Component Assembly', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, asm_equip])
        _, current_time = create_event('End Component Assembly', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, asm_equip])

        # Device Calibration
        current_time += timedelta(hours=random.uniform(0.5, 2))
        cal_equip = get_equipment_for_line(line, 'CALIB')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
        create_event('Start Device Calibration', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, cal_equip])
        _, current_time = create_event('End Device Calibration', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, cal_equip])

        # Final Assembly
        current_time += timedelta(hours=random.uniform(0.5, 1))
        _, current_time = create_event('Final Assembly', 'Production', current_time,
                    current_time + timedelta(hours=random.uniform(1, 3)),
                    [batch_id, line, asm_equip])

        # Packaging
        current_time += timedelta(hours=random.uniform(0.5, 2))
        pack_equip = get_equipment_for_line(line, 'PACK')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(3, 8))
        create_event('Start Packaging', 'Packaging', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, pack_equip])
        _, current_time = create_event('End Packaging', 'Packaging', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, pack_equip])

        # IFU Insertion Check
        current_time += timedelta(minutes=30)
        _, current_time = create_event('IFU Insertion Check', 'Packaging', current_time,
                    current_time + timedelta(hours=random.uniform(0.5, 1)),
                    [batch_id, line])

        return current_time

    def _generate_qc_release(self, batch_id, start_time, conforming=True):
        """Generate QC sampling, result, and QP decision"""
        current_time = start_time

        # QC FP Sampling
        current_time += timedelta(hours=random.uniform(1, 4))
        qcs_id = generate_qc_sample_id()
        self.qc_samples.append(qcs_id)

        objects.append({'object_id': qcs_id, 'object_type': 'QCSample'})
        object_attributes.append({
            'object_id': qcs_id,
            'sample_type': 'FP',
            'lab_id': random.choice(['LAB1', 'LAB2', 'LAB3'])
        })

        _, current_time = create_event('QC FP Sampling', 'QC_Lab', current_time,
                    current_time + timedelta(hours=random.uniform(0.5, 2)),
                    [batch_id, qcs_id])

        # QC Result
        current_time += timedelta(hours=random.uniform(4, 48))
        result_activity = 'QC Result (Conforming)' if conforming else 'QC Result (OOS)'
        _, current_time = create_event(result_activity, 'QC_Lab', current_time,
                    current_time + timedelta(hours=random.uniform(0.5, 4)),
                    [batch_id, qcs_id])

        # QP Decision
        current_time += timedelta(hours=random.uniform(1, 24))
        decision = 'QP Decision (Release)' if conforming else 'QP Decision (Reject)'
        create_event(decision, 'QA', current_time,
                    current_time + timedelta(hours=random.uniform(0.5, 2)),
                    [batch_id])

    def _generate_deviation_rework(self, batch_id, dosage, line, start_time):
        """Scenario: Deviation after major unit with rework and IPC"""
        current_time = start_time

        # Standard start
        current_time = self._run_standard_start(batch_id, dosage, line, current_time)

        # Run partial backbone until compression/filling
        if dosage in ['Tablet', 'Capsule']:
            # Compression
            current_time += timedelta(hours=random.uniform(0.5, 2))
            comp_equip = get_equipment_for_line(line, 'COMP' if dosage == 'Tablet' else 'FILL')
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(3, 8))
            create_event('Start Compression', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, comp_equip])
            _, current_time = create_event('End Compression', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, comp_equip])

            # Deviation after compression
            current_time += timedelta(hours=1)
            dev_id = self._create_deviation('Process', 'Major')
            _, current_time = create_event('Deviation Opened', 'QA', current_time,
                        current_time + timedelta(hours=1),
                        [batch_id, dev_id, comp_equip])

            # Investigation
            current_time += timedelta(hours=random.uniform(2, 8))
            _, current_time = create_event('Investigation', 'QA', current_time,
                        current_time + timedelta(hours=random.uniform(4, 24)),
                        [batch_id, dev_id])

            # IPC Sampling
            current_time += timedelta(hours=1)
            qcs_id = generate_qc_sample_id()
            self.qc_samples.append(qcs_id)
            objects.append({'object_id': qcs_id, 'object_type': 'QCSample'})
            object_attributes.append({
                'object_id': qcs_id,
                'sample_type': 'IPC',
                'lab_id': random.choice(['LAB1', 'LAB2', 'LAB3'])
            })
            _, current_time = create_event('QC IPC Sampling', 'QC_Lab', current_time,
                        current_time + timedelta(hours=1),
                        [batch_id, qcs_id])

            # Rework
            current_time += timedelta(hours=random.uniform(2, 8))
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
            create_event('Start Rework', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, comp_equip])
            _, current_time = create_event('End Rework', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, comp_equip])

            # Deviation closure
            current_time += timedelta(hours=random.uniform(1, 4))
            _, current_time = create_event('Deviation Closed', 'QA', current_time,
                        current_time + timedelta(hours=1),
                        [batch_id, dev_id])

            # Continue with coating and packaging
            current_time = self._run_coating_packaging(batch_id, line, current_time, dosage)
        else:
            # For other dosage forms, run full backbone
            if dosage == 'Injectable':
                current_time = self._generate_injectable_backbone(batch_id, line, current_time)
            elif dosage == 'Hormonal':
                current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
            elif dosage == 'Device':
                current_time = self._generate_device_backbone(batch_id, line, current_time)

        self._generate_qc_release(batch_id, current_time, conforming=True)

    def _generate_downtime(self, batch_id, dosage, line, start_time):
        """Scenario: Machine downtime during operation"""
        current_time = start_time
        current_time = self._run_standard_start(batch_id, dosage, line, current_time)

        if dosage in ['Tablet', 'Capsule']:
            # Start compression
            current_time += timedelta(hours=random.uniform(0.5, 2))
            comp_equip = get_equipment_for_line(line, 'COMP' if dosage == 'Tablet' else 'FILL')
            start_dt = current_time
            create_event('Start Compression', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, comp_equip])

            # Downtime during compression
            downtime_start = start_dt + timedelta(hours=random.uniform(1, 3))
            downtime_end = downtime_start + timedelta(hours=random.uniform(2, 6))
            create_event('Equipment Downtime', 'Maintenance', downtime_start, downtime_end,
                        [comp_equip, line, batch_id])

            # End compression (delayed)
            end_dt = downtime_end + timedelta(hours=random.uniform(2, 4))
            _, current_time = create_event('End Compression', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, comp_equip])

            # Continue normally
            current_time = self._run_coating_packaging(batch_id, line, current_time, dosage)
        else:
            # For other dosage forms, run full backbone
            if dosage == 'Injectable':
                current_time = self._generate_injectable_backbone(batch_id, line, current_time)
            elif dosage == 'Hormonal':
                current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
            elif dosage == 'Device':
                current_time = self._generate_device_backbone(batch_id, line, current_time)

        self._generate_qc_release(batch_id, current_time, conforming=True)

    def _generate_early_cancel(self, batch_id, dosage, line, start_time):
        """Scenario: Early cancellation after staging"""
        current_time = start_time

        # Planning
        mo_id = random.choice(self.market_orders)
        _, current_time = create_event('Plan Batch', 'Planning', current_time,
                    current_time + timedelta(hours=random.uniform(0.25, 2)),
                    [batch_id, mo_id])

        # Release
        current_time += timedelta(hours=random.uniform(1, 8))
        _, current_time = create_event('Release Batch', 'Planning', current_time,
                    current_time + timedelta(hours=random.uniform(0.25, 1)),
                    [batch_id])

        # Stage Materials
        current_time += timedelta(hours=random.uniform(0.5, 4))
        mat_lots = random.sample(self.material_lots, random.randint(2, 5))
        _, current_time = create_event(
            'Stage Materials' if dosage != 'Device' else 'Stage Components',
            'Warehouse', current_time,
            current_time + timedelta(hours=random.uniform(1, 6)),
            [batch_id, line] + mat_lots
        )

        # Cancellation
        current_time += timedelta(hours=random.uniform(1, 24))
        create_event('Batch Cancelled (Material Issue)', 'Planning', current_time,
                    current_time + timedelta(hours=0.5),
                    [batch_id])

    def _generate_oos_reject(self, batch_id, dosage, line, start_time):
        """Scenario: QC OOS leading to rejection"""
        current_time = start_time
        current_time = self._run_standard_start(batch_id, dosage, line, current_time)

        # Run full backbone
        if dosage in ['Tablet', 'Capsule']:
            current_time = self._generate_solids_backbone(batch_id, line, current_time, dosage)
        elif dosage == 'Injectable':
            current_time = self._generate_injectable_backbone(batch_id, line, current_time)
        elif dosage == 'Hormonal':
            current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
        elif dosage == 'Device':
            current_time = self._generate_device_backbone(batch_id, line, current_time)

        # QC with OOS result
        self._generate_qc_release(batch_id, current_time, conforming=False)

    def _generate_complex(self, batch_id, dosage, line, start_time):
        """Scenario: Combined downtime + deviation + extended QA"""
        current_time = start_time
        current_time = self._run_standard_start(batch_id, dosage, line, current_time)

        if dosage in ['Tablet', 'Capsule']:
            # Start compression with downtime
            current_time += timedelta(hours=random.uniform(0.5, 2))
            comp_equip = get_equipment_for_line(line, 'COMP' if dosage == 'Tablet' else 'FILL')
            start_dt = current_time
            create_event('Start Compression', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, comp_equip])

            # Downtime
            downtime_start = start_dt + timedelta(hours=random.uniform(1, 2))
            downtime_end = downtime_start + timedelta(hours=random.uniform(2, 4))
            create_event('Equipment Downtime', 'Maintenance', downtime_start, downtime_end,
                        [comp_equip, line, batch_id])

            # End compression
            end_dt = downtime_end + timedelta(hours=random.uniform(2, 4))
            _, current_time = create_event('End Compression', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, comp_equip])

            # Deviation
            current_time += timedelta(hours=1)
            dev_id = self._create_deviation('Quality', 'Critical')
            _, current_time = create_event('Deviation Opened', 'QA', current_time,
                        current_time + timedelta(hours=1),
                        [batch_id, dev_id, comp_equip])

            _, current_time = create_event('Investigation', 'QA', current_time,
                        current_time + timedelta(hours=random.uniform(8, 24)),
                        [batch_id, dev_id])

            # Extended QA Review
            _, current_time = create_event('Extended QA Review', 'QA', current_time,
                        current_time + timedelta(hours=random.uniform(12, 48)),
                        [batch_id, dev_id])

            _, current_time = create_event('Deviation Closed', 'QA', current_time,
                        current_time + timedelta(hours=2),
                        [batch_id, dev_id])

            # Continue
            current_time = self._run_coating_packaging(batch_id, line, current_time, dosage)
        else:
            # For other dosage forms, run full backbone
            if dosage == 'Injectable':
                current_time = self._generate_injectable_backbone(batch_id, line, current_time)
            elif dosage == 'Hormonal':
                current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
            elif dosage == 'Device':
                current_time = self._generate_device_backbone(batch_id, line, current_time)

        self._generate_qc_release(batch_id, current_time, conforming=True)

    def _generate_material_substitution(self, batch_id, dosage, line, start_time):
        """Scenario A: Material lot substitution mid-flow"""
        current_time = start_time

        # Standard start with initial materials
        mo_id = random.choice(self.market_orders) if random.random() < 0.7 else None
        plan_objs = [batch_id, mo_id] if mo_id else [batch_id]
        _, current_time = create_event('Plan Batch', 'Planning', current_time,
                    current_time + timedelta(hours=random.uniform(0.25, 2)), plan_objs)

        current_time += timedelta(hours=random.uniform(1, 8))
        _, current_time = create_event('Release Batch', 'Planning', current_time,
                    current_time + timedelta(hours=random.uniform(0.25, 1)), [batch_id])

        # Stage initial materials
        current_time += timedelta(hours=random.uniform(0.5, 4))
        mat_lots_initial = random.sample(self.material_lots, random.randint(2, 4))
        _, current_time = create_event(
            'Stage Materials' if dosage != 'Device' else 'Stage Components',
            'Warehouse', current_time, current_time + timedelta(hours=random.uniform(1, 6)),
            [batch_id, line] + mat_lots_initial
        )

        # Start first operation
        if dosage in ['Tablet', 'Capsule']:
            current_time += timedelta(hours=random.uniform(0.5, 2))
            comp_equip = get_equipment_for_line(line, 'COMP' if dosage == 'Tablet' else 'FILL')
            start_dt = current_time
            create_event('Start Compression', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, comp_equip])

            # Discover material issue mid-operation
            issue_time = start_dt + timedelta(hours=random.uniform(1, 2))
            dev_id = self._create_deviation('Supply', 'Major')
            _, issue_time = create_event('Deviation Opened', 'QA', issue_time,
                        issue_time + timedelta(hours=0.5),
                        [batch_id, dev_id] + [mat_lots_initial[0]])

            # Investigation
            _, current_time = create_event('Investigation', 'QA', issue_time,
                        issue_time + timedelta(hours=random.uniform(2, 6)),
                        [batch_id, dev_id])

            # Stage substitute material
            mat_lot_sub = random.choice([m for m in self.material_lots if m not in mat_lots_initial])
            _, current_time = create_event('Stage Materials', 'Warehouse', current_time,
                        current_time + timedelta(hours=random.uniform(2, 4)),
                        [batch_id, line, mat_lot_sub])

            # Extra QA review
            _, current_time = create_event('Extended QA Review', 'QA', current_time,
                        current_time + timedelta(hours=random.uniform(4, 12)),
                        [batch_id, dev_id])

            _, current_time = create_event('Deviation Closed', 'QA', current_time,
                        current_time + timedelta(hours=1), [batch_id, dev_id])

            # End compression
            end_dt = current_time + timedelta(hours=random.uniform(2, 4))
            _, current_time = create_event('End Compression', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, comp_equip])

            current_time = self._run_coating_packaging(batch_id, line, current_time, dosage)
        else:
            # For other dosage forms, run full backbone
            if dosage == 'Injectable':
                current_time = self._generate_injectable_backbone(batch_id, line, current_time)
            elif dosage == 'Hormonal':
                current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
            elif dosage == 'Device':
                current_time = self._generate_device_backbone(batch_id, line, current_time)

        self._generate_qc_release(batch_id, current_time, conforming=True)

    def _generate_line_change(self, batch_id, dosage, line, start_time):
        """Scenario B: Line change between operations"""
        current_time = start_time
        current_time = self._run_standard_start(batch_id, dosage, line, current_time)

        if dosage in ['Tablet', 'Capsule']:
            # Compression on original line
            current_time += timedelta(hours=random.uniform(0.5, 2))
            comp_equip = get_equipment_for_line(line, 'COMP' if dosage == 'Tablet' else 'FILL')
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(3, 8))
            create_event('Start Compression', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, comp_equip])
            _, current_time = create_event('End Compression', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, comp_equip])

            # Switch to different line for coating/packaging
            product_info = PRODUCTS[[k for k, v in PRODUCTS.items() if v['dosage'] == dosage][0]]
            available_lines = product_info['lines']
            new_line = random.choice([l for l in available_lines if l != line])

            # Coating on new line
            current_time += timedelta(hours=random.uniform(2, 8))  # Transfer delay
            coat_equip = get_equipment_for_line(new_line, 'COAT')
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
            create_event('Start Coating', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, new_line, coat_equip])
            _, current_time = create_event('End Coating', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, new_line, coat_equip])

            # Packaging on new line
            current_time += timedelta(hours=random.uniform(0.5, 2))
            pack_equip = get_equipment_for_line(new_line, 'PACK')
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(3, 10))
            create_event('Start Packaging', 'Packaging', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, new_line, pack_equip])
            _, current_time = create_event('End Packaging', 'Packaging', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, new_line, pack_equip])
        else:
            # For other dosage forms, run full backbone
            if dosage == 'Injectable':
                current_time = self._generate_injectable_backbone(batch_id, line, current_time)
            elif dosage == 'Hormonal':
                current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
            elif dosage == 'Device':
                current_time = self._generate_device_backbone(batch_id, line, current_time)

        self._generate_qc_release(batch_id, current_time, conforming=True)

    def _generate_split_packaging(self, batch_id, dosage, line, start_time):
        """Scenario C: Split batch into two packaging runs"""
        current_time = start_time
        current_time = self._run_standard_start(batch_id, dosage, line, current_time)

        if dosage in ['Tablet', 'Capsule']:
            # Run through compression and coating
            current_time += timedelta(hours=random.uniform(0.5, 2))
            comp_equip = get_equipment_for_line(line, 'COMP' if dosage == 'Tablet' else 'FILL')
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(3, 8))
            create_event('Start Compression', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, comp_equip])
            _, current_time = create_event('End Compression', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, comp_equip])

            current_time += timedelta(hours=random.uniform(0.5, 2))
            coat_equip = get_equipment_for_line(line, 'COAT')
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
            create_event('Start Coating', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, coat_equip])
            _, current_time = create_event('End Coating', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, coat_equip])

            # First packaging run
            current_time += timedelta(hours=random.uniform(0.5, 2))
            pack_equip1 = get_equipment_for_line(line, 'PACK')
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(3, 6))
            create_event('Start Packaging', 'Packaging', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, pack_equip1])
            _, current_time = create_event('End Packaging', 'Packaging', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, pack_equip1])

            # Second packaging run (possibly different equipment or line)
            current_time += timedelta(hours=random.uniform(1, 4))
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(3, 6))
            create_event('Start Packaging', 'Packaging', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, pack_equip1])
            _, current_time = create_event('End Packaging', 'Packaging', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, pack_equip1])
        else:
            # For other dosage forms, run full backbone
            if dosage == 'Injectable':
                current_time = self._generate_injectable_backbone(batch_id, line, current_time)
            elif dosage == 'Hormonal':
                current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
            elif dosage == 'Device':
                current_time = self._generate_device_backbone(batch_id, line, current_time)

        self._generate_qc_release(batch_id, current_time, conforming=True)

    def _generate_retest_loop(self, batch_id, dosage, line, start_time):
        """Scenario D: Re-test loop in QC"""
        current_time = start_time
        current_time = self._run_standard_start(batch_id, dosage, line, current_time)

        # Run full backbone
        if dosage in ['Tablet', 'Capsule']:
            current_time = self._generate_solids_backbone(batch_id, line, current_time, dosage)
        elif dosage == 'Injectable':
            current_time = self._generate_injectable_backbone(batch_id, line, current_time)
        elif dosage == 'Hormonal':
            current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
        elif dosage == 'Device':
            current_time = self._generate_device_backbone(batch_id, line, current_time)

        # First QC sample - OOS
        current_time += timedelta(hours=random.uniform(1, 4))
        qcs_id1 = generate_qc_sample_id()
        self.qc_samples.append(qcs_id1)
        objects.append({'object_id': qcs_id1, 'object_type': 'QCSample'})
        object_attributes.append({
            'object_id': qcs_id1,
            'sample_type': 'FP',
            'lab_id': random.choice(['LAB1', 'LAB2', 'LAB3'])
        })
        _, current_time = create_event('QC FP Sampling', 'QC_Lab', current_time,
                    current_time + timedelta(hours=random.uniform(0.5, 2)),
                    [batch_id, qcs_id1])

        current_time += timedelta(hours=random.uniform(4, 24))
        _, current_time = create_event('QC Result (OOS)', 'QC_Lab', current_time,
                    current_time + timedelta(hours=random.uniform(0.5, 4)),
                    [batch_id, qcs_id1])

        # Investigation
        current_time += timedelta(hours=random.uniform(2, 8))
        dev_id = self._create_deviation('Quality', 'Major')
        _, current_time = create_event('Deviation Opened', 'QA', current_time,
                    current_time + timedelta(hours=1),
                    [batch_id, dev_id])

        _, current_time = create_event('Investigation', 'QA', current_time,
                    current_time + timedelta(hours=random.uniform(8, 24)),
                    [batch_id, dev_id])

        # Re-test with new sample
        current_time += timedelta(hours=random.uniform(2, 8))
        qcs_id2 = generate_qc_sample_id()
        self.qc_samples.append(qcs_id2)
        objects.append({'object_id': qcs_id2, 'object_type': 'QCSample'})
        object_attributes.append({
            'object_id': qcs_id2,
            'sample_type': 'FP',
            'lab_id': random.choice(['LAB1', 'LAB2', 'LAB3'])
        })
        _, current_time = create_event('QC FP Sampling', 'QC_Lab', current_time,
                    current_time + timedelta(hours=random.uniform(0.5, 2)),
                    [batch_id, qcs_id2])

        # Decide: recover or reject
        recover = random.random() < 0.7
        current_time += timedelta(hours=random.uniform(4, 24))
        result_activity = 'QC Result (Conforming)' if recover else 'QC Result (OOS)'
        _, current_time = create_event(result_activity, 'QC_Lab', current_time,
                    current_time + timedelta(hours=random.uniform(0.5, 4)),
                    [batch_id, qcs_id2])

        # Close deviation
        _, current_time = create_event('Deviation Closed', 'QA', current_time,
                    current_time + timedelta(hours=2),
                    [batch_id, dev_id])

        # Final QP Decision
        current_time += timedelta(hours=random.uniform(1, 24))
        decision = 'QP Decision (Release)' if recover else 'QP Decision (Reject)'
        create_event(decision, 'QA', current_time,
                    current_time + timedelta(hours=random.uniform(0.5, 2)),
                    [batch_id])

    def _generate_doc_deviation(self, batch_id, dosage, line, start_time):
        """Scenario E: Documentation deviation after packaging"""
        current_time = start_time
        current_time = self._run_standard_start(batch_id, dosage, line, current_time)

        # Run full backbone
        if dosage in ['Tablet', 'Capsule']:
            current_time = self._generate_solids_backbone(batch_id, line, current_time, dosage)
        elif dosage == 'Injectable':
            current_time = self._generate_injectable_backbone(batch_id, line, current_time)
        elif dosage == 'Hormonal':
            current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
        elif dosage == 'Device':
            current_time = self._generate_device_backbone(batch_id, line, current_time)

        # Documentation deviation (no physical rework)
        current_time += timedelta(hours=random.uniform(1, 4))
        dev_id = self._create_deviation('Documentation', 'Minor')
        _, current_time = create_event('Deviation Opened', 'QA', current_time,
                    current_time + timedelta(hours=0.5),
                    [batch_id, dev_id])

        _, current_time = create_event('Investigation', 'QA', current_time,
                    current_time + timedelta(hours=random.uniform(2, 8)),
                    [batch_id, dev_id])

        _, current_time = create_event('Extended QA Review', 'QA', current_time,
                    current_time + timedelta(hours=random.uniform(4, 12)),
                    [batch_id, dev_id])

        _, current_time = create_event('Deviation Closed', 'QA', current_time,
                    current_time + timedelta(hours=1),
                    [batch_id, dev_id])

        # Normal QC and release
        self._generate_qc_release(batch_id, current_time, conforming=True)

    def _generate_preventive_maintenance(self, batch_id, dosage, line, start_time):
        """Scenario F: Preventive maintenance causing queueing"""
        current_time = start_time
        current_time = self._run_standard_start(batch_id, dosage, line, current_time)

        if dosage in ['Tablet', 'Capsule']:
            # Queue before compression due to PM
            comp_equip = get_equipment_for_line(line, 'COMP' if dosage == 'Tablet' else 'FILL')

            # Preventive maintenance window
            pm_start = current_time + timedelta(hours=random.uniform(1, 4))
            pm_end = pm_start + timedelta(hours=random.uniform(4, 8))
            create_event('Preventive Maintenance', 'Maintenance', pm_start, pm_end,
                        [comp_equip, line])

            # Batch waits for PM to complete
            current_time = pm_end + timedelta(hours=random.uniform(0.5, 2))

            # Now run compression
            start_dt = current_time
            end_dt = start_dt + timedelta(hours=random.uniform(3, 8))
            create_event('Start Compression', 'Production', start_dt, start_dt + timedelta(minutes=5),
                        [batch_id, line, comp_equip])
            _, current_time = create_event('End Compression', 'Production', end_dt - timedelta(minutes=5), end_dt,
                        [batch_id, line, comp_equip])

            # Continue normally
            current_time = self._run_coating_packaging(batch_id, line, current_time, dosage)
        else:
            # For other dosage forms, run full backbone
            if dosage == 'Injectable':
                current_time = self._generate_injectable_backbone(batch_id, line, current_time)
            elif dosage == 'Hormonal':
                current_time = self._generate_hormonal_backbone(batch_id, line, current_time)
            elif dosage == 'Device':
                current_time = self._generate_device_backbone(batch_id, line, current_time)

        self._generate_qc_release(batch_id, current_time, conforming=True)

    def _run_standard_start(self, batch_id, dosage, line, start_time):
        """Run standard start: Plan, Release, Stage"""
        current_time = start_time

        # Planning
        mo_id = random.choice(self.market_orders) if random.random() < 0.7 else None
        plan_objs = [batch_id, mo_id] if mo_id else [batch_id]
        _, current_time = create_event('Plan Batch', 'Planning', current_time,
                    current_time + timedelta(hours=random.uniform(0.25, 2)),
                    plan_objs)

        # Release
        current_time += timedelta(hours=random.uniform(1, 8))
        _, current_time = create_event('Release Batch', 'Planning', current_time,
                    current_time + timedelta(hours=random.uniform(0.25, 1)),
                    [batch_id])

        # Stage Materials
        current_time += timedelta(hours=random.uniform(0.5, 4))
        mat_lots = random.sample(self.material_lots, random.randint(2, 5))
        _, current_time = create_event(
            'Stage Materials' if dosage != 'Device' else 'Stage Components',
            'Warehouse', current_time,
            current_time + timedelta(hours=random.uniform(1, 6)),
            [batch_id, line] + mat_lots
        )

        return current_time

    def _run_coating_packaging(self, batch_id, line, start_time, dosage):
        """Run coating and packaging"""
        current_time = start_time

        # Coating
        current_time += timedelta(hours=random.uniform(0.5, 2))
        coat_equip = get_equipment_for_line(line, 'COAT')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(2, 6))
        create_event('Start Coating', 'Production', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, coat_equip])
        _, current_time = create_event('End Coating', 'Production', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, coat_equip])

        # Packaging
        current_time += timedelta(hours=random.uniform(0.5, 2))
        pack_equip = get_equipment_for_line(line, 'PACK')
        start_dt = current_time
        end_dt = start_dt + timedelta(hours=random.uniform(3, 10))
        create_event('Start Packaging', 'Packaging', start_dt, start_dt + timedelta(minutes=5),
                    [batch_id, line, pack_equip])
        _, current_time = create_event('End Packaging', 'Packaging', end_dt - timedelta(minutes=5), end_dt,
                    [batch_id, line, pack_equip])

        return current_time

    def _create_deviation(self, dev_type, criticality):
        """Create a deviation object and return its ID"""
        dev_id = generate_deviation_id()
        self.deviations.append(dev_id)

        objects.append({'object_id': dev_id, 'object_type': 'Deviation'})
        object_attributes.append({
            'object_id': dev_id,
            'deviation_type': dev_type,
            'criticality': criticality
        })

        return dev_id


def generate_batches(batch_gen, num_batches):
    """Generate batches with scenario distribution"""
    # Scenario distribution
    scenarios = [
        ('happy_path', 0.40),  # 40%
        ('deviation_rework', 0.10),
        ('downtime', 0.08),
        ('early_cancel', 0.05),
        ('oos_reject', 0.05),
        ('complex', 0.04),
        ('material_substitution', 0.07),
        ('line_change', 0.06),
        ('split_packaging', 0.05),
        ('retest_loop', 0.05),
        ('doc_deviation', 0.03),
        ('preventive_maintenance', 0.02),
    ]

    # Create scenario list based on distribution
    scenario_list = []
    for scenario, prob in scenarios:
        count = int(num_batches * prob)
        scenario_list.extend([scenario] * count)

    # Fill remaining with happy path
    while len(scenario_list) < num_batches:
        scenario_list.append('happy_path')

    random.shuffle(scenario_list)

    # Generate batches
    batch_ids = []
    current_date = START_DATE

    for i in range(num_batches):
        # Select product
        product_code = random.choice(list(PRODUCTS.keys()))
        scenario = scenario_list[i]

        # Generate batch
        batch_id = batch_gen.generate_batch(product_code, current_date, scenario)
        batch_ids.append(batch_id)

        # Advance time
        current_date += timedelta(hours=random.uniform(12, 72))

        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/{num_batches} batches...")

    return batch_ids


def validate_integrity():
    """Validate Module 9 integrity constraints"""
    print("\n=== INTEGRITY VALIDATION ===\n")

    errors = []

    # Build event lookup
    event_dict = {e['event_id']: e for e in events}

    # Build event-object mappings
    event_to_objects = defaultdict(list)
    object_to_events = defaultdict(list)
    for eo in event_objects:
        event_to_objects[eo['event_id']].append(eo['object_id'])
        object_to_events[eo['object_id']].append(eo['event_id'])

    # 1. Start/End Pairing
    print("1. Checking Start/End pairing...")
    batch_events = defaultdict(list)
    for e in events:
        if e['event_id'] in event_to_objects:
            for obj_id in event_to_objects[e['event_id']]:
                obj_type = next((o['object_type'] for o in objects if o['object_id'] == obj_id), None)
                if obj_type == 'Batch':
                    batch_events[obj_id].append(e)

    for batch_id, evts in batch_events.items():
        start_end_pairs = defaultdict(list)
        for e in evts:
            act = e['activity']
            if act.startswith('Start '):
                key = act.replace('Start ', '')
                start_end_pairs[key].append(('start', e))
            elif act.startswith('End '):
                key = act.replace('End ', '')
                start_end_pairs[key].append(('end', e))

        for key, pairs in start_end_pairs.items():
            starts = [p[1] for p in pairs if p[0] == 'start']
            ends = [p[1] for p in pairs if p[0] == 'end']
            if len(starts) != len(ends):
                errors.append(f"Batch {batch_id}: Mismatched Start/End for '{key}' - {len(starts)} starts, {len(ends)} ends")
            elif len(starts) > 0:
                for s_evt, e_evt in zip(starts, ends):
                    s_time = datetime.fromisoformat(s_evt['event_end'])
                    e_time = datetime.fromisoformat(e_evt['event_start'])
                    if s_time > e_time:
                        errors.append(f"Batch {batch_id}: Start '{key}' ends after End starts")

    # 2. Cancellation Constraint
    print("2. Checking cancellation constraint...")
    for batch_id, evts in batch_events.items():
        has_cancel = any('Cancelled' in e['activity'] for e in evts)
        has_start_mfg = any(e['activity'].startswith('Start ') and
                           e['activity'] not in ['Start Packaging'] for e in evts)
        if has_cancel and has_start_mfg:
            errors.append(f"Batch {batch_id}: Has cancellation but also has Start_* manufacturing events")

    # 3. QC Decision Constraint
    print("3. Checking QC decision constraint...")
    for batch_id, evts in batch_events.items():
        qp_decisions = [e for e in evts if 'QP Decision' in e['activity']]
        has_cancel = any('Cancelled' in e['activity'] for e in evts)

        if has_cancel:
            # Cancelled batches should have no QP Decision
            if len(qp_decisions) != 0:
                errors.append(f"Batch {batch_id}: Cancelled batch has {len(qp_decisions)} QP Decision events (expected 0)")
        else:
            # Non-cancelled batches must have exactly 1 QP Decision
            if len(qp_decisions) != 1:
                errors.append(f"Batch {batch_id}: Has {len(qp_decisions)} QP Decision events (expected 1)")

    # 4. QC Sample Linkage
    print("4. Checking QC sample linkage...")
    qc_result_events = [e for e in events if 'QC Result' in e['activity']]
    for e in qc_result_events:
        linked_objs = event_to_objects.get(e['event_id'], [])
        qcs_objs = [o for o in linked_objs if o.startswith('QCS')]
        if len(qcs_objs) == 0:
            errors.append(f"Event {e['event_id']} (QC Result) has no QCSample linked")

    # 5. Deviation Lifecycle
    print("5. Checking deviation lifecycle...")
    deviation_events = defaultdict(list)
    deviation_ids = {o['object_id'] for o in objects if o['object_type'] == 'Deviation'}
    for e in events:
        for obj_id in event_to_objects.get(e['event_id'], []):
            if obj_id in deviation_ids:
                deviation_events[obj_id].append(e['activity'])

    for dev_id, activities in deviation_events.items():
        has_opened = any('Opened' in a for a in activities)
        has_investigation = any('Investigation' in a for a in activities)
        has_closed = any('Closed' in a for a in activities)
        if not (has_opened and has_investigation and has_closed):
            errors.append(f"Deviation {dev_id}: Missing lifecycle events (Opened={has_opened}, Investigation={has_investigation}, Closed={has_closed})")

    # 6. No Orphan Objects
    print("6. Checking for orphan objects...")
    for obj in objects:
        obj_id = obj['object_id']
        obj_type = obj['object_type']
        # Allow static objects and inventory pools to have no events
        if obj_type in ['ProductionLine', 'MaterialLot', 'MarketOrder']:
            continue
        if obj_id not in object_to_events or len(object_to_events[obj_id]) == 0:
            errors.append(f"Object {obj_id} ({obj_type}) has no event linkages")

    # 7. No Orphan Events
    print("7. Checking for orphan events...")
    for e in events:
        if e['event_id'] not in event_to_objects or len(event_to_objects[e['event_id']]) == 0:
            errors.append(f"Event {e['event_id']} ({e['activity']}) has no object linkages")

    # Report
    if len(errors) == 0:
        print("\n✓ All integrity constraints PASSED\n")
    else:
        print(f"\n✗ Found {len(errors)} integrity violations:\n")
        for err in errors[:20]:  # Show first 20
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
        print()

    return len(errors) == 0


def print_statistics():
    """Print object and event counts"""
    print("=== DATASET STATISTICS ===\n")

    object_counts = defaultdict(int)
    for obj in objects:
        object_counts[obj['object_type']] += 1

    print("Object Counts:")
    for obj_type, count in sorted(object_counts.items()):
        print(f"  {obj_type}: {count}")

    print(f"\nTotal Objects: {len(objects)}")
    print(f"Total Events: {len(events)}")
    print(f"Total Event-Object Links: {len(event_objects)}")

    area_counts = defaultdict(int)
    for e in events:
        area_counts[e['area']] += 1

    print("\nEvents by Area:")
    for area, count in sorted(area_counts.items()):
        print(f"  {area}: {count}")

    print()


def generate_case_centric_projection(num_cases=75):
    """Generate case-centric projection for a subset of batches"""
    print(f"Generating case-centric projection for {num_cases} batches...")

    # Get batch objects
    batch_objs = [o for o in objects if o['object_type'] == 'Batch']
    selected_batches = random.sample(batch_objs, min(num_cases, len(batch_objs)))
    selected_batch_ids = {b['object_id'] for b in selected_batches}

    # Build event-object mapping
    event_to_objects = defaultdict(list)
    for eo in event_objects:
        event_to_objects[eo['event_id']].append(eo['object_id'])

    # Collect events for selected batches
    case_events = []
    for e in events:
        linked_objs = event_to_objects.get(e['event_id'], [])
        batch_ids = [o for o in linked_objs if o in selected_batch_ids]

        if batch_ids:
            # Get line info
            line_objs = [o for o in linked_objs if o in LINE_TO_PLANT]
            line = line_objs[0] if line_objs else ''

            for batch_id in batch_ids:
                case_events.append({
                    'case_id': batch_id,
                    'activity': e['activity'],
                    'event_start': e['event_start'],
                    'event_end': e['event_end'],
                    'timestamp': e['event_timestamp'],
                    'line': line,
                    'area': e['area']
                })

    # Sort by case_id and timestamp
    case_events.sort(key=lambda x: (x['case_id'], x['event_start']))

    # Get batch attributes
    batch_attr_dict = {}
    for oa in object_attributes:
        obj_type = next((o['object_type'] for o in objects if o['object_id'] == oa['object_id']), None)
        if obj_type == 'Batch' and oa['object_id'] in selected_batch_ids:
            batch_attr_dict[oa['object_id']] = oa

    case_attributes = []
    for batch_id in selected_batch_ids:
        if batch_id in batch_attr_dict:
            case_attributes.append(batch_attr_dict[batch_id])

    return case_events, case_attributes


def write_csv_files():
    """Write all CSV files"""
    print("Writing CSV files...")

    # ocel_events.csv
    with open('ocel_events.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['event_id', 'activity', 'area', 'event_start', 'event_end', 'event_timestamp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)

    # ocel_objects.csv
    with open('ocel_objects.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['object_id', 'object_type']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(objects)

    # ocel_event_objects.csv
    with open('ocel_event_objects.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['event_id', 'object_id']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(event_objects)

    # ocel_object_attributes.csv
    if object_attributes:
        with open('ocel_object_attributes.csv', 'w', newline='', encoding='utf-8') as f:
            all_keys = set()
            for oa in object_attributes:
                all_keys.update(oa.keys())
            fieldnames = sorted(all_keys)
            if 'object_id' in fieldnames:
                fieldnames.remove('object_id')
                fieldnames = ['object_id'] + fieldnames

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(object_attributes)

    print("  - ocel_events.csv")
    print("  - ocel_objects.csv")
    print("  - ocel_event_objects.csv")
    print("  - ocel_object_attributes.csv")


def write_case_centric_files(case_events, case_attributes):
    """Write case-centric CSV files"""
    print("Writing case-centric projection files...")

    # case_centric_events_small.csv
    with open('case_centric_events_small.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['case_id', 'activity', 'event_start', 'event_end', 'timestamp', 'line', 'area']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(case_events)

    # case_centric_attributes_small.csv
    if case_attributes:
        with open('case_centric_attributes_small.csv', 'w', newline='', encoding='utf-8') as f:
            all_keys = set()
            for ca in case_attributes:
                all_keys.update(ca.keys())
            fieldnames = sorted(all_keys)
            if 'object_id' in fieldnames:
                fieldnames.remove('object_id')
                fieldnames = ['object_id'] + fieldnames

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(case_attributes)

    print("  - case_centric_events_small.csv")
    print("  - case_centric_attributes_small.csv")


def main():
    print("="*60)
    print("OCEL Pharma Manufacturing Generator")
    print("="*60)
    print()

    # Create static objects
    print("Creating static objects...")
    create_production_lines()
    equipment_list = create_equipment()
    material_lots = create_material_lots(4000)
    market_orders = create_market_orders(1500)

    print(f"  - ProductionLines: {len(LINE_TO_PLANT)}")
    print(f"  - Equipment: {len(equipment_list)}")
    print(f"  - MaterialLots: {len(material_lots)}")
    print(f"  - MarketOrders: {len(market_orders)}")
    print()

    # Generate batches
    print("Generating batches and events...")
    batch_gen = BatchGenerator(material_lots, market_orders, equipment_list)
    batch_ids = generate_batches(batch_gen, 1500)
    print(f"Generated {len(batch_ids)} batches")
    print()

    # Statistics
    print_statistics()

    # Validation
    valid = validate_integrity()

    # Write OCEL files
    write_csv_files()
    print()

    # Generate and write case-centric projection
    case_events, case_attributes = generate_case_centric_projection(75)
    write_case_centric_files(case_events, case_attributes)
    print()

    print("="*60)
    print("Generation Complete!")
    print("="*60)

    if not valid:
        print("\n⚠ WARNING: Integrity validation failed. Review errors above.")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
