# Axperia Trading Bot - RT1

## Problema Resolvido: Divergência TP/SL com Alavancagem

Este repositório contém a solução para o problema de **divergência crítica** entre percentuais configurados de Take Profit (TP) e Stop Loss (SL) e o PnL real calculado com alavancagem.

## O Problema

### Análise da Operação Real
```
Entrada: 16.5894
Saída: 16.7104
Movimento de Preço: 0.729%
PnL Reportado (incorreto): 6.20%
Configuração: TP=5%, SL=3%, Leverage=3x
```

### Causa Raiz Identificada

1. **Confusão Conceitual**: TP_PCT/SL_PCT eram definidos como **movimento de preço** (5%), mas pnl_pct era calculado como **retorno sobre margem alavancada** (~6.20%)
2. **Cálculo Incorreto**: Com leverage 3x, um movimento de 0.729% deveria resultar em ~0.987% de retorno real (após fees), não 6.20%
3. **Impacto**: Bot saía em 6.20% quando TP configurado era 5%, impossibilitando otimização adequada de risco/recompensa

## A Solução

### Separação Clara de Conceitos

O código agora separa claramente dois conceitos fundamentais:

1. **Movimento de Preço** (`price_movement_pct`): A variação percentual do preço do ativo
2. **Retorno sobre Margem** (`margin_return_pct`): O retorno real sobre a margem utilizada (após alavancagem e fees)

### Fórmulas Implementadas

```python
# Movimento de Preço
price_movement_pct = ((current_price - entry_price) / entry_price) × 100

# Retorno Alavancado (antes de fees)
leveraged_return_pct = price_movement_pct × leverage

# Retorno sobre Margem (após fees)
margin_return_pct = leveraged_return_pct - total_fees_pct
```

### Exemplo Prático

Para atingir **5% de retorno sobre margem** com **3x leverage**:

```
Retorno desejado: 5%
Com fees de 1.2% (0.6% cada lado): 5% + 1.2% = 6.2% retorno alavancado necessário
Movimento de preço: 6.2% / 3 = 2.067%
```

Portanto, é necessário um movimento de **~2.07%** no preço para atingir 5% de retorno real.

## Arquivos Principais

### `_axperia_trading_following.py`

Módulo principal contendo:

- **Constantes de Configuração**:
  - `LEVERAGE`: Alavancagem utilizada (padrão: 3x)
  - `FEE_RATE`: Taxa de fee por operação (padrão: 0.6%)
  - `MARGIN_RETURN_TP`: Meta de Take Profit em retorno sobre margem (padrão: 5%)
  - `MARGIN_RETURN_SL`: Meta de Stop Loss em retorno sobre margem (padrão: 3%)

- **Funções Principais**:
  - `calcular_pnl_real()`: Calcula o PnL separando movimento de preço e retorno sobre margem
  - `validar_take_profit()`: Valida se o TP foi atingido usando retorno sobre margem
  - `validar_stop_loss()`: Valida se o SL foi atingido usando retorno sobre margem
  - `imprimir_resumo_configuracao()`: Exibe um resumo da configuração atual

### `test_axperia_trading_following.py`

Suite de testes completa com **20 testes** cobrindo:

- ✅ Cálculos de PnL com movimentos positivos, negativos e zero
- ✅ Validações de Take Profit
- ✅ Validações de Stop Loss
- ✅ Consistência entre alavancagem e fees
- ✅ Casos extremos e edge cases
- ✅ Exemplo real do problema original

## Uso

### Executar o Módulo Principal

```bash
python3 _axperia_trading_following.py
```

Isso exibirá:
1. Configuração atual do bot
2. Exemplo com a operação real do problema
3. Exemplo de operação que atinge o TP

### Executar os Testes

```bash
python3 test_axperia_trading_following.py
```

Ou com pytest:
```bash
pytest test_axperia_trading_following.py -v
```

### Usar as Funções no Código

```python
from _axperia_trading_following import calcular_pnl_real, validar_take_profit

# Calcular PnL
entry = 100.0
current = 102.0
pnl = calcular_pnl_real(entry, current)

print(f"Movimento de preço: {pnl['price_movement_pct']:.2f}%")
print(f"Retorno sobre margem: {pnl['margin_return_pct']:.2f}%")

# Validar TP
if validar_take_profit(pnl):
    print("Take Profit atingido!")
```

## Resultados

### Antes da Correção
- ❌ Movimento de 0.729% reportava 6.20% de PnL
- ❌ TP configurado em 5% era atingido incorretamente
- ❌ Impossível otimizar risk/reward adequadamente

### Depois da Correção
- ✅ Movimento de 0.729% reporta corretamente 0.987% de retorno real
- ✅ TP de 5% só é atingido com movimento de ~2.07%
- ✅ Separação clara entre movimento de preço e retorno alavancado
- ✅ Risk/reward calculado corretamente

## Documentação Técnica

### Relação entre Movimento de Preço e Retorno

Com alavancagem de 3x e fees de 1.2%:

| Movimento de Preço | Retorno Alavancado | Retorno Real (após fees) |
|-------------------|-------------------|------------------------|
| 0.5%              | 1.5%              | 0.3%                   |
| 1.0%              | 3.0%              | 1.8%                   |
| 1.5%              | 4.5%              | 3.3%                   |
| 2.07%             | 6.21%             | 5.01% ✅ (TP)          |
| 2.5%              | 7.5%              | 6.3%                   |
| 3.0%              | 9.0%              | 7.8%                   |

### Constantes Importantes

```python
LEVERAGE = 3                    # Alavancagem 3x
FEE_RATE = 0.006               # 0.6% por operação
TOTAL_FEES = 0.012             # 1.2% total (entrada + saída)
MARGIN_RETURN_TP = 5.0         # 5% Take Profit
MARGIN_RETURN_SL = 3.0         # 3% Stop Loss
PRICE_MOVEMENT_TP = 2.07       # ~2.07% movimento para TP
PRICE_MOVEMENT_SL = 1.40       # ~1.40% movimento para SL
```

## Contribuindo

Para contribuir com melhorias:

1. Mantenha a separação clara entre movimento de preço e retorno sobre margem
2. Adicione testes para qualquer nova funcionalidade
3. Documente as mudanças com exemplos práticos
4. Verifique que todos os testes passam antes de submeter

## Licença

Este projeto é fornecido como está, para fins educacionais e de referência.

## Contato

Para questões ou sugestões, abra uma issue no repositório.

---

**Nota Importante**: Este código demonstra a implementação correta da lógica de TP/SL com alavancagem. Sempre teste completamente antes de usar em operações reais de trading.
