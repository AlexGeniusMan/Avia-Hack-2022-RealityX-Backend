from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.models import User
from project.permissions import CustomIsAuthenticated


class TestView(APIView):
    """ Test """
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):

        return Response(status=status.HTTP_200_OK, data={
            'message': 'Ok.',
        })

