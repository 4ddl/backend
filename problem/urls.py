from django.urls import path
from rest_framework import routers

from problem.views import ProblemViewSet, ProblemImageAPI, ProblemPDFAPI

router = routers.SimpleRouter()
router.register(r'', ProblemViewSet, basename='problem')
urlpatterns = router.urls
urlpatterns += [
    path('image', ProblemImageAPI.as_view()),
    path('pdf', ProblemPDFAPI.as_view()),
]
