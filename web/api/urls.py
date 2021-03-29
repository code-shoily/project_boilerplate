from ninja import NinjaAPI

from web.api.v1 import accounts

api_v1 = NinjaAPI(version="1.0.0")

api_v1.add_router("/accounts/", accounts.router)
