from django.urls import path

import main_app.views as views

urlpatterns = [
    # Test
    path('test', views.TestView.as_view(), name='test'),
]
