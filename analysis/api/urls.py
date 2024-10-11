from django.urls import path

from .views import AnalysisOptionsView, GenerateAnalysisView

urlpatterns = [
    path("analysis/options/", AnalysisOptionsView.as_view(), name="options"),
    path("analysis/generate/", GenerateAnalysisView.as_view(), name="generate"),
]