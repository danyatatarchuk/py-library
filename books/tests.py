from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book


User = get_user_model()


class BookCRUDTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="adminpassword123",
            is_staff=True,
        )

        self.user = User.objects.create_user(
            email="user@example.com",
            password="userpassword123",
        )

        self.book = Book.objects.create(
            title="The Hobbit",
            author="J.R.R. Tolkien",
            cover=Book.CoverType.HARD,
            inventory=5,
            daily_fee=Decimal("2.50"),
        )

        self.list_url = reverse("book-list")
        self.detail_url = reverse(
            "book-detail",
            kwargs={"pk": self.book.pk},
        )

    def test_create_book(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            "title": "1984",
            "author": "George Orwell",
            "cover": Book.CoverType.SOFT,
            "inventory": 10,
            "daily_fee": "3.00",
        }

        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(response.data["title"], "1984")

    def test_list_books(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "The Hobbit")

    def test_retrieve_book(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "The Hobbit")
        self.assertEqual(response.data["inventory"], 5)

    def test_update_book(self):
        self.client.force_authenticate(user=self.admin)

        data = {
            "title": "The Hobbit Updated",
            "author": "J.R.R. Tolkien",
            "cover": Book.CoverType.SOFT,
            "inventory": 10,
            "daily_fee": "3.00",
        }

        response = self.client.put(self.detail_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.book.refresh_from_db()
        self.assertEqual(self.book.title, "The Hobbit Updated")
        self.assertEqual(self.book.inventory, 10)

    def test_partial_update_book(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            self.detail_url,
            {"inventory": 7},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 7)
        self.assertEqual(self.book.title, "The Hobbit")

    def test_delete_book(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Book.objects.filter(pk=self.book.pk).exists()
        )

    def test_unauthenticated_user_cannot_create_book(self):
        data = {
            "title": "1984",
            "author": "George Orwell",
            "cover": Book.CoverType.SOFT,
            "inventory": 10,
            "daily_fee": "3.00",
        }

        response = self.client.post(self.list_url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_regular_user_cannot_create_book(self):
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "1984",
            "author": "George Orwell",
            "cover": Book.CoverType.SOFT,
            "inventory": 10,
            "daily_fee": "3.00",
        }

        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_update_book(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.detail_url,
            {"inventory": 10},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_delete_book(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_can_list_books(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_can_retrieve_book(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
