# distutils: language=c++

from hummingbot.core.data_type.limit_order cimport LimitOrder
from hummingbot.core.time_iterator cimport TimeIterator


cdef class OrderTracker(TimeIterator):
    cdef:
        dict _tracked_limit_orders      ##@@##  {market_pair,  {order_id，LimitOrder} },  记录限价单信息，比市价单多了个price成员
        dict _tracked_market_orders     ##@@##  {market_pair,  {order_id，MarketOrder} }， 记录市价单信息
        dict _order_id_to_market_pair   ## {orderid, market_pair}
        dict _shadow_tracked_limit_orders
        dict _shadow_order_id_to_market_pair
        object _shadow_gc_requests
        object _in_flight_cancels               ## {order_id, timestamp when call "c_check_and_track_cancel()"}
        object _in_flight_pending_created       ## update by c_add_create_order_pending()

    cdef dict c_get_limit_orders(self)      ## return: _tracked_limit_orders
    cdef dict c_get_market_orders(self)     ## return: _tracked_market_orders
    cdef dict c_get_shadow_limit_orders(self)

    cdef bint c_has_in_flight_cancel(self, str order_id)
    cdef bint c_check_and_track_cancel(self, str order_id)

    cdef object c_get_market_pair_from_order_id(self, str order_id)
    cdef object c_get_shadow_market_pair_from_order_id(self, str order_id)

    cdef LimitOrder c_get_limit_order(self, object market_pair, str order_id)
    cdef object c_get_market_order(self, object market_pair, str order_id)
    cdef LimitOrder c_get_shadow_limit_order(self, str order_id)

    cdef c_start_tracking_limit_order(self, object market_pair, str order_id, bint is_buy, object price,
                                      object quantity)      ##@@## 记录 order_id, market_pair 到 _tracked_limit_orders 表中
    cdef c_stop_tracking_limit_order(self, object market_pair, str order_id)        ## 清理 _tracked_limit_orders， _order_id_to_market_pair， _in_flight_cancels; 放入 _shadow_gc_requests 队列
    cdef c_start_tracking_market_order(self, object market_pair, str order_id, bint is_buy, object quantity)            ## update _tracked_market_orders
    cdef c_stop_tracking_market_order(self, object market_pair, str order_id)       ## 清理 _tracked_market_orders， _order_id_to_market_pair

    cdef c_check_and_cleanup_shadow_records(self)
    cdef c_add_create_order_pending(self, str order_id)
    cdef c_remove_create_order_pending(self, str order_id)



##

# MarketOrder(
#             order_id,
#             market_pair.trading_pair,
#             is_buy,
#             market_pair.base_asset,
#             market_pair.quote_asset,
#             float(quantity),
#             self._current_timestamp
#         )
# LimitOrder(order_id,
#             market_pair.trading_pair,
#             is_buy,
#             market_pair.base_asset,
#             market_pair.quote_asset,
#             price,
#             quantity,
#             creation_timestamp=int(self._current_timestamp * 1e6))