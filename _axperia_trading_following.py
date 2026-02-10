#!/usr/bin/env python3
"""
Axperia Trading Bot - Following Strategy with Leverage

This module implements a trading bot that follows a leverage-based strategy.
It separates the concepts of:
- Price Movement: The actual percentage change in the asset price
- Margin Return: The leveraged return on the margin used for the trade

Key Concepts:
- With 3x leverage, a 1% price movement results in ~3% return on margin (before fees)
- Fees are applied on both entry and exit, reducing the effective return
- TP (Take Profit) and SL (Stop Loss) are configured as MARGIN RETURN targets
"""

# =============================================================================
# CONFIGURATION CONSTANTS
# =============================================================================

# Leverage Configuration
LEVERAGE = 3  # 3x leverage

# Fee Configuration (per side)
FEE_RATE = 0.006  # 0.6% per trade (entry or exit)
TOTAL_FEES = FEE_RATE * 2  # 1.2% total (both sides)

# Risk Management - MARGIN RETURN TARGETS
# These represent the desired return on margin (after leverage is applied)
MARGIN_RETURN_TP = 5.0  # Take Profit: 5% return on margin
MARGIN_RETURN_SL = 3.0  # Stop Loss: 3% loss on margin

# Minimum Margin Return to trigger TP
MIN_MARGIN_RETURN_TARGET = MARGIN_RETURN_TP

# Calculated Price Movement Targets
# To achieve the desired margin return, we need to calculate the required price movement
# Formula: margin_return = (price_movement × leverage) - fees
# Rearranging: price_movement = (margin_return + fees) / leverage
# Example: For 5% margin return with 3x leverage and 1.2% fees:
#   leveraged_return_needed = 5.0% + 1.2% = 6.2%
#   price_movement = 6.2% / 3 = 2.067%
PRICE_MOVEMENT_TP = (MARGIN_RETURN_TP + TOTAL_FEES * 100) / LEVERAGE
PRICE_MOVEMENT_SL = (MARGIN_RETURN_SL + TOTAL_FEES * 100) / LEVERAGE

# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def calcular_pnl_real(entry_price: float, current_price: float, leverage: float = LEVERAGE) -> dict:
    """
    Calculate the real PnL considering leverage and fees.
    
    This function separates two important concepts:
    1. Price Movement: The percentage change in asset price
    2. Margin Return: The actual return on the margin used (leveraged)
    
    Args:
        entry_price: The price at which the position was entered
        current_price: The current price of the asset
        leverage: The leverage multiplier (default: LEVERAGE constant)
    
    Returns:
        dict: A dictionary containing:
            - price_movement_pct: The raw percentage change in price
            - leveraged_return_pct: The return multiplied by leverage (before fees)
            - margin_return_pct: The actual return on margin (after fees)
            - fees_pct: The total fees as a percentage
    
    Example:
        Entry: 16.5894, Exit: 16.7104, Leverage: 3x
        - Price movement: 0.729%
        - Leveraged return (before fees): 0.729% × 3 = 2.187%
        - Fees: 1.2%
        - Margin return (after fees): 2.187% - 1.2% = 0.987%
    """
    # Calculate raw price movement percentage
    price_movement_pct = ((current_price - entry_price) / entry_price) * 100
    
    # Apply leverage to get the leveraged return (before fees)
    leveraged_return_pct = price_movement_pct * leverage
    
    # Calculate fees as a percentage
    fees_pct = TOTAL_FEES * 100
    
    # Calculate the actual margin return (after fees)
    # This is the real return the trader sees on their margin
    margin_return_pct = leveraged_return_pct - fees_pct
    
    return {
        'price_movement_pct': price_movement_pct,
        'leveraged_return_pct': leveraged_return_pct,
        'fees_pct': fees_pct,
        'margin_return_pct': margin_return_pct
    }


def validar_take_profit(pnl_data: dict) -> bool:
    """
    Validate if the Take Profit condition is met.
    
    This function checks if the margin return (actual return on margin after fees)
    has reached or exceeded the configured Take Profit target.
    
    Args:
        pnl_data: Dictionary returned by calcular_pnl_real()
    
    Returns:
        bool: True if TP condition is met, False otherwise
    
    Note:
        Previous implementation incorrectly compared margin return against
        price movement targets, causing exits at wrong levels.
    """
    # Compare margin return against margin return target (not price movement)
    return pnl_data['margin_return_pct'] >= MIN_MARGIN_RETURN_TARGET


def validar_stop_loss(pnl_data: dict) -> bool:
    """
    Validate if the Stop Loss condition is met.
    
    This function checks if the margin return (actual return on margin after fees)
    has reached or exceeded the configured Stop Loss target (negative value).
    
    Args:
        pnl_data: Dictionary returned by calcular_pnl_real()
    
    Returns:
        bool: True if SL condition is met, False otherwise
    """
    # Compare margin return against margin return target (note: SL is negative)
    return pnl_data['margin_return_pct'] <= -MARGIN_RETURN_SL


def imprimir_resumo_configuracao():
    """
    Print a summary of the current configuration showing the relationship
    between price movement and margin return.
    
    This helps understand how the configured targets translate between
    price movement and actual returns.
    """
    print("=" * 70)
    print("CONFIGURAÇÃO DO BOT - AXPERIA TRADING")
    print("=" * 70)
    print(f"\nAlavancagem: {LEVERAGE}x")
    print(f"Taxa de Fee (por lado): {FEE_RATE * 100:.2f}%")
    print(f"Taxa de Fee (total): {TOTAL_FEES * 100:.2f}%")
    print("\n" + "-" * 70)
    print("METAS DE RETORNO SOBRE MARGEM (após fees):")
    print("-" * 70)
    print(f"Take Profit: {MARGIN_RETURN_TP:.2f}%")
    print(f"Stop Loss: {MARGIN_RETURN_SL:.2f}%")
    print("\n" + "-" * 70)
    print("MOVIMENTO DE PREÇO NECESSÁRIO (antes de fees):")
    print("-" * 70)
    print(f"Para TP de {MARGIN_RETURN_TP:.2f}%: ~{PRICE_MOVEMENT_TP:.2f}% de movimento")
    print(f"Para SL de {MARGIN_RETURN_SL:.2f}%: ~{PRICE_MOVEMENT_SL:.2f}% de movimento")
    print("\n" + "=" * 70)
    print("\nOBSERVAÇÃO IMPORTANTE:")
    print("O bot agora usa RETORNO SOBRE MARGEM para validações de TP/SL,")
    print("não movimento de preço. Isso garante que os targets configurados")
    print("reflitam o retorno real que o trader verá na conta.")
    print("=" * 70 + "\n")


# =============================================================================
# EXEMPLO DE USO
# =============================================================================

if __name__ == "__main__":
    # Imprimir configuração
    imprimir_resumo_configuracao()
    
    # Exemplo da operação real mencionada no problema
    print("\nEXEMPLO - Operação Real:")
    print("-" * 70)
    
    entry_price = 16.5894
    exit_price = 16.7104
    
    print(f"Entrada: {entry_price}")
    print(f"Saída: {exit_price}")
    print(f"Leverage: {LEVERAGE}x")
    
    pnl = calcular_pnl_real(entry_price, exit_price)
    
    print(f"\nResultados:")
    print(f"  Movimento de Preço: {pnl['price_movement_pct']:.3f}%")
    print(f"  Retorno Alavancado (antes de fees): {pnl['leveraged_return_pct']:.3f}%")
    print(f"  Fees Totais: {pnl['fees_pct']:.3f}%")
    print(f"  Retorno sobre Margem (após fees): {pnl['margin_return_pct']:.3f}%")
    
    print(f"\nValidações:")
    print(f"  Take Profit atingido? {validar_take_profit(pnl)}")
    print(f"  Stop Loss atingido? {validar_stop_loss(pnl)}")
    
    print("\n" + "=" * 70)
    
    # Exemplo com valores que atingem o TP
    print("\nEXEMPLO - Operação que atinge TP de 5%:")
    print("-" * 70)
    
    # Para atingir 5% de retorno sobre margem com 3x leverage:
    # Precisamos de: (5% + 1.2%) / 3 = 2.07% de movimento
    # Testando com 2.07% de movimento
    entry_price_2 = 100.0
    # 2.07% de movimento = 102.07
    exit_price_2 = 102.07
    
    print(f"Entrada: {entry_price_2}")
    print(f"Saída: {exit_price_2}")
    print(f"Leverage: {LEVERAGE}x")
    
    pnl_2 = calcular_pnl_real(entry_price_2, exit_price_2)
    
    print(f"\nResultados:")
    print(f"  Movimento de Preço: {pnl_2['price_movement_pct']:.3f}%")
    print(f"  Retorno Alavancado (antes de fees): {pnl_2['leveraged_return_pct']:.3f}%")
    print(f"  Fees Totais: {pnl_2['fees_pct']:.3f}%")
    print(f"  Retorno sobre Margem (após fees): {pnl_2['margin_return_pct']:.3f}%")
    
    print(f"\nValidações:")
    print(f"  Take Profit atingido? {validar_take_profit(pnl_2)}")
    print(f"  Stop Loss atingido? {validar_stop_loss(pnl_2)}")
    
    print("\n" + "=" * 70)
