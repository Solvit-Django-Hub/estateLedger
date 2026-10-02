
# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
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
    queryset = Estate.objects.all().order_by("id")
    serializer_class = EstateSerializer

@extend_schema(
    tags=["Estates"],
    summary="Retrieve, update or delete an estate",
)
class EstateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Estate.objects.all().order_by("id")
    serializer_class = EstateSerializer

@extend_schema(
    tags=["Units"],
    summary="List or create units",
)
class UnitListCreateView(generics.ListCreateAPIView):
    queryset = Unit.objects.all().order_by("id")
    serializer_class = UnitSerializer
    def create(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)

            return Response(
                {
                    "message": "Unit created successfully.",
                    "unit": serializer.data,
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
@extend_schema(
    tags=["Units"],
    summary="Retrieve, update or delete a unit",
)
class UnitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Unit.objects.all().order_by("id")
    serializer_class = UnitSerializer

@extend_schema(
    tags=["Unit Claims"],
    summary="List or create unit claims",
)
class UnitClaimListCreateView(generics.ListCreateAPIView):
    queryset = UnitClaim.objects.all().order_by("id")
    serializer_class = UnitClaimSerializer
@extend_schema(
    tags=["Unit Claims"],
    summary="Retrieve or delete a unit claim",
)
class UnitClaimDetailView(generics.RetrieveDestroyAPIView):
    queryset = UnitClaim.objects.all().order_by("id")
    serializer_class = UnitClaimSerializer
    permission_classes = [IsAuthenticated]
@extend_schema(
    tags=["Unit Claims"],
    summary="Approve or reject a unit claim",
)
class UnitClaimApprovalView(generics.UpdateAPIView):
    queryset = UnitClaim.objects.all().order_by("id")
    serializer_class = UnitClaimApprovalSerializer
@extend_schema(
    tags=["Estate Memberships"],
    summary="List or create estate memberships",
)
class EstateMembershipListCreateView(generics.ListCreateAPIView):
    queryset = EstateMembership.objects.all().order_by("id")
    serializer_class = EstateMembershipSerializer

@extend_schema(
    tags=["Estate Memberships"],
    summary="Retrieve, update or delete an estate membership",
)
class EstateMembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EstateMembership.objects.all().order_by("id")
    serializer_class = EstateMembershipSerializer