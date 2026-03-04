from finrl.meta.data_processors.processor_alpaca import AlpacaProcessor
from finrl.meta.preprocessor.preprocessors import FeatureEngineer
from finrl.config import INDICATORS
from utils.api_keys import APIKeys
from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
from finrl.agents.stablebaselines3.models import DRLAgent

# --- 1. 数据下载阶段 ---
BASE_URL = "https://paper-api.alpaca.markets"

# 初始化数据处理器（使用 Alpaca 接口）
dp = AlpacaProcessor(APIKeys.alpaca_key, APIKeys.alpaca_secret, BASE_URL)

# 下载 AAPL（苹果）数据。注意：实战中建议下载多只股票以增加环境复杂性
raw_df = dp.download_data(ticker_list=['AAPL'],
                          start_date='2023-01-01',
                          end_date='2024-01-01',
                          time_interval='1D')

# 1. 基础更名：FinRL 必须要有 'date' 和 'tic' 列
df = raw_df.copy()
df = df.rename(columns={'timestamp': 'date', 'symbol': 'tic'})

# 2. 核心修复：去除时区（Alpaca 返回的是带 UTC 的，必须去掉才能和后文匹配）
import pandas as pd
df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)

# 3. 排序：这是强化学习环境读取数据的唯一依据（按时间升序）
df = df.sort_values(['date', 'tic']).reset_index(drop=True)

# 4. 类型检查：确保数值列没有字符串
for col in ['open', 'high', 'low', 'close', 'volume']:
    df[col] = df[col].astype(float)

# 现在得到的 clean_df 就可以直接喂给 FeatureEngineer 了
clean_df = df

# --- 2. 特征工程 (关键修正) ---
# FinRL 默认寻找 'date' 列，而 Alpaca 返回的是 'timestamp'
if 'timestamp' in clean_df.columns:
    clean_df = clean_df.rename(columns={'timestamp': 'date'})

# 初始化特征工程：自动添加常用的技术指标（MACD, RSI, CCI, ADX 等）
fe = FeatureEngineer(use_technical_indicator=True,
                     tech_indicator_list=INDICATORS,
                     use_vix=False,
                     use_turbulence=False)

processed_df = fe.preprocess_data(clean_df)
processed_df = processed_df.fillna(0) # 将因计算指标产生的 NaN 填补为 0

# 确保数据格式符合强化学习要求
processed_df = processed_df.sort_values(['date', 'tic']).reset_index(drop=True)
for col in ['open', 'high', 'low', 'close', 'volume']:
    processed_df[col] = processed_df[col].astype(float)

# --- 3. 环境构建 ---
# 动态计算强化学习的状态空间维度
# 状态 = [余额] + [收盘价] * 数量 + [持有股数] * 数量 + [技术指标] * 数量
# 计算股票数量
stock_dimension = len(processed_df.tic.unique())
state_space = 1 + 2 * stock_dimension + len(INDICATORS) * stock_dimension

# 核心修复：手续费必须是列表，长度等于股票数量
# 哪怕只有一只股票，也要写成 [0.001]
buy_cost_list = [0.001] * stock_dimension
sell_cost_list = [0.001] * stock_dimension

env_kwargs = {
    "stock_dim": stock_dimension,
    "hmax": 100,
    "initial_amount": 100000,
    "num_stock_shares": [0] * stock_dimension,
    "buy_cost_pct": buy_cost_list,   # <--- 修复：由 float 改为 list
    "sell_cost_pct": sell_cost_list, # <--- 修复：由 float 改为 list
    "state_space": state_space,
    "action_space": stock_dimension,
    "tech_indicator_list": INDICATORS,
    "reward_scaling": 1e-4
}

# 之后再初始化环境
e_train_gym = StockTradingEnv(df=processed_df, **env_kwargs)

# --- 4. 模型训练 (Stable Baselines 3) ---
agent = DRLAgent(env=e_train_gym)

# 使用 PPO（近端策略优化）算法，适合连续动作空间且较稳定
model_ppo = agent.get_model("ppo")

print("正在训练 AI 交易员...")
# total_timesteps 建议至少设置在 50,000 以上才能看到收敛效果
trained_ppo = agent.train_model(model=model_ppo,
                                tb_log_name='ppo_trading_run',
                                total_timesteps=10000)

# 保存模型以便后续回测或实盘
trained_ppo.save("ppo_alpaca_model")