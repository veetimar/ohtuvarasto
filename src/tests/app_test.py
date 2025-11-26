import unittest
from app import app, manager


class TestApp(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        manager.warehouses.clear()
        manager.id_counter = 0

    def test_index_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Warehouse Manager", response.data)

    def test_create_warehouse(self):
        response = self.client.post(
            "/create",
            data={"name": "Test", "capacity": "100", "initial_balance": "50"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(manager.warehouses), 1)
        wh = manager.warehouses[1]
        self.assertEqual(wh["name"], "Test")
        self.assertAlmostEqual(wh["varasto"].tilavuus, 100)
        self.assertAlmostEqual(wh["varasto"].saldo, 50)

    def test_create_warehouse_empty_name(self):
        self.client.post(
            "/create",
            data={"name": "", "capacity": "100", "initial_balance": "0"}
        )
        self.assertEqual(len(manager.warehouses), 0)

    def test_delete_warehouse(self):
        self.client.post(
            "/create",
            data={"name": "Test", "capacity": "100", "initial_balance": "0"}
        )
        self.assertEqual(len(manager.warehouses), 1)
        response = self.client.post("/delete/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(manager.warehouses), 0)

    def test_add_to_warehouse(self):
        self.client.post(
            "/create",
            data={"name": "Test", "capacity": "100", "initial_balance": "0"}
        )
        self.client.post("/add/1", data={"amount": "25"})
        self.assertAlmostEqual(manager.warehouses[1]["varasto"].saldo, 25)

    def test_remove_from_warehouse(self):
        self.client.post(
            "/create",
            data={"name": "Test", "capacity": "100", "initial_balance": "50"}
        )
        self.client.post("/remove/1", data={"amount": "20"})
        self.assertAlmostEqual(manager.warehouses[1]["varasto"].saldo, 30)

    def test_invalid_capacity_value(self):
        self.client.post(
            "/create",
            data={"name": "Test", "capacity": "invalid", "initial_balance": "0"}
        )
        self.assertEqual(len(manager.warehouses), 0)

    def test_add_to_nonexistent_warehouse(self):
        response = self.client.post("/add/999", data={"amount": "10"})
        self.assertEqual(response.status_code, 302)

    def test_remove_from_nonexistent_warehouse(self):
        response = self.client.post("/remove/999", data={"amount": "10"})
        self.assertEqual(response.status_code, 302)

    def test_delete_nonexistent_warehouse(self):
        response = self.client.post("/delete/999")
        self.assertEqual(response.status_code, 302)
