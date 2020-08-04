from rest_framework.routers import SimpleRouter, DynamicRoute

from user.views import AuthViewSet


class AuthRouter(SimpleRouter):
    routes = [
        DynamicRoute(
            url=r'^{prefix}/{url_path}/$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        )
    ]


router = AuthRouter()
router.register('', AuthViewSet, basename='user')
urlpatterns = router.urls
