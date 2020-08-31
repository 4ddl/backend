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
        DynamicRoute(
            url=r'^{prefix}/{lookup}/{url_path}$',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'user_info',
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        )
    ]


router = AuthRouter()
router.register('', AuthViewSet, basename='user')
urlpatterns = router.urls
