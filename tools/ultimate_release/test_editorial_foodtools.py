"""Check authored grocery/logging guides against retained source panels."""
import unittest
from editorial_foodtools import verify

class SourceReview(unittest.TestCase):
    def test_primary_panels_portions_and_arithmetic(self):
        result=verify()
        self.assertEqual(result['result'],'passed')
        self.assertEqual(result['new_authored_articles'],14)
        self.assertEqual(result['arithmetic_cases'],24)
        self.assertGreaterEqual(result['checks_passed'],170)

if __name__=='__main__':unittest.main(verbosity=2)
