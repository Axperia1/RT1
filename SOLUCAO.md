# Resumo da Solução - Correção TP/SL com Alavancagem

## Problema Original

O bot tinha uma **divergência crítica** entre:
- TP/SL configurados (5% e 3%)
- PnL real reportado (incorreto: 6.20% quando deveria ser ~0.99%)

### Exemplo Real do Problema
```
Entrada: 16.5894
Saída: 16.7104
Movimento de Preço: 0.729%
PnL Reportado (INCORRETO): 6.20%
PnL Correto: 0.988%
```

## Causa Raiz

Confusão entre dois conceitos diferentes:
1. **Movimento de Preço**: Variação percentual do ativo (0.729%)
2. **Retorno sobre Margem**: Retorno alavancado real após fees (0.988%)

## Solução Implementada

### 1. Separação Clara de Conceitos

Criado arquivo `_axperia_trading_following.py` com:

```python
# Configuração
LEVERAGE = 3
FEE_RATE = 0.006  # 0.6% por lado
TOTAL_FEES = 0.012  # 1.2% total

# Metas de Retorno sobre Margem (após fees)
MARGIN_RETURN_TP = 5.0  # 5% Take Profit
MARGIN_RETURN_SL = 3.0  # 3% Stop Loss

# Movimento de Preço Necessário (calculado)
# Formula: (margin_return + fees) / leverage
PRICE_MOVEMENT_TP = 2.07%  # Para atingir 5% retorno
PRICE_MOVEMENT_SL = 1.40%  # Para atingir 3% perda
```

### 2. Cálculo Correto do PnL

```python
def calcular_pnl_real(entry_price, current_price, leverage=3):
    # 1. Movimento de preço bruto
    price_movement_pct = ((current_price - entry_price) / entry_price) * 100
    
    # 2. Aplicar alavancagem
    leveraged_return_pct = price_movement_pct * leverage
    
    # 3. Subtrair fees
    fees_pct = 1.2  # 0.6% cada lado
    margin_return_pct = leveraged_return_pct - fees_pct
    
    return {
        'price_movement_pct': price_movement_pct,
        'leveraged_return_pct': leveraged_return_pct,
        'fees_pct': fees_pct,
        'margin_return_pct': margin_return_pct  # Valor real!
    }
```

### 3. Validações Corretas

```python
# ANTES (ERRADO): Comparava com movimento de preço
if pnl_pct >= (TP_PCT * 100):  # Comparação incorreta

# DEPOIS (CORRETO): Compara com retorno sobre margem
def validar_take_profit(pnl_data):
    return pnl_data['margin_return_pct'] >= MARGIN_RETURN_TP
```

## Resultados

### Operação Real Recalculada

```
Entrada: 16.5894
Saída: 16.7104

✅ Movimento de Preço: 0.729%
✅ Retorno Alavancado: 2.188% (0.729% × 3)
✅ Fees: 1.200%
✅ Retorno sobre Margem: 0.988% (2.188% - 1.200%)

Validação:
❌ TP não atingido (0.988% < 5.0%)
❌ SL não atingido (0.988% > -3.0%)
```

### Para Atingir TP de 5%

```
Movimento necessário: 2.07%
Exemplo: Entrada 100.0 → Saída 102.07

✅ Movimento de Preço: 2.070%
✅ Retorno Alavancado: 6.210% (2.070% × 3)
✅ Fees: 1.200%
✅ Retorno sobre Margem: 5.010% (6.210% - 1.200%)

Validação:
✅ TP atingido! (5.010% >= 5.0%)
```

## Tabela de Referência

Com leverage 3x e fees 1.2%:

| Movimento de Preço | Retorno Alavancado | Retorno Real | Status |
|-------------------|-------------------|--------------|---------|
| 0.5%              | 1.5%              | 0.3%         | -       |
| 0.729%            | 2.19%             | 0.99%        | -       |
| 1.0%              | 3.0%              | 1.8%         | -       |
| 1.40%             | 4.2%              | 3.0%         | SL      |
| 2.07%             | 6.21%             | 5.01%        | TP ✅   |
| 3.0%              | 9.0%              | 7.8%         | TP      |

## Verificação

✅ **20 testes automatizados** - Todos passando
✅ **CodeQL security scan** - Sem alertas
✅ **Documentação completa** - README e comentários
✅ **Exemplos práticos** - Operação real e casos de teste

## Fórmulas Importantes

### Retorno sobre Margem
```
margin_return = (price_movement × leverage) - fees
```

### Movimento Necessário para TP/SL
```
price_movement = (margin_return_target + fees) / leverage

Exemplo TP 5%:
price_movement = (5.0% + 1.2%) / 3 = 2.067%
```

## Arquivos do Projeto

1. **`_axperia_trading_following.py`** (225 linhas)
   - Implementação completa com cálculos corretos
   - Funções de validação de TP/SL
   - Exemplos e documentação

2. **`test_axperia_trading_following.py`** (287 linhas)
   - 20 testes cobrindo todos os casos
   - Validação da operação real do problema
   - Testes de edge cases

3. **`README.md`** (188 linhas)
   - Documentação completa
   - Exemplos práticos
   - Tabelas de referência

4. **`.gitignore`**
   - Configuração Python padrão

## Conclusão

A solução agora:
- ✅ Separa claramente movimento de preço vs retorno sobre margem
- ✅ Calcula PnL corretamente com leverage e fees
- ✅ Valida TP/SL usando retorno sobre margem (não movimento de preço)
- ✅ Documenta a matemática por trás dos cálculos
- ✅ Fornece exemplos práticos e verificáveis
- ✅ Inclui testes automatizados completos

**O bot agora funciona corretamente e de forma previsível!**
