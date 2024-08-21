from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import HistoricalRecord
import json

class HistoricalRecordListView(View):
    def get(self, request):
        records = HistoricalRecord.objects.all().values()
        return JsonResponse(list(records), safe=False)

    @method_decorator(csrf_exempt)
    def post(self, request):
        data = json.loads(request.body)
        new_record = HistoricalRecord.objects.create(
            user_name=data['userName'],
            user_action=data['userAction'],
            user_email=data['userEmail'],
            timestamp=data['timestamp']
        )
        return JsonResponse({"message": "Record added successfully", "record_id": new_record.id})
