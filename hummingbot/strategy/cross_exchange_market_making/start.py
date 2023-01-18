from typing import List, Tuple, cast

from hummingbot.client.settings import AllConnectorSettings
from hummingbot.connector.gateway.amm.gateway_evm_amm import GatewayEVMAMM
from hummingbot.connector.gateway.gateway_price_shim import GatewayPriceShim
from hummingbot.strategy.cross_exchange_market_making.cross_exchange_market_making import (
    CrossExchangeMarketMakingStrategy,
    LogOption,
)
from hummingbot.strategy.maker_taker_market_pair import MakerTakerMarketPair
from hummingbot.strategy.market_trading_pair_tuple import MarketTradingPairTuple
from hummingbot.connector.exchange

def start(self):
    c_map = self.strategy_config_map
    maker_market = c_map.maker_market.lower()  ## binance
    taker_market = c_map.taker_market.lower()  ## pancakeswap_binance-smart-chain_mainnet
    raw_maker_trading_pair = c_map.maker_market_trading_pair    ##BNB-USDT
    raw_taker_trading_pair = c_map.taker_market_trading_pair       ##WBNB-USDT
    status_report_interval = self.client_config_map.strategy_report_interval
    debug_price_shim = c_map.debug_price_shim

    try:
        maker_trading_pair: str = raw_maker_trading_pair
        taker_trading_pair: str = raw_taker_trading_pair
        maker_assets: Tuple[str, str] = self._initialize_market_assets(maker_market, [maker_trading_pair])[0]
        taker_assets: Tuple[str, str] = self._initialize_market_assets(taker_market, [taker_trading_pair])[0]
        """
        def _initialize_market_assets(market_name: str, trading_pairs: List[str]) -> List[Tuple[str, str]]:
            market_trading_pairs: List[Tuple[str, str]] = [(trading_pair.split('-')) for trading_pair in trading_pairs]
            return market_trading_pairs
        """
    except ValueError as e:
        self.notify(str(e))
        return

    market_names: List[Tuple[str, List[str]]] = [
        (maker_market, [maker_trading_pair]),
        (taker_market, [taker_trading_pair]),
    ]

    self._initialize_markets(market_names)
    maker_data = [self.markets[maker_market], maker_trading_pair] + list(maker_assets)
    taker_data = [self.markets[taker_market], taker_trading_pair] + list(taker_assets)
    
    # maker_market_trading_pair_tuple = MarketTradingPairTuple(*maker_data)
    # taker_market_trading_pair_tuple = MarketTradingPairTuple(*taker_data)
    # self.market_trading_pair_tuples = [maker_market_trading_pair_tuple, taker_market_trading_pair_tuple]
    # self.market_pair = MakerTakerMarketPair(maker=maker_market_trading_pair_tuple, taker=taker_market_trading_pair_tuple)
    # self.market_pair2 = MakerTakerMarketPair(maker=MarketTradingPairTuple(binance, "ETH/USDT", "ETH", "USDT"), taker=MarketTradingPairTuple())
    
    self.market_pair = MakerTakerMarketPair(maker=MarketTradingPairTuple(binance_paper_trade, "ETH-USDT", "ETH", "USDT"), taker=MarketTradingPairTuple(pancakeswap_binance-smart-chain_testnet, "ETH-USDT", "ETH", "USDT"))
    self.market_pair2 = MakerTakerMarketPair(maker=MarketTradingPairTuple(binance_paper_trade, "BNB-USDT", "BNB", "USDT"), taker=MarketTradingPairTuple(pancakeswap_binance-smart-chain_testnet, "WBNB-USDT", "WBNB", "USDT"))



    if taker_market in AllConnectorSettings.get_gateway_amm_connector_names():
        if debug_price_shim:
            amm_connector: GatewayEVMAMM = cast(GatewayEVMAMM, self.market_pair.taker.market)
            GatewayPriceShim.get_instance().patch_prices(
                maker_market,
                maker_trading_pair,
                amm_connector.connector_name,
                amm_connector.chain,
                amm_connector.network,
                taker_trading_pair
            )

    strategy_logging_options = (
        LogOption.CREATE_ORDER,
        LogOption.ADJUST_ORDER,
        LogOption.MAKER_ORDER_FILLED,
        LogOption.REMOVING_ORDER,
        LogOption.STATUS_REPORT,
        LogOption.MAKER_ORDER_HEDGED
    )
    self.strategy = CrossExchangeMarketMakingStrategy()
    self.strategy.init_params(
        config_map=c_map,
        market_pairs=[self.market_pair, self.market_pair2],
        status_report_interval=status_report_interval,
        logging_options=strategy_logging_options,
        hb_app_notification=True,
    )
