from django.http import JsonResponse
from .serializers import LeadSerializer
from .models import Lead
# third party imports

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework import mixins


class TestView(APIView):
    def get(self, request, *args, **kwargs):
        lead = Lead.objects.all()
        serializer = LeadSerializer(lead, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)

        
        
""" USING CLASSES MIXINS AND Generics """

class LeadListView(generics.ListAPIView):
    permission_classes = [AllowAny,]

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    
    
class LeadCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny,]
    
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    
        
class LeadUpdateView(generics.UpdateAPIView):
    permission_classes = LeadSerializer
    queryset = Lead.objects.all()
    lookup_field = 'pk'
    
    
class LeadDeleteView(generics.DestroyAPIView):
    serializer_class = LeadSerializer
    queryset = Lead.objects.all()
    lookup_field = 'pk'
    
class LeadRetrieveView(generics.RetrieveAPIView):
    serializer_class = LeadSerializer
    queryset = Lead.objects.all()
    lookup_field = 'pk'
    
    
    
""" 
def test_drf(request):
    student_age = [23, 45, 50]
    data = {"message": "Hello dear", "age": student_age}
    return JsonResponse(data, safe=False) """
