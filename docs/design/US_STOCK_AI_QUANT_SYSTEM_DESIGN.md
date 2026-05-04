# 美股 AI 量化交易系统详细设计文档

> 项目：AiQuantSys  
> 仓库：https://github.com/Liangwei-zhang/AiQuantSys.git  
> 资产范围：美股股票、ETF  
> 第一阶段：Alpaca Paper Trading + 高流动性美股 + LLM 决策 + 程序化风控  
> 明确不做：加密货币、永续合约、资金费率、Binance/OKX/Bitget、期权实盘、高频交易

---

## 1. 项目背景

本文档根据《用 AI 构建你自己的量化交易系统》中的核心思想，重新设计为一个**美股 AI 量化交易系统**。

原文章最有价值的思想不是“让 LLM 直接预测涨跌”，而是：

1. 先由程序完成市场数据处理、指标计算、市场结构分析和风险过滤；
2. 再把结构化后的市场快照交给 LLM；
3. LLM 负责推理、解释、比较候选标的和输出决策建议；
4. 程序负责最终校验、下单、止损、持仓维护和复盘。

美股市场与加密货币市场不同，不能直接复用币圈交易系统。

| 维度 | 加密货币系统 | 美股系统 |
|---|---|---|
| 交易时间 | 7x24 | 有正常交易时段、盘前盘后、节假日、半日交易 |
| 交易场所 | Binance、OKX、Bitget、Hyperliquid | Alpaca、Interactive Brokers、Tradier 等券商 |
| 数据特征 | K线、资金费率、持仓量、清算数据 | K线、Quote、财报、SEC 文件、公司行动、行业因子、期权链 |
| 风控重点 | 杠杆、爆仓、资金费率、交易所风险 | PDT、T+1、财报、停牌、LULD、做空可借券、价差、流动性 |
| 交易标的 | BTC、ETH、山寨币 | 股票、ETF，后续可扩展期权 |

因此 AiQuantSys 的第一版应该是一个**美股专用 AI 量化系统**，而不是把加密货币系统简单换成股票代码。

---

## 2. 项目目标

### 2.1 总目标

构建一个面向美股市场的 AI 辅助量化交易系统，实现：

```text
美股数据接入
    ↓
股票池筛选
    ↓
多周期技术分析
    ↓
市场结构识别
    ↓
财报与事件过滤
    ↓
美股规则检查
    ↓
账户风险控制
    ↓
LLM 结构化决策
    ↓
程序化信号校验
    ↓
券商模拟盘执行
    ↓
交易记录与复盘
```

### 2.2 第一阶段边界

第一版 MVP 只做：

- 美股股票和 ETF；
- 只做多；
- 只在正常交易时段交易；
- Alpaca Paper Trading；
- 日线 / 1小时 / 15分钟三个周期；
- 高流动性股票池；
- 趋势延续和回调买入两类策略；
- 财报窗口默认规避；
- LLM 只输出建议；
- 程序负责最终下单。

第一版不做：

- 加密货币；
- 永续合约；
- 期权实盘；
- 做空；
- 盘前盘后实盘；
- 高频交易；
- 自动全市场实盘扫描；
- 强化学习；
- 多券商实盘路由。

---

## 3. 总体架构

```text
前端控制台
    ↓
FastAPI 服务层
    ↓
用户配置 / 策略配置 / 风控配置
    ↓
美股交易日历模块
    ↓
行情与事件数据接入层
    ↓
股票池筛选模块
    ↓
技术指标计算模块
    ↓
市场结构分析模块
    ↓
大盘与行业状态模块
    ↓
财报与公司行动过滤模块
    ↓
账户风险控制模块
    ↓
LLM Context Builder
    ↓
LLM 决策模块
    ↓
LLM Response Parser
    ↓
程序化信号校验模块
    ↓
券商执行模块
    ↓
订单 / 成交 / 持仓管理
    ↓
交易复盘 / 回测 / 日志 / 通知
```

---

## 4. 核心原则

### 4.1 LLM 不直接预测价格

禁止：

```text
这是 AAPL 最近的 K 线，请判断接下来涨还是跌。
```

推荐：

```json
{
  "symbol": "AAPL",
  "market_context": {
    "spy_trend": "neutral",
    "qqq_trend": "bullish",
    "vix_state": "falling",
    "sector_strength": "technology_strong"
  },
  "technical_structure": {
    "daily": "bullish_above_ema20_ema50",
    "h1": "pullback_to_vwap",
    "m15": "retest_confirmed_with_volume"
  },
  "event_flags": {
    "earnings_in_days": 14,
    "corporate_action_today": false,
    "major_sec_filing_today": false
  },
  "risk_state": {
    "daily_pnl_pct": -0.3,
    "max_daily_loss_pct": 2.0,
    "open_positions": 3,
    "max_open_positions": 5
  },
  "allowed_actions": ["open_long_limit", "wait", "hold"]
}
```

### 4.2 风控先于决策

正确顺序：

```text
交易日历检查
    ↓
账户状态检查
    ↓
风控检查
    ↓
事件风险检查
    ↓
市场分析
    ↓
LLM 决策
    ↓
程序化校验
    ↓
订单执行
```

### 4.3 程序拥有最终执行权

LLM 只能建议，不能直接下单。所有 LLM 输出必须经过：

- JSON Schema 校验；
- 动作白名单校验；
- 交易时段校验；
- 财报窗口校验；
- 最大仓位校验；
- 最大亏损校验；
- 价差校验；
- 成交额校验；
- 券商购买力校验；
- 止损合法性校验。

---

## 5. 技术选型

| 模块 | 推荐方案 |
|---|---|
| 后端 API | Python 3.11+ / FastAPI |
| 异步任务 | asyncio / APScheduler |
| 数据库 | PostgreSQL，MVP 可用 SQLite |
| 缓存 | Redis |
| 行情数据 | Alpaca Market Data，后续 Polygon / IBKR |
| 模拟盘 | Alpaca Paper Trading |
| 生产券商 | Interactive Brokers |
| 技术指标 | pandas / numpy / pandas-ta / TA-Lib |
| 前端 | Vue 3 或 React + Tailwind CSS |
| 图表 | ECharts / TradingView Lightweight Charts |
| LLM | OpenAI compatible API / DeepSeek / Claude / Gemini |
| 日志 | loguru / structlog |
| 通知 | Telegram / Email / Webhook |

---

## 6. 核心模块设计

## 6.1 美股交易日历模块

### 6.1.1 职责

判断当前是否允许交易，并提供市场状态。

需要识别：

- 正常交易日；
- 节假日；
- 半日交易；
- 盘前；
- 正常交易时段；
- 收盘后；
- 开盘保护窗口；
- 收盘保护窗口；
- 全市场熔断；
- 个股停牌。

### 6.1.2 市场状态枚举

```python
from enum import Enum

class MarketSession(str, Enum):
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    OPEN_AUCTION = "open_auction"
    REGULAR = "regular"
    CLOSE_AUCTION = "close_auction"
    AFTER_HOURS = "after_hours"
    HALF_DAY = "half_day"
    HALTED = "halted"
```

### 6.1.3 调度规则

```text
05:00 ET：更新股票池、财报日历、公司行动
08:30 ET：获取盘前异动
09:25 ET：开盘保护窗口，不允许追单
09:31 ET：开始正常交易逻辑
每 15 分钟：运行 AI 决策
15:45 ET：降低新开仓权限
15:50 ET：进入收盘保护窗口
16:05 ET：日终复盘
夜间：回测、日志归档、财报文件更新
```

---

## 6.2 美股数据接入模块

### 6.2.1 行情数据

- 日线；
- 1 小时 K 线；
- 15 分钟 K 线；
- 1 分钟 K 线；
- 实时报价；
- Bid / Ask；
- 成交量；
- VWAP；
- Relative Volume；
- 盘前涨跌幅；
- 盘后涨跌幅；
- Spread。

### 6.2.2 基本面数据

- 市值；
- 行业；
- 营收；
- EPS；
- 毛利率；
- 自由现金流；
- 估值指标；
- SEC 10-K / 10-Q / 8-K。

### 6.2.3 事件数据

- 财报日期；
- 财报发布时间：盘前 / 盘后；
- 分红；
- 拆股；
- 并购；
- 增发；
- 管理层变动；
- FOMC；
- CPI；
- 非农数据。

### 6.2.4 期权辅助数据

第一版不交易期权，但可作为辅助信号：

- IV Rank；
- IV Percentile；
- Put / Call Ratio；
- 期权成交量；
- 期权未平仓量；
- Expected Move。

---

## 6.3 股票池筛选模块

### 6.3.1 股票池层级

```text
全市场股票
    ↓
基础可交易池
    ↓
高流动性池
    ↓
策略候选池
    ↓
LLM 分析池
    ↓
最终交易池
```

### 6.3.2 基础过滤条件

```text
股价 > 5 美元
20日平均成交额 > 5000万美元
交易所属于 NYSE / NASDAQ / ARCA
不是 OTC
不是粉单
不是退市风险股票
不是停牌股票
不是重大公司行动当天
财报黑名单未触发
价差不超过阈值
```

### 6.3.3 过滤示例

```python
def base_stock_filter(stock):
    if stock.price < 5:
        return False
    if stock.avg_dollar_volume_20d < 50_000_000:
        return False
    if not stock.is_active:
        return False
    if stock.exchange not in ["NYSE", "NASDAQ", "ARCA"]:
        return False
    if stock.is_halted:
        return False
    if stock.earnings_blackout:
        return False
    if stock.spread_bps > 20:
        return False
    return True
```

### 6.3.4 美股选股评分模型

```text
StockScore =
    流动性评分 * 0.25
  + 相对强度评分 * 0.20
  + 趋势质量评分 * 0.15
  + 波动率质量评分 * 0.15
  + 财报安全评分 * 0.10
  + 行业强度评分 * 0.10
  + 期权情绪评分 * 0.05
```

---

## 6.4 技术指标模块

### 6.4.1 周期设计

| 周期 | 用途 |
|---|---|
| 1D | 判断大趋势和市场结构 |
| 1H | 判断盘中结构和节奏 |
| 15M | 判断入场时机 |
| 1M | 只用于订单执行校验 |

### 6.4.2 指标清单

第一版支持：

- EMA20；
- EMA50；
- EMA200；
- RSI14；
- MACD；
- ADX；
- ATR；
- Bollinger Bands；
- VWAP；
- OBV；
- Relative Volume；
- Gap Percent；
- Beta；
- Sector Relative Strength。

### 6.4.3 结构化输出

```json
{
  "symbol": "MSFT",
  "daily": {
    "trend": "bullish",
    "ema_structure": "price_above_20_50_200",
    "relative_strength_vs_qqq": "strong",
    "rsi_state": "bullish_not_overheated",
    "atr_regime": "normal"
  },
  "h1": {
    "structure": "pullback_to_vwap",
    "momentum": "recovering",
    "volume": "above_average"
  },
  "m15": {
    "entry_state": "breakout_retest",
    "risk_reward": "acceptable",
    "spread_state": "normal"
  }
}
```

---

## 6.5 市场结构分析模块

### 6.5.1 通用结构

- 上升趋势；
- 下降趋势；
- 震荡区间；
- 突破；
- 假突破；
- 回踩确认；
- 趋势衰竭；
- 放量突破；
- 缩量回调。

### 6.5.2 美股专用结构

- 盘前跳空；
- 财报后跳空；
- 开盘区间突破；
- VWAP 上方趋势；
- VWAP 下方弱势；
- 收盘前资金流；
- 行业共振；
- 大盘拖累；
- 个股独立行情。

---

## 6.6 风险管理模块

### 6.6.1 风控优先级

```text
市场是否开盘
账户是否允许交易
是否触发 PDT / 日内交易限制
是否触发财报黑名单
是否停牌 / LULD
是否超过最大日亏损
是否超过最大回撤
是否超过最大仓位
是否满足流动性
是否满足价差要求
LLM 信号是否合规
```

### 6.6.2 风控配置表

```sql
CREATE TABLE user_risk_config (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    max_daily_loss_pct NUMERIC(8,4) DEFAULT 2.0000,
    max_weekly_loss_pct NUMERIC(8,4) DEFAULT 5.0000,
    max_drawdown_pct NUMERIC(8,4) DEFAULT 10.0000,
    max_position_pct NUMERIC(8,4) DEFAULT 10.0000,
    max_sector_exposure_pct NUMERIC(8,4) DEFAULT 30.0000,
    max_single_trade_loss_pct NUMERIC(8,4) DEFAULT 1.0000,
    max_open_positions INT DEFAULT 5,
    min_avg_dollar_volume BIGINT DEFAULT 50000000,
    max_spread_bps NUMERIC(8,4) DEFAULT 20.0000,
    avoid_earnings BOOLEAN DEFAULT TRUE,
    earnings_blackout_days INT DEFAULT 2,
    enable_pdt_guard BOOLEAN DEFAULT TRUE,
    enable_short_guard BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 6.6.3 仓位计算

```text
单笔最大亏损 = 账户权益 * 单笔风险比例
每股风险 = abs(入场价 - 止损价)
股数 = 单笔最大亏损 / 每股风险
```

```python
def calculate_position_size(account_equity, entry_price, stop_price, risk_pct):
    max_loss = account_equity * risk_pct
    risk_per_share = abs(entry_price - stop_price)
    if risk_per_share <= 0:
        return 0
    shares = int(max_loss / risk_per_share)
    notional = shares * entry_price
    return shares, notional
```

### 6.6.4 日内熔断

```text
亏损达到 -1%：降低仓位 50%
亏损达到 -2%：停止新开仓
亏损达到 -3%：只允许减仓 / 平仓
连续亏损 3 笔：暂停 1 小时
连续亏损 5 笔：当天停止交易
```

### 6.6.5 财报风控

```text
财报前 2 天：禁止新开 swing 仓位
财报当天：默认禁止交易
财报后第 1 天：只允许事件策略
财报跳空超过 8%：降低仓位
财报后成交量不足：禁止交易
```

---

## 6.7 LLM 决策模块

### 6.7.1 LLM 可以做

- 理解多周期信号；
- 判断信号冲突；
- 比较多个候选股票；
- 选择策略模板；
- 解释交易理由；
- 输出 JSON 决策建议。

### 6.7.2 LLM 不能做

- 直接下单；
- 绕过风控；
- 自行决定杠杆；
- 忽略 PDT 或财报风险；
- 编造行情、新闻或财务数据；
- 修改系统规则。

### 6.7.3 Prompt 模板

```text
你是一个美股 AI 量化交易决策助手。

你不能直接下单。
你只能基于系统提供的数据做判断。
你不能编造行情、财报、新闻或财务数据。
你不能绕过风控规则。
你只能从 allowed_actions 中选择动作。
如果信号不充分，必须选择 wait。
你必须输出严格 JSON。

当前市场状态：
{market_context}

当前股票数据：
{stock_features}

事件风险：
{event_flags}

账户与风控状态：
{risk_state}

允许动作：
{allowed_actions}

请输出：
{
  "symbol": "AAPL",
  "action": "open_long_limit | close_position | update_stop_loss | wait",
  "strategy_type": "trend_following | pullback | breakout | gap_follow | no_trade",
  "confidence": 0.0,
  "entry_price": null,
  "stop_loss": null,
  "take_profit": null,
  "position_size_pct": 0.0,
  "reason": "...",
  "risk_notes": ["..."],
  "must_pass_checks": ["session_ok", "earnings_ok", "spread_ok", "pdt_ok"]
}
```

---

## 6.8 信号校验模块

LLM 输出后必须经过程序化校验。

```python
def validate_llm_decision(decision, account, symbol_state, risk_state):
    if decision["action"] not in symbol_state.allowed_actions:
        return Reject("action_not_allowed")

    if symbol_state.session != "regular":
        if not account.allow_extended_hours:
            return Reject("extended_hours_not_allowed")

    if symbol_state.is_halted:
        return Reject("symbol_halted")

    if symbol_state.earnings_in_days is not None:
        if symbol_state.earnings_in_days <= account.earnings_blackout_days:
            return Reject("earnings_blackout")

    if risk_state.daily_loss_pct <= -account.max_daily_loss_pct:
        return Reject("daily_loss_limit")

    if symbol_state.spread_bps > account.max_spread_bps:
        return Reject("spread_too_wide")

    if decision["position_size_pct"] > account.max_position_pct:
        decision["position_size_pct"] = account.max_position_pct

    if decision["action"].startswith("open") and decision["stop_loss"] is None:
        return Reject("missing_stop_loss")

    return Accept(decision)
```

---

## 6.9 券商执行模块

### 6.9.1 券商适配顺序

第一阶段：Alpaca

- Paper Trading 方便；
- API 简单；
- 适合 MVP；
- 支持股票交易。

第二阶段：Interactive Brokers

- 市场覆盖广；
- 订单类型多；
- 更适合生产环境；
- API 和认证复杂度更高。

第三阶段：Tradier

- 适合期权链数据；
- 可作为辅助数据源或备选券商。

### 6.9.2 统一券商接口

```python
class BaseBroker:
    async def get_account(self) -> Account:
        pass

    async def get_positions(self) -> list[Position]:
        pass

    async def get_orders(self) -> list[Order]:
        pass

    async def submit_order(self, order: OrderRequest) -> OrderResult:
        pass

    async def cancel_order(self, order_id: str) -> bool:
        pass

    async def get_bars(self, symbol: str, timeframe: str, start, end):
        pass

    async def get_quote(self, symbol: str) -> Quote:
        pass

    async def is_shortable(self, symbol: str) -> bool:
        pass
```

### 6.9.3 订单策略

```text
正常交易时段：优先限价单
盘前 / 盘后：只允许限价单
财报日：默认不下单
价差过大：禁止市价单，必要时禁止交易
```

---

## 7. 数据库设计

## 7.1 股票主数据表

```sql
CREATE TABLE symbol_master (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    symbol VARCHAR(16) NOT NULL UNIQUE,
    name VARCHAR(255),
    exchange VARCHAR(32),
    asset_type VARCHAR(16) DEFAULT 'stock',
    sector VARCHAR(64),
    industry VARCHAR(128),
    is_active BOOLEAN DEFAULT TRUE,
    is_shortable BOOLEAN DEFAULT FALSE,
    min_tick NUMERIC(12,6) DEFAULT 0.01,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 7.2 K线表

```sql
CREATE TABLE bars_15m (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    symbol VARCHAR(16) NOT NULL,
    ts TIMESTAMP NOT NULL,
    open NUMERIC(18,6),
    high NUMERIC(18,6),
    low NUMERIC(18,6),
    close NUMERIC(18,6),
    volume BIGINT,
    vwap NUMERIC(18,6),
    trade_count INT,
    session_tag VARCHAR(32),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, ts)
);
```

## 7.3 AI 决策表

```sql
CREATE TABLE ai_decisions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    model_provider VARCHAR(64),
    model_name VARCHAR(128),
    prompt_hash VARCHAR(128),
    request_payload JSONB,
    raw_response TEXT,
    parsed_response JSONB,
    validation_status VARCHAR(32) DEFAULT 'error',
    reject_reason VARCHAR(255),
    confidence NUMERIC(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 7.4 订单表

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    decision_id BIGINT,
    broker VARCHAR(32),
    broker_order_id VARCHAR(128),
    symbol VARCHAR(16) NOT NULL,
    side VARCHAR(32) NOT NULL,
    order_type VARCHAR(32) NOT NULL,
    time_in_force VARCHAR(32) DEFAULT 'day',
    quantity INT NOT NULL,
    limit_price NUMERIC(18,6),
    stop_price NUMERIC(18,6),
    status VARCHAR(32) DEFAULT 'new',
    submitted_at TIMESTAMP,
    filled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 7.5 持仓表

```sql
CREATE TABLE positions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    side VARCHAR(16) NOT NULL,
    quantity INT NOT NULL,
    avg_price NUMERIC(18,6),
    market_price NUMERIC(18,6),
    unrealized_pnl NUMERIC(18,6),
    realized_pnl NUMERIC(18,6),
    stop_loss NUMERIC(18,6),
    take_profit NUMERIC(18,6),
    opened_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 8. 回测系统设计

### 8.1 美股回测必须考虑

- 退市股票；
- 拆股；
- 分红；
- 财报日期；
- 财报实际发布时间；
- 盘前盘后；
- 滑点；
- 价差；
- 成交量限制；
- 停牌；
- PDT；
- 做空可借券；
- 手续费；
- T+1 资金结算。

### 8.2 回测流程

```text
加载历史股票池
        ↓
加载历史行情
        ↓
加载财报 / 公司行动 / SEC 文件时间点
        ↓
按交易日推进
        ↓
每日开盘前选股
        ↓
盘中每 15 分钟生成特征
        ↓
运行策略 / LLM 决策
        ↓
程序化风控校验
        ↓
模拟成交与滑点
        ↓
更新持仓
        ↓
触发止损止盈
        ↓
日终结算
        ↓
输出绩效报告
```

### 8.3 回测指标

- 总收益；
- 年化收益；
- 最大回撤；
- Sharpe Ratio；
- Sortino Ratio；
- Calmar Ratio；
- 胜率；
- 盈亏比；
- 平均持仓时间；
- 滑点成本；
- 手续费成本；
- 最大连续亏损；
- 行业暴露；
- 财报窗口表现；
- 大盘上涨期表现；
- 大盘下跌期表现；
- 震荡期表现。

---

## 9. 策略模板

## 9.1 趋势延续策略

适合：

- 强趋势股；
- 价格在 EMA20 / EMA50 上方；
- 大盘风险偏好良好；
- 行业强势；
- 成交量健康。

入场：

```text
日线多头
1小时回踩
15分钟重新站上 VWAP
```

出场：

```text
跌破 1小时结构低点
跌破 VWAP
达到 2R 止盈
移动止损触发
```

## 9.2 回调买入策略

适合：

- 强势股短线回调；
- 趋势未破；
- 回调到 EMA20 / VWAP / 支撑区；
- RSI 从中性区反弹。

## 9.3 开盘区间突破策略

适合：

- 盘前有明显催化；
- 开盘 15-30 分钟形成区间；
- 放量突破开盘区间；
- 大盘同步支持。

第一版只建议模拟，不建议直接实盘。

## 9.4 财报后趋势策略

适合：

- 财报后跳空；
- 成交量明显放大；
- 价格没有快速回补缺口；
- 行业同步强势。

第一版建议只做观察或小仓位模拟。

---

## 10. 交易复盘模块

### 10.1 每笔交易复盘输出

```json
{
  "symbol": "NVDA",
  "strategy": "pullback",
  "entry_reason": "日线趋势强，1小时回踩VWAP，15分钟放量反弹",
  "exit_reason": "达到2R止盈",
  "pnl_pct": 3.2,
  "holding_period": "2 days",
  "market_context": "QQQ bullish, SMH strong",
  "mistake": null,
  "lesson": "强行业趋势下，VWAP回踩策略表现良好"
}
```

### 10.2 失败类型

```python
class FailureType(str, Enum):
    FALSE_BREAKOUT = "false_breakout"
    LATE_ENTRY = "late_entry"
    STOP_TOO_TIGHT = "stop_too_tight"
    EARNINGS_GAP_RISK = "earnings_gap_risk"
    MARKET_REVERSAL = "market_reversal"
    SECTOR_WEAKNESS = "sector_weakness"
    LOW_LIQUIDITY = "low_liquidity"
    SPREAD_TOO_WIDE = "spread_too_wide"
    OVERTRADING = "overtrading"
    LLM_OVERCONFIDENCE = "llm_overconfidence"
```

---

## 11. 推荐项目目录

```text
aiquantsys/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   └── logging_config.py
├── us_stock/
│   ├── calendar/
│   │   ├── market_calendar.py
│   │   └── session_state.py
│   ├── brokers/
│   │   ├── base.py
│   │   ├── alpaca_broker.py
│   │   ├── ibkr_broker.py
│   │   └── factory.py
│   ├── market_data/
│   │   ├── bars.py
│   │   ├── quotes.py
│   │   ├── sec_filings.py
│   │   ├── earnings.py
│   │   └── corporate_actions.py
│   ├── universe/
│   │   ├── filters.py
│   │   ├── scoring.py
│   │   └── watchlist.py
│   ├── analysis/
│   │   ├── indicators.py
│   │   ├── market_structure.py
│   │   ├── sector_strength.py
│   │   └── feature_builder.py
│   ├── rules/
│   │   ├── pdt.py
│   │   ├── settlement.py
│   │   ├── short_sale.py
│   │   ├── luld.py
│   │   ├── trading_session.py
│   │   └── earnings_blackout.py
│   ├── risk/
│   │   ├── position_sizing.py
│   │   ├── drawdown.py
│   │   ├── circuit_breaker.py
│   │   └── exposure.py
│   ├── llm/
│   │   ├── prompt_templates.py
│   │   ├── context_builder.py
│   │   ├── response_parser.py
│   │   └── decision_cache.py
│   ├── execution/
│   │   ├── order_validator.py
│   │   ├── order_router.py
│   │   ├── order_manager.py
│   │   ├── fill_handler.py
│   │   └── position_manager.py
│   ├── backtest/
│   │   ├── engine.py
│   │   ├── broker_simulator.py
│   │   ├── slippage.py
│   │   ├── metrics.py
│   │   └── report.py
│   └── review/
│       ├── trade_autopsy.py
│       └── failure_classifier.py
├── docs/
│   └── design/
├── tests/
├── pyproject.toml
└── README.md
```

---

## 12. MVP 开发路线

### Phase 1：基础框架

- 初始化 Python 项目；
- 建立 FastAPI 服务；
- 建立配置系统；
- 建立日志系统；
- 建立数据库连接；
- 建立 Redis 连接；
- 建立项目目录。

### Phase 2：Alpaca 模拟盘接入

- Alpaca 账户查询；
- Alpaca 持仓查询；
- Alpaca K线获取；
- Alpaca Quote 获取；
- Alpaca Paper Trading 下单；
- 订单状态同步。

### Phase 3：股票池与指标

- 股票池基础过滤；
- 流动性评分；
- 相对强度评分；
- 财报黑名单；
- EMA / RSI / MACD / ATR / ADX / VWAP；
- 日线 / 1H / 15M 多周期特征。

### Phase 4：风控系统

- 最大日亏损；
- 最大回撤；
- 最大单股仓位；
- 最大行业暴露；
- 财报避让；
- 价差过滤；
- 停牌过滤；
- 订单校验。

### Phase 5：LLM 决策

- 构建美股 Prompt；
- 构建 LLM Payload；
- JSON Schema 校验；
- 决策记录；
- 拒绝原因记录。

### Phase 6：模拟交易闭环

- 运行 watchlist；
- 生成 AI 决策；
- 校验信号；
- 提交模拟盘订单；
- 同步成交；
- 维护持仓；
- 生成复盘。

### Phase 7：回测系统

- 历史数据加载；
- 事件驱动回测；
- 手续费和滑点；
- 策略对比；
- 报告生成。

---

## 13. MVP 验收标准

第一版完成后，应满足：

- 能读取 Alpaca Paper Trading 账户；
- 能获取指定股票的日线 / 1H / 15M 数据；
- 能生成 20-50 只股票的 watchlist；
- 能计算基础指标；
- 能识别 SPY / QQQ / VIX 大盘状态；
- 能构建 LLM 输入 Payload；
- 能解析 LLM JSON 输出；
- 能拒绝不合规信号；
- 能提交模拟盘限价单；
- 能记录订单、成交和 AI 决策；
- 能生成简单交易复盘。

---

## 14. 最终结论

AiQuantSys 的核心不是“让 LLM 猜股票涨跌”，而是构建一个完整的美股交易决策管道：

```text
美股数据接入
    ↓
股票池筛选
    ↓
多周期技术结构
    ↓
财报与事件过滤
    ↓
美股规则检查
    ↓
风控前置
    ↓
LLM 结构化决策
    ↓
程序化信号校验
    ↓
券商模拟盘执行
    ↓
回测与复盘
```

第一阶段建议落地：

```text
Alpaca + Paper Trading + 高流动性美股股票池 + 日线/1H/15M + LLM 决策 + 严格风控 + 回测复盘
```

等模拟盘和回测稳定后，再扩展：

- Interactive Brokers；
- 做空；
- 期权数据增强；
- SEC 文件分析；
- 多策略组合；
- 小资金实盘；
- 强化学习或自适应参数优化。

---

## 15. 参考资料

- 原文章：https://dashen.wang/article/8841
- SEC T+1 Settlement：https://www.sec.gov/newsroom/press-releases/2024-62
- FINRA Rule 4210：https://www.finra.org/rules-guidance/rulebooks/finra-rules/4210
- Alpaca Paper Trading：https://docs.alpaca.markets/docs/paper-trading
- Alpaca Orders：https://docs.alpaca.markets/docs/orders-at-alpaca
- Interactive Brokers API：https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/
- SEC EDGAR APIs：https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Nasdaq Earnings Calendar：https://www.nasdaq.com/market-activity/earnings
- TA-Lib Functions：https://ta-lib.org/functions/
