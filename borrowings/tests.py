from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing


User = get_user_model()


class BorrowingListDetailTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            first_name="Other",
            last_name="User",
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=Decimal("2.50"),
        )

        self.borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=7),
            book=self.book,
            user=self.user,
        )

        self.client.force_authenticate(user=self.user)

    def test_borrowing_list_returns_200(self):
        response = self.client.get("/api/borrowings/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_borrowing_list_contains_borrowing(self):
        response = self.client.get("/api/borrowings/")

        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["id"],
            self.borrowing.id,
        )

    def test_borrowing_list_contains_book_info(self):
        response = self.client.get("/api/borrowings/")

        self.assertEqual(
            response.data[0]["book"],
            {
                "id": self.book.id,
                "title": self.book.title,
                "author": self.book.author,
                "cover": "HARD",
                "daily_fee": "2.50",
            },
        )

    def test_borrowing_detail_returns_200(self):
        response = self.client.get(
            f"/api/borrowings/{self.borrowing.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_borrowing_detail_contains_book_info(self):
        response = self.client.get(
            f"/api/borrowings/{self.borrowing.id}/"
        )

        self.assertEqual(
            response.data["book"],
            {
                "id": self.book.id,
                "title": self.book.title,
                "author": self.book.author,
                "cover": "HARD",
                "daily_fee": "2.50",
            },
        )

    def test_borrowing_detail_contains_user(self):
        response = self.client.get(
            f"/api/borrowings/{self.borrowing.id}/"
        )

        self.assertEqual(
            response.data["user"],
            self.user.id,
        )

    def test_borrowing_detail_for_nonexistent_borrowing_returns_404(self):
        response = self.client.get("/api/borrowings/999/")

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_borrowing_list_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/borrowings/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_borrowing_detail_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            f"/api/borrowings/{self.borrowing.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_expected_return_date_cannot_be_before_borrow_date(self):
        borrowing = Borrowing(
            borrow_date=date.today(),
            expected_return_date=date.today() - timedelta(days=1),
            book=self.book,
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            borrowing.validate_constraints()

    def test_actual_return_date_cannot_be_before_borrow_date(self):
        borrowing = Borrowing(
            borrow_date=date.today(),
            expected_return_date=date.today() + timedelta(days=7),
            actual_return_date=date.today() - timedelta(days=1),
            book=self.book,
            user=self.user,
        )

        with self.assertRaises(ValidationError):
            borrowing.validate_constraints()


class BorrowingCreateTests(APITestCase):
    def setUp(self):
        self.email = "borrower@example.com"
        self.password = "testpassword123"

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            first_name="Test",
            last_name="User",
        )

        self.book = Book.objects.create(
            title="Available Book",
            author="Test Author",
            cover=Book.CoverType.HARD,
            inventory=3,
            daily_fee="2.50",
        )

        response = self.client.post(
            "/api/users/token/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.client.credentials(
            HTTP_AUTHORIZE=f"Bearer {response.data['access']}"
        )

    def test_create_borrowing(self):
        response = self.client.post(
            "/api/borrowings/",
            {
                "expected_return_date": "2026-08-30",
                "book": self.book.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        borrowing = Borrowing.objects.get()

        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(
            borrowing.expected_return_date.isoformat(),
            "2026-08-30",
        )

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)

    def test_cannot_create_borrowing_when_book_is_out_of_stock(self):
        self.book.inventory = 0
        self.book.save(update_fields=["inventory"])

        response = self.client.post(
            "/api/borrowings/",
            {
                "expected_return_date": "2026-08-30",
                "book": self.book.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("book", response.data)

        self.assertEqual(
            Borrowing.objects.count(),
            0,
        )

    def test_create_borrowing_requires_authentication(self):
        self.client.credentials()

        response = self.client.post(
            "/api/borrowings/",
            {
                "expected_return_date": "2026-08-30",
                "book": self.book.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_create_borrowing_with_invalid_book(self):
        response = self.client.post(
            "/api/borrowings/",
            {
                "expected_return_date": "2026-08-30",
                "book": 9999,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_create_borrowing_requires_expected_return_date(self):
        response = self.client.post(
            "/api/borrowings/",
            {
                "book": self.book.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
