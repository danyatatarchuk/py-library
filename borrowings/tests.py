from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing


User = get_user_model()


class BorrowingListDetailTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User",
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee="2.50",
        )

        self.borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )

        response = self.client.post(
            "/api/users/token/",
            {
                "email": "test@example.com",
                "password": "testpassword123",
            },
            format="json",
        )

        self.access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZE=f"Bearer {self.access_token}"
        )

    def test_get_borrowings_list(self):
        response = self.client.get("/api/borrowings/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)

    def test_get_borrowing_detail(self):
        response = self.client.get(
            f"/api/borrowings/{self.borrowing.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["id"],
            self.borrowing.id,
        )
        self.assertEqual(
            response.data["user"],
            self.user.id,
        )

    def test_borrowing_detail_contains_book_info(self):
        response = self.client.get(
            f"/api/borrowings/{self.borrowing.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["book"],
            {
                "id": self.book.id,
                "title": self.book.title,
                "author": self.book.author,
                "cover": "HARD",
                "daily_fee": Decimal("2.50"),
            },
        )

    def test_borrowings_list_requires_authentication(self):
        self.client.credentials()

        response = self.client.get("/api/borrowings/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_borrowing_detail_requires_authentication(self):
        self.client.credentials()

        response = self.client.get(
            f"/api/borrowings/{self.borrowing.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
