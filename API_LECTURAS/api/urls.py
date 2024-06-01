from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'mediciones',views.MedicionesViewSet )


urlpatterns = [
    path("", include(router.urls) ),
    path(r"withvalidations/",views.post_medicion_with_validations),
    path(r"getdata/",views.get_medicion_between_range),
    path(r"getlast/",views.get_last)
]