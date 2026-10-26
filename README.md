# Arbitrage Crypto App

Aplicativo pessoal para monitorar oportunidades de arbitragem entre corretoras de criptoativos. A primeira versão é **somente leitura e simulação**: consulta preços públicos, estima taxas/slippage e sinaliza spreads; não envia ordens reais.

## Estado do projeto

- [x] Estrutura inicial e regras de segurança
- [ ] Scanner público Binance ↔ Bybit
- [ ] Cálculo de lucro líquido com taxas e slippage
- [ ] Painel web local
- [ ] Simulação/paper trading
- [ ] Testes em testnet
- [ ] Execução real opcional, apenas após validação e controles de risco

## Segurança importante

Este repositório está atualmente **público**. Nunca coloque chaves/API secrets, senhas, tokens, arquivos `.env` ou dados de conta no GitHub. Para qualquer integração privada futura, prefira chaves sem permissão de saque e mantenha os segredos somente no backend, fora do controle de versão. Se pretendia manter o projeto privado, altere Visibility em Settings → General → Danger Zone.

## Princípios

- Não afirmar que um spread é lucro garantido.
- Considerar taxas, liquidez, slippage, atraso de dados, fills parciais e risco de execução.
- Exibir claramente quando os dados estiverem indisponíveis ou desatualizados.
- Começar com dados públicos e simulação; ordens reais ficam desativadas por padrão.

## Desenvolvimento

Requisitos: Python 3.11+.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abra `http://127.0.0.1:8000`.

## Configuração

Copie `.env.example` para `.env` somente no seu computador. Não envie esse arquivo ao GitHub. Na versão inicial, a leitura de mercado usa endpoints públicos e não precisa de API key.
