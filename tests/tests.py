import unittest
from harvest.harvest import OAIChecker


class HarvestTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(HarvestTest, self).__init__(*args, **kwargs)
        self.request = OAIChecker("http://nashville.contentdm.oclc.org/oai/oai.php", "p15769coll18", "oai_qdc")

    def test_initialization(self):
        self.assertIsInstance(OAIChecker("http://nashville.contentdm.oclc.org/oai/oai.php"), OAIChecker)
        self.assertIsInstance(OAIChecker("http://nashville.contentdm.oclc.org/oai/oai.php", "test", "MODS"), OAIChecker)
