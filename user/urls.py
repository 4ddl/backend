from rest_framework.routers import Route, SimpleRouter

from user.views import AuthViewSet


class AuthRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}$',
            mapping={'get': 'info'},
            name='{basename}-info',
            detail=False,
            initkwargs={'suffix': 'Info'}
        ),
        Route(
            url=r'^{prefix}$',
            mapping={'post': 'login'},
            name='{basename}-login',
            detail=False,
            initkwargs={'suffix': 'Login'}
        ),
        Route(
            url=r'^{prefix}/{lookup}/activate$',
            mapping={'post': 'activate'},
            name='{basename}-activate',
            detail=True,
            initkwargs={'suffix': 'Activate'}
        ),
        Route(
            url=r'^{prefix}$',
            mapping={'put': 'register'},
            name='{basename}-register',
            detail=False,
            initkwargs={'suffix': 'Register'}
        ),
        Route(
            url=r'^{prefix}$',
            mapping={'delete': 'logout'},
            name='{basename}-logout',
            detail=False,
            initkwargs={'suffix': 'Logout'}
        ),
    ]


router = AuthRouter()
router.register('auth', AuthViewSet, basename='user')
urlpatterns = router.urls
