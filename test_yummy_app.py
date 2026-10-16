import unittest
from unittest.mock import patch
from yummy_app import YummyApp
import gps_service


# ================================================================
# CAP DO 1: Bo test co ban cho san (Moi chi dat ~35% Coverage)
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)

    def test_calculate_total_with_item_not_in_menu(self):
        cart = {"tra_sua": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ================================================================
# CAP DO 2 (TIET 3): SINH VIEN TU TAY LAP TRINH TEST CASE DUOI DAY
# (Sau khi da hoan thanh Bang thiet ke test case viet tay tren giay)
# ================================================================
class TestMediumLevel(unittest.TestCase):
    """Kiem thu chuc nang kiem tra va ap dung ma khuyen mai (apply_promo_code)"""

    def setUp(self):
        self.app = YummyApp()

    def test_apply_promo_code_online_valid(self):
        """Kich ban 1: Online hop le - Ma GIAM10 giam 10%"""
        app = YummyApp(network_status="online", os_version=15)
        total = 100000.0
        result = app.apply_promo_code(total, "GIAM10")
        self.assertAlmostEqual(result, 90000.0)

    def test_apply_promo_code_offline_raises_connection_error(self):
        """Kich ban 2: Offline nem ConnectionError"""
        app = YummyApp(network_status="offline", os_version=15)
        with self.assertRaises(ConnectionError) as context:
            app.apply_promo_code(100000.0, "GIAM10")
        self.assertIn("Khong co ket noi mang de xac thuc ma.", str(context.exception))

    def test_apply_promo_code_special_code_valid_os15(self):
        """Kich ban 3: Ma dac biet NEW_OS_ONLY tren OS 15 thanh cong (giam 20%)"""
        app = YummyApp(network_status="online", os_version=15)
        total = 100000.0
        result = app.apply_promo_code(total, "NEW_OS_ONLY")
        self.assertAlmostEqual(result, 80000.0)

    def test_apply_promo_code_special_code_invalid_os14_raises_value_error(self):
        """Kich ban 4: Ma dac biet tren OS 14 (< min_os_version=15) nem ValueError"""
        app = YummyApp(network_status="online", os_version=14)
        with self.assertRaises(ValueError) as context:
            app.apply_promo_code(100000.0, "NEW_OS_ONLY")
        self.assertIn("Ma nay yeu cau HDH phien ban 15 tro len.", str(context.exception))

    def test_apply_promo_code_invalid_code_raises_value_error(self):
        """Kich ban bo sung: Ma khuyen mai khong ton tai trong he thong nem ValueError"""
        app = YummyApp(network_status="online", os_version=15)
        with self.assertRaises(ValueError) as context:
            app.apply_promo_code(100000.0, "MA_KHONG_TON_TAI")
        self.assertIn("Ma khuyen mai khong hop le.", str(context.exception))


class TestHardLevel(unittest.TestCase):
    """Kiem thu chuc nang goi GPS de xuat nha hang lan can (Mocking ngoai vi)"""

    def setUp(self):
        self.app = YummyApp()

    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_in_range(self, mock_gps):
        """Kich ban 1: Mock GPS trong vung (10.0, 105.0) tra ve danh sach nha hang"""
        mock_gps.return_value = (10.0, 105.0)
        expected = ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"]
        actual = self.app.get_nearby_restaurants()
        self.assertEqual(actual, expected)
        mock_gps.assert_called_once()

    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_out_of_range(self, mock_gps):
        """Kich ban 2: Mock GPS ngoai vung (20.0, 110.0) tra ve danh sach rong"""
        mock_gps.return_value = (20.0, 110.0)
        actual = self.app.get_nearby_restaurants()
        self.assertEqual(actual, [])
        mock_gps.assert_called_once()

    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_gps_signal_lost_raises_error(self, mock_gps):
        """Kich ban 3: Mock GPS nem ngoai le GPSSignalLostError tra ve thong bao loi than thien"""
        mock_gps.side_effect = gps_service.GPSSignalLostError()
        actual = self.app.get_nearby_restaurants()
        self.assertEqual(actual, "Khong the xac dinh vi tri.")
        mock_gps.assert_called_once()


if __name__ == "__main__":
    unittest.main()
