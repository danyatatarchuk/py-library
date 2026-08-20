from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class UserRegistrationTests(APITestCase):
    def test_create_user(self):
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
        }

        response = self.client.post("/api/users/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], data["email"])
        self.assertNotIn("password", response.data)

        user = User.objects.get(email=data["email"])
        self.assertTrue(user.check_password(data["password"]))

    def test_email_must_be_unique(self):
        User.objects.create_user(
            email="test@example.com",
            password="password123",
        )

        data = {
            "email": "test@example.com",
            "first_name": "Another",
            "last_name": "User",
            "password": "password123",
        }

        response = self.client.post("/api/users/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_is_required(self):
        data = {
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
        }

        response = self.client.post("/api/users/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_is_required(self):
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }

        response = self.client.post("/api/users/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.email = "jwt@example.com"
        self.password = "testpassword123"

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            first_name="JWT",
            last_name="Test",
        )

    def test_obtain_token_pair(self):
        response = self.client.post(
            "/api/users/token/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_with_invalid_password(self):
        response = self.client.post(
            "/api/users/token/",
            {
                "email": self.email,
                "password": "wrongpassword",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        response = self.client.post(
            "/api/users/token/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        refresh_token = response.data["refresh"]

        refresh_response = self.client.post(
            "/api/users/token/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("access", refresh_response.data)

    def test_refresh_with_invalid_token(self):
        response = self.client.post(
            "/api/users/token/refresh/",
            {
                "refresh": "invalid-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class UserMeTests(APITestCase):
    def setUp(self):
        self.email = "me@example.com"
        self.password = "testpassword123"

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            first_name="Test",
            last_name="User",
        )

        response = self.client.post(
            "/api/users/token/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.access_token = response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZE=f"Bearer {self.access_token}"
        )

    def test_get_my_profile(self):
        response = self.client.get("/api/users/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], self.email)
        self.assertEqual(response.data["first_name"], "Test")
        self.assertEqual(response.data["last_name"], "User")

    def test_update_my_profile_with_patch(self):
        response = self.client.patch(
            "/api/users/me/",
            {
                "first_name": "Updated",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Updated")

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_update_my_profile_with_put(self):
        response = self.client.put(
            "/api/users/me/",
            {
                "email": "updated@example.com",
                "first_name": "Updated",
                "last_name": "User",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["email"],
            "updated@example.com",
        )

        self.user.refresh_from_db()
        self.assertEqual(
            self.user.email,
            "updated@example.com",
        )

    def test_profile_requires_authentication(self):
        self.client.credentials()

        response = self.client.get("/api/users/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
