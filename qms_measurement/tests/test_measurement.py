from odoo.tests.common import TransactionCase


class TestQmsMeasurement(TransactionCase):
    def test_due_date(self):
        equipment = self.env['qms.measurement.equipment'].create({'name': 'Pressure Gauge', 'calibration_interval': 365})
        equipment.last_calibration_date = '2026-01-01'
        self.assertEqual(str(equipment.next_due_date), '2027-01-01')

    def test_failed_calibration_places_equipment_out_of_service(self):
        equipment = self.env["qms.measurement.equipment"].create({"name": "Critical Gauge", "calibration_interval": 365})
        calibration = self.env["qms.measurement.calibration"].create({"equipment_id": equipment.id, "result": "fail", "as_found": "fail", "as_left": "fail"})
        calibration.action_validate()
        self.assertEqual(equipment.state, "out_of_service")

    def test_calibration_updates_last_date_on_pass(self):
        equipment = self.env["qms.measurement.equipment"].create({"name": "Gauge Pass", "calibration_interval": 365})
        calibration = self.env["qms.measurement.calibration"].create({"equipment_id": equipment.id, "result": "pass", "as_found": "pass", "as_left": "pass", "calibration_date": "2026-09-01"})
        calibration.action_validate()
        self.assertEqual(str(equipment.last_calibration_date), "2026-09-01")
        self.assertEqual(equipment.state, "active")
