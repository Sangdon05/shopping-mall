from dataclasses import asdict, dataclass

from postgrest.exceptions import APIError

from ..utils.time import get_timestamptz
from .base_service import BaseService


@dataclass(kw_only=True)
class ProductInfo:
    name: str | None = None
    description: str | None = None
    price: int | None = None


class ProductService(BaseService):
    def search(
        self,
        keyword: str = "",
        seller_id: str | None = None,
        product_id: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ):
        try:
            query = self.get_products_table().select("*")

            if seller_id:
                query = query.eq("seller_id", seller_id)

            if product_id:
                query = query.eq("id", product_id)

            keyword = keyword.strip()
            if keyword:
                query = query.or_(
                    f"name.ilike.%{keyword}%,description.ilike.%{keyword}%"
                )

            response = (
                query.is_("deleted_at", "null")
                .offset(offset * limit)
                .limit(limit)
                .execute()
            )

            return response.data
        except APIError as e:
            match e.code:
                case "23502":
                    raise ValueError("필수 입력값 누락되었습니다.") from e
                case _:
                    raise RuntimeError("검색 시 문제가 발생하였습니다.") from e

    def add(self, info: ProductInfo):
        try:
            user_type = self.get_user_type()
            if user_type != "SELLER":
                raise PermissionError("상품 등록 권한이 없습니다.")

            values = asdict(info)
            values["seller_id"] = self.get_user_info().id
            response = self.get_products_table().insert(values).execute()

            if response and response.data:
                return response.data
            else:
                raise RuntimeError("상품 추가에 실패하였습니다.")
        except APIError as e:
            match e.code:
                case "23502":
                    raise ValueError("필수 입력값 누락되었습니다.") from e
                case _:
                    raise RuntimeError("상품 추가 시 문제가 발생하였습니다.") from e

    def update(self, product_id: str, info: ProductInfo):
        try:
            user = self.get_user_info()
            values = {k: v for k, v in asdict(info).items() if v != None}
            values["modified_at"] = get_timestamptz()
            response = (
                self.get_products_table()
                .update(values)
                .eq("seller_id", user.id)
                .eq("id", product_id)
                .execute()
            )

            if response and response.data:
                return response.data
            else:
                raise RuntimeError("상품 업데이트에 실패하였습니다.")

        except APIError as e:
            match e.code:
                case "23502":
                    raise ValueError("필수 입력값 누락되었습니다.") from e
                case _:
                    raise RuntimeError(
                        "상품 정보 업데이트 시 문제가 발생하였습니다."
                    ) from e

    def delete(self, product_id: str):
        try:
            user = self.get_user_info()
            response = (
                self.get_products_table()
                .update({"deleted_at": get_timestamptz()})
                .eq("seller_id", user.id)
                .eq("id", product_id)
                .execute()
            )

            if response and response.data:
                return response.data
            else:
                raise RuntimeError("상품 삭제에 실패하였습니다.")
        except APIError as e:
            match e.code:
                case "23502":
                    raise ValueError("필수 입력값 누락되었습니다.") from e
                case _:
                    raise RuntimeError("상품 삭제 시 문제가 발생하였습니다.") from e
