
# Create your views here.
from rest_framework import generics
from .models import Estate, Unit, UnitClaim, EstateMembership
from .serializers import (
    EstateSerializer, 
    UnitSerializer, 
    UnitClaimSerializer, 
    UnitClaimApprovalSerializer,
    EstateMembershipSerializer
    
)


class EstateListCreateView(generics.ListCreateAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer


class EstateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer


class UnitListCreateView(generics.ListCreateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


class UnitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

class UnitClaimListCreateView(generics.ListCreateAPIView):
    queryset = UnitClaim.objects.all()
    serializer_class = UnitClaimSerializer

class UnitClaimDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UnitClaim.objects.all()
    serializer_class = UnitClaimSerializer

class UnitClaimApprovalView(generics.UpdateAPIView):
    queryset = UnitClaim.objects.all()
    serializer_class = UnitClaimApprovalSerializer

class EstateMembershipListCreateView(generics.ListCreateAPIView):
    queryset = EstateMembership.objects.all()
    serializer_class = EstateMembershipSerializer
class EstateMembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EstateMembership.objects.all()
    serializer_class = EstateMembershipSerializer