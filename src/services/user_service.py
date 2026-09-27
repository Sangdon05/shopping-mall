from dataclasses import asdict, dataclass
from typing import Literal

from postgrest.exceptions import APIError
from supabase import AuthApiError, AuthInvalidCredentialsError

from ..utils.time import get_timestamptz
from .base_service import BaseService


@dataclass(kw_only=True)
class Account:
    email: str
    password: str


@dataclass(kw_only=True)
class AccountInfo:
    type: Literal["BUYER", "SELLER"] | None = None
    cellphone: str | None = None
    zipcode: str | None = None
    address: str | None = None
    address_sub: str | None = None


class UserService(BaseService):
    # 회원가입
    def sign_up(self, account: Account):
        try:
            response = self.client.auth.sign_up(
                {
                    "email": account.email,
                    "password": account.password,
                }
            )

            if not response.user:
                raise RuntimeError("가입 중 오류가 발생하였습니다.")

            return response.user
        except AuthInvalidCredentialsError as e:
            raise RuntimeError("계정을 다시 확인해주세요.") from e
        except AuthApiError as e:
            raise RuntimeError("이미 가입된 계정입니다.") from e
        except APIError as e:
            match e.code:
                case "23502":
                    raise ValueError("필수 입력값 누락되었습니다.") from e
                case _:
                    raise RuntimeError("가입 시 문제가 발생하였습니다.") from e

    # 회원 상세 정보 입력하기
    def set_details(self, info: AccountInfo):
        try:
            user = self.get_user_info()
            response = (
                self.get_user_details_table()
                .select("id")
                .eq("id", user.id)
                .limit(1)
                .execute()
            )

            if len(response.data) != 0:
                # update info
                values = {k: v for k, v in asdict(info).items() if v != None}
                values["modified_at"] = get_timestamptz()
                response = (
                    self.get_user_details_table()
                    .update(values)
                    .eq("id", user.id)
                    .execute()
                )

                if response and response.data:
                    return response.data
                else:
                    raise RuntimeError("상세정보 업데이트에 실패하였습니다.")
            else:
                # insert info
                values = asdict(info)
                values["id"] = user.id
                response = self.get_user_details_table().insert(values).execute()

                if response and response.data:
                    return response.data
                else:
                    raise RuntimeError("상세정보 업데이트에 실패하였습니다.")
        except APIError as e:
            match e.code:
                case "23502":
                    raise ValueError("필수 입력값 누락되었습니다.") from e
                case _:
                    raise RuntimeError(
                        "사용자 정보 업데이트 시 문제가 발생하였습니다."
                    ) from e

    # 회원 상세 정보 가져오기
    def get_details(self) -> dict[str, any]:
        user = self.get_user_info()
        response = (
            self.get_user_details_table()
            .select("*")
            .eq("id", user.id)
            .is_("deleted_at", "null")
            .limit(1)
            .maybe_single()
            .execute()
        )

        if response and response.data:
            info = dict(response.data)
            info["email"] = user.email
            return info
        else:
            return {"email": user.email}

    # 로그인
    def login(self, account: Account):
        try:
            response = self.get_auth().sign_in_with_password(
                {"email": account.email, "password": account.password}
            )

            if response.user:
                return response.user
            else:
                raise PermissionError("사용자가 존재하지 않습니다.")
        except AuthApiError as e:
            raise PermissionError("사용자가 존재하지 않습니다.") from e
        except APIError as e:
            match e.code:
                case "23502":
                    raise ValueError("필수 입력값 누락되었습니다.") from e
                case _:
                    raise RuntimeError("로그인 시 문제가 발생하였습니다.") from e

    # 로그 아웃
    def logout(self):
        self.get_auth().sign_out()
