#!/usr/bin/env python3
"""
Tests for Axperia Trading Bot - Following Strategy

These tests verify the correct behavior of the PnL calculations,
TP/SL validations, and the separation between price movement and margin return.
"""

import unittest
from _axperia_trading_following import (
    calcular_pnl_real,
    validar_take_profit,
    validar_stop_loss,
    LEVERAGE,
    MARGIN_RETURN_TP,
    MARGIN_RETURN_SL,
    TOTAL_FEES,
    FEE_RATE
)


class TestPnLCalculations(unittest.TestCase):
    """Test the PnL calculation functions"""
    
    def test_calcular_pnl_real_positive_movement(self):
        """Test PnL calculation with positive price movement"""
        entry_price = 100.0
        exit_price = 102.0  # 2% movement
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Price movement should be 2%
        self.assertAlmostEqual(pnl['price_movement_pct'], 2.0, places=2)
        
        # Leveraged return (before fees) should be 2% * 3 = 6%
        self.assertAlmostEqual(pnl['leveraged_return_pct'], 6.0, places=2)
        
        # Fees should be 1.2%
        self.assertAlmostEqual(pnl['fees_pct'], 1.2, places=2)
        
        # Margin return (after fees) should be 6% - 1.2% = 4.8%
        self.assertAlmostEqual(pnl['margin_return_pct'], 4.8, places=2)
    
    def test_calcular_pnl_real_negative_movement(self):
        """Test PnL calculation with negative price movement"""
        entry_price = 100.0
        exit_price = 98.0  # -2% movement
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Price movement should be -2%
        self.assertAlmostEqual(pnl['price_movement_pct'], -2.0, places=2)
        
        # Leveraged return (before fees) should be -2% * 3 = -6%
        self.assertAlmostEqual(pnl['leveraged_return_pct'], -6.0, places=2)
        
        # Margin return (after fees) should be -6% - 1.2% = -7.2%
        self.assertAlmostEqual(pnl['margin_return_pct'], -7.2, places=2)
    
    def test_calcular_pnl_real_example_from_problem(self):
        """Test with the real example from the problem statement"""
        entry_price = 16.5894
        exit_price = 16.7104
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Price movement should be approximately 0.729%
        self.assertAlmostEqual(pnl['price_movement_pct'], 0.729, places=2)
        
        # Leveraged return should be approximately 2.187%
        self.assertAlmostEqual(pnl['leveraged_return_pct'], 2.187, places=2)
        
        # Margin return should be approximately 0.987% (2.187% - 1.2%)
        # NOT 6.20% as incorrectly calculated before
        self.assertAlmostEqual(pnl['margin_return_pct'], 0.987, places=2)
    
    def test_calcular_pnl_real_zero_movement(self):
        """Test PnL calculation with no price movement"""
        entry_price = 100.0
        exit_price = 100.0
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Price movement should be 0%
        self.assertAlmostEqual(pnl['price_movement_pct'], 0.0, places=2)
        
        # Leveraged return should be 0%
        self.assertAlmostEqual(pnl['leveraged_return_pct'], 0.0, places=2)
        
        # Margin return should be -1.2% (only fees)
        self.assertAlmostEqual(pnl['margin_return_pct'], -1.2, places=2)
    
    def test_calcular_pnl_real_required_for_tp(self):
        """Test the price movement required to reach TP target"""
        # To achieve 5% margin return with 3x leverage:
        # We need: (5% + 1.2%) / 3 = 2.067% price movement
        entry_price = 100.0
        exit_price = 102.067
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Margin return should be approximately 5%
        self.assertAlmostEqual(pnl['margin_return_pct'], 5.0, places=1)


class TestTakeProfitValidation(unittest.TestCase):
    """Test the Take Profit validation logic"""
    
    def test_tp_not_reached(self):
        """Test TP validation when target is not reached"""
        entry_price = 100.0
        exit_price = 101.0  # 1% movement = 3% leveraged - 1.2% fees = 1.8%
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should not trigger TP (1.8% < 5%)
        self.assertFalse(validar_take_profit(pnl))
    
    def test_tp_exactly_reached(self):
        """Test TP validation when target is exactly reached"""
        entry_price = 100.0
        # Calculate exact price for 5% margin return
        # 5% + 1.2% = 6.2% leveraged return needed
        # 6.2% / 3 = 2.067% price movement
        exit_price = 102.067
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should trigger TP (~5%)
        self.assertTrue(validar_take_profit(pnl))
    
    def test_tp_exceeded(self):
        """Test TP validation when target is exceeded"""
        entry_price = 100.0
        exit_price = 103.0  # 3% movement = 9% leveraged - 1.2% fees = 7.8%
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should trigger TP (7.8% > 5%)
        self.assertTrue(validar_take_profit(pnl))
    
    def test_tp_with_real_example(self):
        """Test TP with the real example from problem statement"""
        entry_price = 16.5894
        exit_price = 16.7104
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should NOT trigger TP (~0.987% < 5%)
        self.assertFalse(validar_take_profit(pnl))


class TestStopLossValidation(unittest.TestCase):
    """Test the Stop Loss validation logic"""
    
    def test_sl_not_reached(self):
        """Test SL validation when not reached"""
        entry_price = 100.0
        exit_price = 99.5  # -0.5% movement = -1.5% leveraged - 1.2% fees = -2.7%
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should not trigger SL (-2.7% > -3%)
        self.assertFalse(validar_stop_loss(pnl))
    
    def test_sl_exactly_reached(self):
        """Test SL validation when exactly reached"""
        entry_price = 100.0
        # Calculate exact price for -3% margin return
        # margin_return = (price_movement × leverage) - fees
        # -3% = (price_movement × 3) - 1.2%
        # price_movement × 3 = -3% + 1.2% = -1.8%
        # price_movement = -1.8% / 3 = -0.6%
        # Using 99.39 to ensure we cross the threshold (accounting for floating point)
        exit_price = 99.39  # Slightly below -0.6% to ensure SL is triggered
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should trigger SL (margin return should be at or below -3%)
        self.assertTrue(validar_stop_loss(pnl))
        # Verify margin return is approximately -3%
        self.assertLessEqual(pnl['margin_return_pct'], -2.9)
    
    def test_sl_exceeded(self):
        """Test SL validation when exceeded"""
        entry_price = 100.0
        exit_price = 98.0  # -2% movement = -6% leveraged - 1.2% fees = -7.2%
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should trigger SL (-7.2% < -3%)
        self.assertTrue(validar_stop_loss(pnl))
    
    def test_sl_with_positive_return(self):
        """Test SL validation with positive returns"""
        entry_price = 100.0
        exit_price = 102.0  # Positive movement
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should not trigger SL (positive return)
        self.assertFalse(validar_stop_loss(pnl))


class TestLeverageAndFeesConsistency(unittest.TestCase):
    """Test the consistency of leverage and fee calculations"""
    
    def test_fee_calculation(self):
        """Test that fees are correctly calculated"""
        # Fees should be 0.6% per side, 1.2% total
        self.assertAlmostEqual(FEE_RATE, 0.006, places=4)
        self.assertAlmostEqual(TOTAL_FEES, 0.012, places=4)
    
    def test_leverage_multiplier(self):
        """Test that leverage correctly multiplies returns"""
        entry_price = 100.0
        exit_price = 101.0  # 1% movement
        
        pnl = calcular_pnl_real(entry_price, exit_price, leverage=LEVERAGE)
        
        # Leveraged return should be price_movement * leverage
        expected_leveraged = pnl['price_movement_pct'] * LEVERAGE
        self.assertAlmostEqual(pnl['leveraged_return_pct'], expected_leveraged, places=2)
    
    def test_margin_return_includes_fees(self):
        """Test that margin return correctly subtracts fees"""
        entry_price = 100.0
        exit_price = 102.0
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Margin return should be leveraged return minus fees
        expected_margin = pnl['leveraged_return_pct'] - pnl['fees_pct']
        self.assertAlmostEqual(pnl['margin_return_pct'], expected_margin, places=2)
    
    def test_configured_targets(self):
        """Test that configured TP and SL targets are reasonable"""
        # TP should be positive
        self.assertGreater(MARGIN_RETURN_TP, 0)
        
        # SL should be positive (represents loss magnitude)
        self.assertGreater(MARGIN_RETURN_SL, 0)
        
        # TP should be greater than SL for typical risk/reward
        self.assertGreater(MARGIN_RETURN_TP, MARGIN_RETURN_SL)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_very_small_movement(self):
        """Test with very small price movement"""
        entry_price = 100.0
        exit_price = 100.01  # 0.01% movement
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should still calculate correctly
        self.assertAlmostEqual(pnl['price_movement_pct'], 0.01, places=2)
        self.assertAlmostEqual(pnl['leveraged_return_pct'], 0.03, places=2)
        # Margin return will be negative due to fees
        self.assertLess(pnl['margin_return_pct'], 0)
    
    def test_large_movement(self):
        """Test with large price movement"""
        entry_price = 100.0
        exit_price = 110.0  # 10% movement
        
        pnl = calcular_pnl_real(entry_price, exit_price)
        
        # Should handle large movements
        self.assertAlmostEqual(pnl['price_movement_pct'], 10.0, places=2)
        self.assertAlmostEqual(pnl['leveraged_return_pct'], 30.0, places=2)
        self.assertAlmostEqual(pnl['margin_return_pct'], 28.8, places=2)
    
    def test_custom_leverage(self):
        """Test with custom leverage value"""
        entry_price = 100.0
        exit_price = 102.0
        custom_leverage = 5
        
        pnl = calcular_pnl_real(entry_price, exit_price, leverage=custom_leverage)
        
        # Leveraged return should use custom leverage
        expected_leveraged = 2.0 * custom_leverage
        self.assertAlmostEqual(pnl['leveraged_return_pct'], expected_leveraged, places=2)


if __name__ == '__main__':
    # Run the tests with verbose output
    unittest.main(verbosity=2)
