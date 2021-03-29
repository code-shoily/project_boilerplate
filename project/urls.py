import debug_toolbar
from django.contrib import admin
from django.urls import include, path

from web.api.urls import api_v1

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include(debug_toolbar.urls)),
    path("api/v1/", api_v1.urls),
]
