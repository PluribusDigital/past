import unittest
from decimal import Decimal
from unittest.mock import patch
from api.endpoints.document_closest import distance

class TestDocumentClosest(unittest.TestCase):
    connArgs = {'database': 'pasp_development'}

    def setUp(self):
        self.v1 = {
            'locker': Decimal(11.5141),
            'micro': Decimal(8.6712),
            'truck': Decimal(7.2466),
            'door': Decimal(4.7606),
            'switch': Decimal(4.4076),
            'fastener': Decimal(3.9582),
            'stopper': Decimal(3.3115),
            'status': Decimal(3.3012),
            'lock': Decimal(3.1351),
            'security': Decimal(2.6488),
            'control': Decimal(2.3931),
            'rear': Decimal(2.0837),
            'flash': Decimal(1.9596),
            'unlock': Decimal(1.7395),
            'pivotally': Decimal(1.6889),
            'led': Decimal(1.6103),
            'checking': Decimal(1.4553),
            'structure': Decimal(1.2646),
            'period': Decimal(1.249),
            'mount': Decimal(1.2468) }

        self.v2 = {
            'member': Decimal(4.6507),
            'component': Decimal(4.4337),
            'direction': Decimal(4.2056),
            'joint': Decimal(4.1603),
            'fitting': Decimal(3.2561),
            'hole': Decimal(3.1894),
            'shank': Decimal(2.7808),
            'fastener': Decimal(2.5439),
            'insertion': Decimal(2.158),
            'flow': Decimal(2.1084),
            'channel': Decimal(1.9037),
            'mount': Decimal(1.864),
            'second': Decimal(1.8526),
            'join': Decimal(1.8173),
            'device': Decimal(1.6389),
            'construct': Decimal(1.5805),
            'relative': Decimal(1.5209),
            'mounting': Decimal(1.476),
            'open': Decimal(1.469),
            'surface': Decimal(1.3234) }

    # -------------------------------------------------------------------------
    # Test Methods
    # ------------------------------------------------------- ------------------

    def test_distancev1v2(self):
        result = distance(self.v1, self.v2)
        self.assertAlmostEqual(Decimal('0.96701061'), result)

    def test_distancev1v1(self):
        result = distance(self.v1, self.v1)
        self.assertEqual(0, result)

    def test_distanceInfinite(self):
        v3 = {'infinite': Decimal('inf')}
        result = distance(self.v1, v3)
        self.assertAlmostEqual(Decimal('1.0000637'), result)

    @unittest.skip('Used for debugging')
    @patch('api.endpoints.document_closest.DB')
    def test_get(self, mockDB):
        from cProfile import Profile
        from pstats import Stats
        from api import Server, app, DB

        mockDB.connection.return_value = DB.connection(**self.connArgs)

        pr = Profile()
        pr.enable()
        print("\n<<<---", self.id())

        target = app.test_client()
        url = Server.absoluteUrl('/document/8567/closest')

        rv = target.get(url)

        p = Stats(pr)
        p.strip_dirs()
        p.sort_stats ('tottime')
        p.print_stats ()
        print("\n--->>>")

        self.assertEqual(200, rv.status_code)

if __name__ == '__main__':
    unittest.main()
