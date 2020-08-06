from rest_framework import routers
from problem.views import ProblemViewSet, ProblemImageAPI
from django.urls import path

router = routers.SimpleRouter()
router.register(r'', ProblemViewSet, basename='problem')
urlpatterns = router.urls
urlpatterns += [
    path('image', ProblemImageAPI.as_view()),
]
