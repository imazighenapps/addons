# -*- coding: utf-8 -*-
import base64
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDocstore(TransactionCase):
    def _att(self, name, content, model=False, res_id=False):
        return self.env["ir.attachment"].create({
            "name": name, "raw": base64.b64encode(content),
            "mimetype": "text/plain",
            "res_model": model or False, "res_id": res_id or 0,
        })

    def test_01_duplicates_found(self):
        att_a = self._att("zz-a.txt", b"same-bytes-uniq")
        self._att("zz-b.txt", b"same-bytes-uniq")
        self._att("zz-c.txt", b"unique-bytes-zzz")
        scan = self.env["doc.storage.scan"].create({})
        scan.action_run()
        self.assertEqual(scan.state, "done")
        mine = scan.duplicate_ids.filtered(
            lambda d: att_a.id in d.attachment_ids.ids)
        self.assertEqual(len(mine), 1)
        self.assertEqual(mine.count, 2)
        self.assertEqual(mine.wasted_bytes, mine.file_size)

    def test_02_clean_keeps_newest(self):
        self._att("zz-a.txt", b"same-bytes-uniq")
        self._att("zz-b.txt", b"same-bytes-uniq")
        scan = self.env["doc.storage.scan"].create({})
        scan.action_run()
        mine = scan.duplicate_ids.filtered(
            lambda d: any(a.name == "zz-a.txt" for a in d.attachment_ids))
        self.assertEqual(len(mine), 1)
        mine.action_clean_keep_newest()
        self.assertEqual(mine.state, "kept")
        remaining = [a for a in mine.attachment_ids.exists()
                     if a.name in ("zz-a.txt", "zz-b.txt")]
        self.assertEqual(len(remaining), 1)

    def test_03_orphans_found(self):
        self._att("ghost.txt", b"data", model="res.partner", res_id=999999999)
        scan = self.env["doc.storage.scan"].create({})
        scan.action_run()
        orphans = scan.orphan_ids.filtered(
            lambda o: o.attachment_id.name == "ghost.txt")
        self.assertEqual(len(orphans), 1)
        ghost_id = orphans.attachment_id.id
        orphans.action_delete()
        self.assertEqual(orphans.state, "deleted")
        self.assertFalse(self.env["ir.attachment"].browse(ghost_id).exists())

    def test_04_min_size_filter(self):
        self._att("big.txt", b"x" * 5000)
        self._att("small.txt", b"y")
        scan = self.env["doc.storage.scan"].create({"min_size_kb": 1})
        scan.action_run()
        self.assertGreaterEqual(scan.total_files, 1)
