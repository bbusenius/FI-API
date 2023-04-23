import unittest

from app import app


class Tests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def testHomepageRoute(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testJsonHomeRoute(self):
        response = self.client.get('/json', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def testBadRoute(self):
        response = self.client.get('/nada', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def testJSONEndpoint(self):
        with app.app_context():
            response1 = self.client.get(
                '/json/take_home_pay?gross_pay=5000&employer_match=1000&taxes_and_fees=3000'
            )
            self.assertEqual(response1.get_json(), '3000')

            response2 = self.client.get(
                '/json/take_home_pay?gross_pay=5000&employer_match=600&taxes_and_fees=2000,500,400'
            )
            self.assertEqual(response2.get_json(), '2700')


if __name__ == '__main__':
    unittest.main()
