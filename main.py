import os
from getpass import getpass

from dotenv import load_dotenv
from supabase import Client, create_client

from src.services.order_service import OrderInfo, OrderItemInfo, OrderService
from src.services.product_service import ProductInfo, ProductService
from src.services.user_service import Account, AccountInfo, UserService

load_dotenv()

url: str = os.getenv("SUPABASE_URL") or ""
key: str = os.getenv("SUPABASE_ANON_KEY") or ""

if not url and not key:
    raise ValueError("url과 key를 확인해 주세요.")

client: Client = create_client(url, key)
user_service = UserService(client)
product_service = ProductService(client)
order_service = OrderService(client)


def signup(
    email: str,
    password: str,
    confirm_password: str,
    isCustomer: bool = True,
    cellphone: str | None = None,
    zipcode: str | None = None,
    address: str | None = None,
    address_sub: str | None = None,
):
    try:
        user_service.sign_up(Account(email=email, password=password), confirm_password)
        user_service.set_details(
            AccountInfo(
                type="BUYER" if isCustomer else "SELLER",
                cellphone=cellphone,
                zipcode=zipcode,
                address=address,
                address_sub=address_sub,
            )
        )
        print("회원가입이 완료되었습니다. 서비스 이용을 위해 로그인해 주세요.")

    except Exception as e:
        print(e)


def signout():
    user_service.logout()


def update_details(
    cellphone: str | None = None,
    zipcode: str | None = None,
    address: str | None = None,
    address_sub: str | None = None,
):
    try:
        user_service.set_details(
            AccountInfo(
                cellphone=cellphone,
                zipcode=zipcode,
                address=address,
                address_sub=address_sub,
            )
        )
        print("회원 정보를 업데이하였습니다.")
    except Exception as e:
        print(e)


def sign_in_with_password(email: str, password: str):
    try:
        user_service.login(Account(email=email, password=password))
        print("로그인 완료되었습니다.")
    except Exception as e:
        print(e)


def add_product(name: str, description: str, price: int):
    try:
        product_service.add(
            ProductInfo(name=name, description=description, price=price)
        )
        print("상품 등록이 완료되었습니다.")
    except Exception as e:
        print(e)


def search_product(keyword: str):
    try:
        products = product_service.search(keyword=keyword)
        for product in products:
            print(
                f"이름: {product['name']}, 가격: {product['price']}, ID: {product['id']}"
            )
    except Exception as e:
        print(e)


def update_product(
    product_id: str,
    name: str | None = None,
    description: str | None = None,
    price: int | None = None,
):
    try:
        product_service.update(
            product_id, ProductInfo(name=name, description=description, price=price)
        )
        print("상품 업데이트 완료하였습니다.")
    except Exception as e:
        print(e)


def delete_product(product_id: str):
    try:
        product_service.delete(product_id)
        print("상품을 삭제하였습니다.")
    except Exception as e:
        print(e)


def check_seller() -> bool:
    return user_service.get_user_type() == "SELLER"


def product_order(
    order_name: str,
    receiver_name: str,
    receiver_phone: str,
    zipcode: str,
    address: str,
    address_sub: str,
    delivery_memo: str,
    products: list[dict],
):
    try:
        user_details = user_service.get_details()
        order_service.order(
            OrderInfo(
                p_order_name=order_name,
                p_order_email=user_details["email"],
                p_order_phone=user_details["cellphone"],
                p_receiver_name=receiver_name,
                p_receiver_phone=receiver_phone,
                p_zipcode=zipcode,
                p_address=address,
                p_address_sub=address_sub,
                p_delivery_memo=delivery_memo,
                p_items=[
                    OrderItemInfo(
                        product_id=product["product_id"], quantity=product["quantity"]
                    )
                    for product in products
                ],
            )
        )
        print("상품 주문을 완료하였습니다.")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    while True:
        select_number = input(
            "1) 일반 회원 가입\n"
            "2) 점주 회원 가입\n"
            "3) 로그인\n"
            "4) 상품 검색\n"
            "5) 상품 등록\n"
            "6) 상품 삭제\n"
            "7) 상품 주문\n"
            "8) 로그아웃\n"
        )

        if not select_number.isdigit():
            print("숫자 입력해 주세요.")
            continue
        select_number = int(select_number)
        match select_number:
            case 1 | 2:
                step = 1
                data = {}
                while True:
                    match step:
                        case 1:
                            data["email"] = input("이메일: ")
                        case 2:
                            data["password"] = getpass("비밀번호: ")
                        case 3:
                            data["confirm_password"] = getpass("비밀번호 확인: ")
                            if data["password"] != data["confirm_password"]:
                                break
                        case 4:
                            data["cellphone"] = input("전화번호: ")
                        case 5:
                            data["zipcode"] = input("우편번호: ")
                        case 6:
                            data["address"] = input("주소: ")
                        case 7:
                            data["address_sub"] = input("상세 주소: ")
                            break
                    step += 1

                signup(**data, isCustomer=select_number == 1)
            case 3:
                step = 1
                data = {}
                while True:
                    match step:
                        case 1:
                            data["email"] = input("이메일: ")
                        case 2:
                            data["password"] = getpass("비밀번호: ")
                            break
                    step += 1

                sign_in_with_password(**data)
            case 4:
                keyword = input("상품명: ")
                search_product(keyword)
            case 5:
                if not check_seller():
                    print("판매자 계정이 아닙니다.")
                    continue
                step = 1
                data = {}
                while True:
                    match step:
                        case 1:
                            data["name"] = input("상품명: ")
                        case 2:
                            data["description"] = input("상품상세: ")
                        case 3:
                            data["price"] = input("가격: ")
                            break
                    step += 1

                add_product(**data)
            case 6:
                if not check_seller():
                    print("판매자 계정이 아닙니다.")
                    continue
                product_id = input("상품 ID: ")
                delete_product(product_id)
            case 7:
                if check_seller():
                    print("일반회원 계정이 아닙니다.")
                    continue

                step = 1
                data = {}
                while True:
                    match step:
                        case 1:
                            data["order_name"] = input("주문자 이름: ")
                        case 2:
                            data["receiver_name"] = input("받는이 이름: ")
                        case 3:
                            data["receiver_phone"] = input("받는이 연락처: ")
                        case 4:
                            data["zipcode"] = input("받는이 우편번호: ")
                        case 5:
                            data["address"] = input("받는이 주소: ")
                        case 6:
                            data["address_sub"] = input("받는이 상세주소: ")
                        case 7:
                            data["delivery_memo"] = input("메모: ")
                        case 8:
                            products = []
                            isContinue = True
                            while isContinue:
                                product_step = 1
                                product = {}
                                while True:
                                    match product_step:
                                        case 1:
                                            product["product_id"] = input("상품 ID: ")
                                        case 2:
                                            product["quantity"] = input("상품 개수: ")
                                            break
                                    product_step += 1
                                products.append(product)
                                input_value = input("1) 상품 추가\n2) 주문하기\n")
                                if not input_value.isdigit():
                                    print("잘못된 입력입니다. 주문하기로 진행합니다.")
                                    isContinue = False
                                isContinue = int(input_value) == 1
                            data["products"] = products
                            break

                    step += 1
                product_order(**data)
            case 8:
                signout()

    # user_service = UserService(client)
    # 일반 사용자 테스트
    # user_service.sign_up(
    #     Account(
    #         email="user03@test.com",
    #         password="password1234",
    #     ),
    #     confirm_password="password1234",
    # )
    # user_service.login(Account(email="user01@test.com", password="password1234"))
    # print(user_service.get_details())
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
    # print(user_service.get_user_type())
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
