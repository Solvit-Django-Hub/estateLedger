from django.urls import path
from .views import (
    EstateListCreateView,
    EstateDetailView,
    UnitListCreateView,
    UnitDetailView,
    UnitClaimListCreateView,
    UnitClaimDetailView,
    EstateMembershipListCreateView,
    EstateMembershipDetailView,
)

urlpatterns = [
    path("estates/", EstateListCreateView.as_view(), name="estate-list-create"),
    path("estates/<int:pk>/", EstateDetailView.as_view(), name="estate-detail"),

    path("units/", UnitListCreateView.as_view(), name="unit-list-create"),
    path("units/<int:pk>/", UnitDetailView.as_view(), name="unit-detail"),

    path("claims/", UnitClaimListCreateView.as_view(), name="claim-list-create"),
    path("claims/<int:pk>/", UnitClaimDetailView.as_view(), name="claim-detail"),
    path("claims/<int:pk>/approve/", UnitClaimDetailView.as_view(), name="claim-approval"),

    path("memberships/", EstateMembershipListCreateView.as_view(), name="membership-list-create",),
    path("memberships/<int:pk>/",EstateMembershipDetailView.as_view(),name="membership-detail",)
]