# AiQuantSys

AiQuantSys 是一个面向**美股股票 / ETF** 的 AI 辅助量化交易系统。

第一阶段目标不是让 LLM 直接预测涨跌，而是构建完整的美股交易决策管道：

```text
美股数据接入 → 股票池筛选 → 多周期结构分析 → 事件过滤 → 风控前置 → LLM 结构化决策 → 程序校验 → 模拟盘执行 → 回测复盘
```

## 当前状态

已完成 MVP Phase 1 和 Phase 2 的基础能力：

- FastAPI 应用入口；
- 环境变量配置；
- 日志配置；
- 美股市场时段识别；
- 股票池基础过滤；
- 固定亏损额度仓位计算；
- LLM 决策数据模型；
- Alpaca Paper Trading broker 适配器；
- 账户、持仓、报价、K线 API；
- 纸交易订单提交 API；
- 基础单元测试。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload
```

## 环境变量

在 `.env` 中配置 Alpaca Paper Trading：

```env
ALPACA_API_KEY=your_key
ALPACA_SECRET_KEY=your_secret
ALPACA_PAPER_BASE_URL=https://paper-api.alpaca.markets
ALPACA_DATA_BASE_URL=https://data.alpaca.markets
ALLOW_LIVE_TRADING=false
ALLOW_EXTENDED_HOURS=false
```

## API 示例

健康检查：

```bash
curl http://localhost:8000/health
```

美股市场时段：

```bash
curl http://localhost:8000/api/us-stock/session
```

Alpaca Paper 账户：

```bash
curl http://localhost:8000/api/us-stock/broker/account
```

当前持仓：

```bash
curl http://localhost:8000/api/us-stock/broker/positions
```

最新报价：

```bash
curl http://localhost:8000/api/us-stock/broker/quote/MSFT
```

15分钟K线：

```bash
curl "http://localhost:8000/api/us-stock/broker/bars/MSFT?timeframe=15Min&lookback_days=5&limit=100"
```

提交 Alpaca Paper 限价单：

```bash
curl -X POST http://localhost:8000/api/us-stock/broker/orders/paper \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MSFT",
    "side": "buy",
    "quantity": 1,
    "order_type": "limit",
    "time_in_force": "day",
    "limit_price": 420,
    "extended_hours": false
  }'
```

运行测试：

```bash
pytest
```

## 目录

```text
app/                    FastAPI 应用、配置、日志
us_stock/calendar/       美股市场时段与交易日历
us_stock/brokers/        Alpaca / IBKR 等券商适配
us_stock/universe/       股票池过滤与评分
us_stock/risk/           风控与仓位计算
us_stock/execution/      订单校验与执行辅助
us_stock/llm/            LLM 决策数据模型
us_stock/api/            API 路由
docs/design/             设计文档
tests/                   单元测试
```

## 第一阶段范围

- 只做美股股票 / ETF；
- 只做多；
- 只接 Alpaca Paper Trading；
- 只在正常交易时段交易；
- 日线 / 1H / 15M 多周期；
- 财报窗口默认规避；
- LLM 只输出建议，程序负责最终执行。

## 文档

详细设计文档：

- `docs/design/US_STOCK_AI_QUANT_SYSTEM_DESIGN.md`
