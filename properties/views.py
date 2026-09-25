
# Create your views here.
from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import Estate, Unit, UnitClaim, EstateMembership
from .serializers import (
    EstateSerializer, 
    UnitSerializer, 
    UnitClaimSerializer, 
    UnitClaimApprovalSerializer,
    EstateMembershipSerializer
    
)

@extend_schema(
    tags=["Estates"],
    summary="List or create estates",
)
class EstateListCreateView(generics.ListCreateAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

@extend_schema(
    tags=["Estates"],
    summary="Retrieve, update or delete an estate",
)
class EstateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Estate.objects.all()
    serializer_class = EstateSerializer

@extend_schema(
    tags=["Units"],
    summary="List or create units",
)
class UnitListCreateView(generics.ListCreateAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

@extend_schema(
    tags=["Units"],
    summary="Retrieve, update or delete a unit",
)
class UnitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

@extend_schema(
    tags=["Unit Claims"],
    summary="List or create unit claims",
)
class UnitClaimListCreateView(generics.ListCreateAPIView):
    queryset = UnitClaim.objects.all()
    serializer_class = UnitClaimSerializer
@extend_schema(
    tags=["Unit Claims"],
    summary="Retrieve, update or delete a unit claim",
)
class UnitClaimDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UnitClaim.objects.all()
    serializer_class = UnitClaimSerializer
@extend_schema(
    tags=["Unit Claims"],
    summary="Approve or reject a unit claim",
)
class UnitClaimApprovalView(generics.UpdateAPIView):
    queryset = UnitClaim.objects.all()
    serializer_class = UnitClaimApprovalSerializer
@extend_schema(
    tags=["Estate Memberships"],
    summary="List or create estate memberships",
)
class EstateMembershipListCreateView(generics.ListCreateAPIView):
    queryset = EstateMembership.objects.all()
    serializer_class = EstateMembershipSerializer

@extend_schema(
    tags=["Estate Memberships"],
    summary="Retrieve, update or delete an estate membership",
)
class EstateMembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EstateMembership.objects.all()
    serializer_class = EstateMembershipSerializer