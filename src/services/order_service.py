from dataclasses import asdict, dataclass

from postgrest.exceptions import APIError

from .base_service import BaseService


@dataclass(kw_only=True)
class OrderItemInfo:
    product_id: str
    quantity: int = 1


@dataclass(kw_only=True)
class OrderInfo:
    p_order_name: str
    p_order_email: str
    p_order_phone: str
    p_receiver_name: str
    p_receiver_phone: str
    p_zipcode: str
    p_address: str
    p_address_sub: str = ""
    p_delivery_memo: str
    p_items: list[OrderItemInfo]


class OrderService(BaseService):
    def order(self, order: OrderInfo):
        try:
            user = self.get_user_info()
            user_type = self.get_user_type()
            if user_type != "BUYER":
                raise PermissionError("상품 구매는 일반 계정으로만 가능합니다.")

            if not order.p_items:
                raise ValueError("주문 상품정보가 올바르지 않습니다.")

            values = asdict(order)
            values["p_user_id"] = user.id
            response = self.client.rpc("create_order_transaction", values).execute()

            if response and response.data:
                return response.data
            else:
                raise RuntimeError("상품 주문에 실패하였습니다.")
        except APIError as e:
            match e.code:
                case "23502":
                    raise ValueError("필수 입력값 누락되었습니다.") from e
                case _:
                    raise RuntimeError("서버에 문제가 발생하였습니다.") from e
