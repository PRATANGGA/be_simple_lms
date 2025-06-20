from ninja import NinjaAPI, UploadedFile, File, Form, Router, Schema
from ninja.responses import Response
from typing import List
from lms_core.schema import CourseSchemaOut, CourseMemberOut, CourseSchemaIn
from lms_core.schema import CourseContentMini, CourseContentFull
from lms_core.schema import CourseCommentOut, CourseCommentIn
from lms_core.models import Course, CourseMember, CourseContent, Comment # Keep existing imports
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from ninja.pagination import paginate, PageNumberPagination
from django.contrib.auth.models import User
from rest_framework import status

from django.shortcuts import get_object_or_404

# Inisialisasi API dan otentikasi
apiAuth = HttpJwtAuth()
apiv1 = NinjaAPI()
apiv1.add_router("/auth/", mobile_auth_router)

# Router utama
router = Router()

# Hello endpoint
class HelloResponse(Schema):
    msg: str

@router.get("/hello", response=HelloResponse)
def hello(request):
    return {"msg": "Hello World"}

# List courses
@router.get("/courses", response=List[CourseSchemaOut])
@paginate(PageNumberPagination)
def list_courses(request):
    return Course.objects.all()

# Create course
@router.post("/courses", auth=apiAuth, response=CourseSchemaOut)
def create_course(
    request,
    name: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    file: UploadedFile = File(None),
):
    user = User.objects.create_user(username='hehehe',password='password123')

    # Ensure user is authenticated before creating a course
    # if not request.user.is_authenticated:
    #     return Response({"detail": "Authentication required."}, status=401)

    course = Course.objects.create(
        name=name,
        description=description,
        price=price,
        teacher=user, # request.user should now be a proper User object
    )
    return Response({"id": course.id, "name": course.name, "description": course.description, "price": course.price}, status=201 )

# Update course
@router.post("/courses/{course_id}", auth=apiAuth, response=CourseSchemaOut)
def update_course(
    request,
    course_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    file: UploadedFile = File(None),
):
    course = get_object_or_404(Course, id=course_id)
    course.name = name
    course.description = description
    course.price = price

    # Jika file di-upload, perbarui image
    if file:
        course.image.save(file.name, file.file, save=False)

    course.save()
    return course

from ninja.errors import HttpError

@router.post("/courses/{course_id}/enroll/")
def enroll_course(request, course_id: int):
    course = get_object_or_404(Course, id=course_id)

    user, created = User.objects.get_or_create(username="user", defaults={"password": "password"}) # temporary fix

    if CourseMember.objects.filter(course_id=course, user_id=user).exists():
        raise HttpError(400, "You are already enrolled in this course.")

    CourseMember.objects.create(course_id=course, user_id=user)
    return {"message": "Enrolled successfully"}



# Create comment
@router.post("/contents/{content_id}/comments/")
def create_comment(request, content_id: int, payload: CourseCommentIn):
    comment = payload.comment
    # user = request.user
    user, created = User.objects.get_or_create(username="user", defaults={"password": "password"}) 

    content = get_object_or_404(CourseContent, id=content_id)
    course = get_object_or_404(Course, id=content.course_id.id)
    member = get_object_or_404(CourseMember, user_id=user, course_id=course)

    user, created = User.objects.get_or_create(username="userr", defaults={"password": "password"}) # 

    if user != member.user_id:
        return Response({'error': 'You are not authorized to create comment in this content'}, status=status.HTTP_401_UNAUTHORIZED)

    comment = Comment.objects.create(
        content_id=content,
        member_id=member,
        comment=comment
    )

    return Response({
        "id": comment.id,
        "comment": comment.comment,
        "content_id": content.id
    }, status=201)

# Delete comment
@router.delete("/comments/{comment_id}", auth=apiAuth)
def delete_comment(request, comment_id: int):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=401)

    comment = get_object_or_404(Comment, id=comment_id)

    # Pastikan user adalah pemilik komentar lewat CourseMember
    if comment.member_id.user_id != user:
        return Response({'error': 'You are not authorized to delete this comment'}, status=403)

    comment.delete()
    return Response({"deleted": True}, status=200)



apiv1.add_router("/", router)