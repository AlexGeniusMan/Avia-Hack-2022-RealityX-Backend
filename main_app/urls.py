from django.urls import path

import main_app.views as views

urlpatterns = [
    # Predict
    path('predict', views.PredictView.as_view(), name='predict'),
    # History by engine
    path('get_history_by_engine', views.HistoryEngineView.as_view(), name='history_engine'),
    # Metric by engine, datetime and phase
    path('get_metric', views.MetricView.as_view(), name='metric'),
]
