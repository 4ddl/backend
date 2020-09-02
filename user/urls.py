from rest_framework.routers import SimpleRouter

from user.views import AuthViewSet, AdvancedUserViewSet

router = SimpleRouter()
router.register('advanced', AdvancedUserViewSet, basename='advanced-user')
router.register('', AuthViewSet, basename='user')
urlpatterns = router.urls
