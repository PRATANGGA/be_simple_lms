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
from django.contrib.auth.models import User # Keep existing imports
from django.shortcuts import get_object_or_404

# Inisialisasi API dan otentikasi
apiv1 = NinjaAPI()
apiAuth = HttpJwtAuth()
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
    # Ensure user is authenticated before creating a course
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=401)

    course = Course.objects.create(
        name=name,
        description=description,
        price=price,
        teacher=request.user, # request.user should now be a proper User object
    )
    return course

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
    # Ensure user is authenticated
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=401)

    course = get_object_or_404(Course, id=course_id)
    # Check if the authenticated user is the teacher of the course
    if course.teacher != request.user:
        return Response({"detail": "Unauthorized: You are not the teacher of this course."}, status=403)
    course.name = name
    course.description = description
    course.price = price
    course.save()
    return course

# Enroll course
@router.post("/courses/{course_id}/enroll", auth=apiAuth)
def enroll_course(request, course_id: int):
    # Ensure user is authenticated
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=401)

    course = get_object_or_404(Course, id=course_id)
    # Use request.user directly, which should be authenticated
    CourseMember.objects.get_or_create(course_id=course, user_id=request.user)
    return {"enrolled": True}

# Create comment
@router.post("/contents/{content_id}/comments", auth=apiAuth, response=CourseCommentOut)
def create_comment(request, content_id: int, payload: CourseCommentIn):
    # Ensure user is authenticated
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=401)

    content = get_object_or_404(CourseContent, id=content_id)
    try:
        # Fetch the CourseMember instance using the authenticated user
        member = CourseMember.objects.get(course_id=content.course_id, user_id=request.user)
    except CourseMember.DoesNotExist:
        return Response({"detail": "Anda belum tergabung dalam kursus ini"}, status=403)

    comment = Comment.objects.create(
        member_id=member,
        content_id=content,
        comment=payload.comment,
    )
    return comment

# Delete comment
@router.delete("/comments/{comment_id}", auth=apiAuth)
def delete_comment(request, comment_id: int):
    # Ensure user is authenticated
    if not request.user.is_authenticated:
        return Response({"detail": "Authentication required."}, status=401)

    comment = get_object_or_404(Comment, id=comment_id)
    # Check if the authenticated user is the one who made the comment
    if comment.member_id.user_id != request.user:
        return Response({"detail": "Forbidden: You can only delete your own comments."}, status=403)
    comment.delete()
    return {"deleted": True}

# Tambahkan router utama ke API
apiv1.add_router("/", router)