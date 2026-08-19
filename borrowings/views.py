from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer


class BorrowingListView(ListAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]


class BorrowingDetailView(RetrieveAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]
