from rest_framework import routers

from .views import SystemViewSet

urlpatterns = []
router = routers.SimpleRouter()
router.register(r'', SystemViewSet, basename='system')
urlpatterns += router.urls
