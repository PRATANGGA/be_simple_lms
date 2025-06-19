from django.test import TestCase
from django.contrib.auth.models import User
from lms_core.models import Course, CourseMember, CourseContent, Comment
from lms_core.api import apiv1
import json

class APITestCase(TestCase):
    base_url = '/api/v1/'

    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher',password='password123')
        self.student = User.objects.create_user(username='student', password='password123')
        self.course = Course.objects.create(
            name = "Django for Beginners",
            description = "Learn Django from scratch",
            price = 9000,
            teacher = self.teacher
        )
        login = self.client.post(self.base_url+'auth/sign-in',data=json.dumps({
            'username': 'teacher',
            'password': 'password123'
        }), content_type='application/json')
        self.token = login.json()['access']
        login = self.client.post(self.base_url+'auth/sign-in',data=json.dumps({
            'username': 'student',
            'password':'password123'
        }), content_type='application/json')
        self.student_token = login.json()['access']

    def test_list_courses(self):
        response = self.client.get(f'{self.base_url}courses')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['items']), 1)

    def test_create_course(self):
        response = self.client.post(self.base_url+'courses', data={
            'name': 'New Course',
            'description': 'New Course Description',
            'price': 150,
            'file': {'image': None}
        }, format='multipart', **{'HTTP_AUTHORIZATION': 'Bearer ' + str(self.token)})
        # print(response.request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['name'], 'New Course')