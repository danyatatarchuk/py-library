from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingSerializer,
)


class BorrowingListCreateView(ListCreateAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BorrowingCreateSerializer

        return BorrowingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(user=user)

            user_id = self.request.query_params.get("user_id")
            if user_id and user_id != str(user.id):
                return queryset.none()

        elif self.request.query_params.get("user_id"):
            queryset = queryset.filter(
                user_id=self.request.query_params["user_id"]
            )

        is_active = self.request.query_params.get("is_active")

        if is_active == "true":
            queryset = queryset.filter(
                actual_return_date__isnull=True
            )
        elif is_active == "false":
            queryset = queryset.filter(
                actual_return_date__isnull=False
            )

        return queryset


class BorrowingDetailView(RetrieveAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]
