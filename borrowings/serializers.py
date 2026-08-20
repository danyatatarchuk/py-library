from django.db import transaction
from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    book = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )

    def get_book(self, obj):
        return {
            "id": obj.book.id,
            "title": obj.book.title,
            "author": obj.book.author,
            "cover": obj.book.cover,
            "daily_fee": str(obj.book.daily_fee),
        }


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "expected_return_date",
            "book",
        )

    def validate_book(self, book):
        if book.inventory <= 0:
            raise serializers.ValidationError(
                "This book is currently out of stock."
            )

        return book

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data["book"]

        with transaction.atomic():
            book.inventory -= 1
            book.save(update_fields=["inventory"])

            return Borrowing.objects.create(
                user=user,
                **validated_data,
            )
