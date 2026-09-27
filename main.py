import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

url: str = os.getenv("SUPABASE_URL") or ""
key: str = os.getenv("SUPABASE_ANON_KEY") or ""

if not url and not key:
    raise ValueError("url과 key를 확인해 주세요.")

client: Client = create_client(url, key)

if __name__ == "__main__":
    from src.services.order_service import OrderInfo, OrderItemInfo, OrderService
    from src.services.product_service import ProductInfo, ProductService
    from src.services.user_service import Account, AccountInfo, UserService

    user_service = UserService(client)
    # 일반 사용자 테스트
    # user_service.sign_up(Account(email="user01@test.com", password="password1234"))
    user_service.login(Account(email="user01@test.com", password="password1234"))
    # user_service.set_info(
    #     AccountInfo(
    #         type="BUYER",
    #         cellphone="010-0000-0000",
    #         zipcode="1000",
    #         address="addres",
    #         address_sub="address_sub",
    #     )
    # )
    # user_service.set_info(
    #     AccountInfo(zipcode="20000", address="addres", address_sub="address_sub")
    # )
    # print(user_service.get_details())
    # print(product_service.search())

    # 판매자 테스트
    # user_service.sign_up(Account(email="user02@test.com", password="password1234"))
    # user_service.login(Account(email="user02@test.com", password="password1234"))
    # user_service.set_details(
    #     AccountInfo(
    #         type="SELLER",
    #         cellphone="010-0300-0300",
    #         zipcode="4000",
    #         address="addres 2",
    #         address_sub="address_sub 2",
    #     )
    # )

    # 상품 테스트
    product_service = ProductService(client)
    # print(
    #     product_service.add(
    #         ProductInfo(
    #             name="스파르타 JS 교안",
    #             description="JS 기초 학습 가능",
    #             price=15000,
    #         )
    #     )
    # )
    # print(product_service.search("학습"))
    # print(product_service.search())
    # print(
    #     product_service.update(
    #         "5d36cda8-c532-464f-a85b-a1c3e5f540dc",
    #         ProductInfo(
    #             name="스파르타 파이썬 교안 (수정)",
    #             price=25000,
    #         ),
    #     )
    # )
    # print(
    #     product_service.delete(
    #         "5d36cda8-c532-464f-a85b-a1c3e5f540dc",
    #     )
    # )

    # 주문 테스트
    # order_service = OrderService(client)
    # user = order_service.get_user_info()
    # user_details = user_service.get_details()
    # print(
    #     order_service.order(
    #         OrderInfo(
    #             p_order_name="김철수",
    #             p_order_email=user.email,
    #             p_order_phone=user_details["cellphone"],
    #             p_receiver_name="이영희",
    #             p_receiver_phone="010-1234-5678",
    #             p_zipcode="3200",
    #             p_address="받는사람 주소",
    #             p_address_sub="받는사람 상세 주소",
    #             p_delivery_memo="문앞에 두세요.",
    #             p_items=[
    #                 OrderItemInfo(
    #                     product_id="5d36cda8-c532-464f-a85b-a1c3e5f540dc", quantity=1
    #                 ),
    #                 OrderItemInfo(
    #                     product_id="0d8100d4-3ce9-42d7-aa59-ad4b505211d4", quantity=2
    #                 ),
    #             ],
    #         )
    #     )
    # )
