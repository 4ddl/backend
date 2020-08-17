from rest_framework.routers import SimpleRouter, DynamicRoute, Route

from user.views import AuthViewSet


class AuthRouter(SimpleRouter):
    routes = [
        DynamicRoute(
            url=r'^{prefix}/{url_path}/$',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        )
    ]


router = AuthRouter()
router.register('', AuthViewSet, basename='user')
urlpatterns = router.urls
