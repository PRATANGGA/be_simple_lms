from locust import HttpUser, TaskSet, task, between
import json

class UserBehavior(TaskSet):
    def on_start(self):
        # Login user dan mendapatkan token
        self.login()

    def login(self):
        response = self.client.post("/auth/sign-in", json={
            "username": "LarissaWylie",  # Ganti dengan username yang valid
            "password": "RLS71GOH8GF"    # Ganti dengan password yang valid
        })
        if response.status_code == 200:
            self.token = response.json().get("access")
        else:
            print("Login failed:", response.text)
            self.token = None

    @task(1)
    def get_my_courses(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get("/mycourses", headers=headers)

        if response.status_code == 200:
            courses = response.json()
            if courses:
                course_id = courses[0]['course_id']['id']
                self.get_course_contents(course_id)

    def get_course_contents(self, course_id):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.get(f"/courses/{course_id}/contents", headers=headers)

        if response.status_code == 200:
            contents = response.json()
            if contents:
                content_id = contents[0]['id']
                self.post_comment(content_id)

    def post_comment(self, content_id):
        headers = {"Authorization": f"Bearer {self.token}"}
        comment_data = {"comment": "This is a test comment."}
        response = self.client.post(f"/contents/{content_id}/comments", json=comment_data, headers=headers)

        if response.status_code == 201:
            comment_id = response.json().get("id")
            self.delete_comment(comment_id)

    def delete_comment(self, comment_id):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.client.delete(f"/comments/{comment_id}", headers=headers)
        if response.status_code == 200:
            print("Comment deleted:", response.json())
        else:
            print("Failed to delete comment:", response.status_code, response.text)


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 2)
