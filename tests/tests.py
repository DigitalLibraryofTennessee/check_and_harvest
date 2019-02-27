import unittest
from dltnchecker.harvest import OAIChecker, XOAITester, MODSTester, DCTester, QDCTester
from tests.test_data import xoai_bad_records, xoai_good_records, mods_bad_records, dc_bad_records, qdc_bad_records, \
    qdc_good_records


class HarvestTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(HarvestTest, self).__init__(*args, **kwargs)
        self.request = OAIChecker("http://nashville.contentdm.oclc.org/oai/oai.php", "p15769coll18", "oai_qdc")

    def test_initialization(self):
        self.assertIsInstance(OAIChecker("http://nashville.contentdm.oclc.org/oai/oai.php"), OAIChecker)
        self.assertIsInstance(OAIChecker("http://nashville.contentdm.oclc.org/oai/oai.php", "test", "MODS"), OAIChecker)


class TestMetadataTesters(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestMetadataTesters, self).__init__(*args, **kwargs)

    def test_bad_xoai_records(self):
        for record in xoai_bad_records:
            self.assertFalse(XOAITester(record).is_good)

    def test_good_xoai_records(self):
        for record in xoai_good_records:
            self.assertTrue(XOAITester(record).is_good)

    def test_bad_mods_records(self):
        for record in mods_bad_records:
            self.assertFalse(MODSTester(record).is_good)

    def test_bad_dc_records(self):
        for record in dc_bad_records:
            self.assertFalse(DCTester('oai_dc:dc', record).is_good)

    def test_bad_qdc_records(self):
        for record in qdc_bad_records:
            self.assertFalse(QDCTester('oai_qdc:qualifieddc', record).is_good)

    def test_good_qdc_records(self):
        for record in qdc_good_records:
            self.assertTrue(QDCTester('oai_qdc:qualifieddc', record).is_good)
