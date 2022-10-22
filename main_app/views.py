from pprint import pprint

import requests
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from dateutil import parser
from main_app.models import User, Session, Prediction, Metric, MetricValue
from project.permissions import CustomIsAuthenticated


class TestView(APIView):
    """ Test """
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        return Response(status=status.HTTP_200_OK, data={
            'message': 'Ok.',
        })


class HistoryEngineView(APIView):
    """ History by engine """
    permission_classes = [CustomIsAuthenticated]

    def get(self, request):
        if not request.GET.get('session_id'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': 'No session_id provided.',
            })
        if Session.objects.filter(id=request.GET.get('session_id')).exists():
            session = Session.objects.get(id=request.GET.get('session_id'))
            data = {}
            for prediction in Prediction.objects.filter(session=session):
                data[prediction.flight_phase] = {}

            for prediction in Prediction.objects.filter(session=session):
                data[prediction.flight_phase][prediction.engine_id] = {}

            for prediction in Prediction.objects.filter(session=session):
                metric_values = MetricValue.objects.filter(prediction=prediction)
                for metric_value in metric_values:
                    if 'metrics' in data[prediction.flight_phase][prediction.engine_id]:
                        if metric_value.metric_name.name not in data[prediction.flight_phase][prediction.engine_id]['metrics']:
                            data[prediction.flight_phase][prediction.engine_id]['metrics'].append(
                                metric_value.metric_name.name)
                    else:
                        data[prediction.flight_phase][prediction.engine_id]['metrics'] = []

            # session = Session.objects.get(id=request.GET.get('session_id'))
            # predictions = Prediction.objects.filter(session=session)
            # engines = {}
            # for prediction in predictions:
            #     engines[prediction.engine_id] = {
            #         'metrics': {}
            #     }
            # for prediction in predictions:
            #     metric_values = MetricValue.objects.filter(prediction=prediction)
            #     for metric_value in metric_values:
            #         metric_names = Metric.objects.filter(id=metric_value.metric_name.id)
            #         for metric_name in metric_names:
            #             if metric_name.name in engines[prediction.engine_id]['metrics']:
            #                 engines[prediction.engine_id]['metrics'][metric_name.name].append(prediction.flight_phase)
            #             else:
            #                 engines[prediction.engine_id]['metrics'][metric_name.name] = []
            # print(engines)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={
                'message': 'No session with such id.',
            })

        return Response(status=status.HTTP_200_OK, data={
            'data': data,
        })

    def post(self, request):
        if not request.data.get('engine_id'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': 'No engine_id provided.',
            })
        if not request.data.get('metric'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': 'No metric provided.',
            })
        if not request.data.get('phase'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                'message': 'No phase provided.',
            })
        data = []
        if Session.objects.filter(id=request.data.get('session_id')).exists():
            session = Session.objects.get(id=request.data.get('session_id'))
            predictions = (Prediction.objects.
                           filter(session=session)
                           .filter(engine_id=request.data.get('engine_id'))
                           .filter(flight_phase=request.data.get('phase'))
                           .filter(metric_values__metric_name__name__exact=request.data.get('metric'))
                           )
            for prediction in predictions:
                data.append({
                    'datetime': prediction.flight_datetime,
                    'value': prediction.metric_values.get(metric_name__name__exact=request.data.get('metric')).value,
                })

                # metric_values = MetricValue.objects.filter(prediction=prediction)
                # for metric_value in metric_values:
                #     if metric_value.metric_name.name == request.data.get('metric'):


        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={
                'message': 'No session with such id.',
            })

        return Response(status=status.HTTP_200_OK, data={
            'data': data,
        })


class PredictView(APIView):
    """ Predict """
    permission_classes = [CustomIsAuthenticated]

    def post(self, request):
        file = request.FILES['file']

        # ml_url = 'http://localhost:5000/predict'
        ml_url = 'http://ml:5000/predict'
        response = requests.post(ml_url, files=dict(file=file))
        session = Session.objects.create(
            user=request.user
        )
        # session.save()
        for prediction in response.json():
            prediction_db = Prediction.objects.create(
                session=session,
                flight_phase=prediction['flight_phase'],
                flight_datetime=parser.parse(prediction['flight_datetime']),
                engine_id=prediction['engine_id']
            )
            for metric in prediction['metrics'].items():
                if metric[1] is not None:
                    if not Metric.objects.filter(name=metric[0]).exists():
                        metric_db = Metric.objects.create(
                            name=metric[0]
                        )
                    else:
                        metric_db = Metric.objects.get(name=metric[0])
                    MetricValue.objects.create(
                        metric_name=metric_db,
                        prediction=prediction_db,
                        value=metric[1]
                    )

        return Response(status=status.HTTP_200_OK, data={
            'session_id': session.id,
        })
