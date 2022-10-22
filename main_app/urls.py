from django.urls import path

import main_app.views as views

urlpatterns = [
    # Test
    path('test', views.TestView.as_view(), name='test'),

    # Predict
    path('predict', views.PredictView.as_view(), name='predict'),
    # History by engine
    path('get_history_by_engine', views.HistoryEngineView.as_view(), name='history_engine'),
    # History by engine type
    # Metrics by engine
]
