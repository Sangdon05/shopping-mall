from postgrest import SyncRequestBuilder
from supabase import Client
from supabase._sync.auth_client import SyncSupabaseAuthClient


class BaseService:
    def __init__(self, client: Client):
        self.client = client

    def get_user_info(self):
        response = self.get_auth().get_user()
        if not response:
            raise PermissionError("로그인 필수 기능입니다. 로그인이 필요합니다.")

        return response.user

    def get_user_details_table(self) -> SyncRequestBuilder:
        return self.client.table("user_details")

    def get_products_table(self) -> SyncRequestBuilder:
        return self.client.table("products")

    def get_orders_table(self) -> SyncRequestBuilder:
        return self.client.table("orders")

    def get_order_items_table(self) -> SyncRequestBuilder:
        return self.client.table("order_items")

    def get_auth(self) -> SyncSupabaseAuthClient:
        return self.client.auth

    def get_user_type(self) -> str:
        user = self.get_user_info()
        response = (
            self.get_user_details_table()
            .select("type")
            .eq("id", user.id)
            .limit(1)
            .maybe_single()
            .execute()
        )

        if response and response.data:
            return response.data["type"]
        else:
            raise ValueError("회원 정보가 없습니다.")
