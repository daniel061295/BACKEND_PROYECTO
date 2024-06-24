from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

router = DefaultRouter()
router.register(r'mediciones',views.MedicionesViewSet )


urlpatterns = [
    path("", include(router.urls) ),
    path(r"withvalidations/",views.post_medicion_with_validations),
    path(r"getdata/",views.get_medicion_between_range),
    path(r"getlast/",views.get_last),
    re_path("login", views.login, name="login"),
    re_path("register", views.register, name="register"),
    re_path("downloadcsv", views.download_csv, name="download_csv")
]