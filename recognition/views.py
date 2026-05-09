from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import StudentRegistrationForm
from .models import Student, Attendance
from .face_utils import (
    capture_face_samples,
    train_faces,
    recognize_and_attend
)


def home(request):
    total_students = Student.objects.count()
    total_attendance = Attendance.objects.count()

    context = {
        "total_students": total_students,
        "total_attendance": total_attendance,
    }

    return render(request, "home.html", context)


def register_student(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            student_id = form.cleaned_data["student_id"]
            name = form.cleaned_data["name"]
            department = form.cleaned_data["department"]
            admin_password = form.cleaned_data["admin_password"]

            if admin_password != settings.ADMIN_PASSWORD:
                messages.error(request, "Invalid admin password")
                return redirect("register_student")

            if Student.objects.filter(student_id=student_id).exists():
                messages.error(request, "Student ID already exists")
                return redirect("register_student")

            Student.objects.create(
                student_id=student_id,
                name=name,
                department=department
            )

            try:
                capture_face_samples(student_id, name)
                messages.success(
                    request,
                    f"Student {name} registered successfully with face samples captured."
                )

            except Exception as e:
                messages.error(request, f"Camera error: {str(e)}")

            return redirect("home")

    else:
        form = StudentRegistrationForm()

    return render(request, "register.html", {"form": form})


def train_model(request):
    try:
        success = train_faces()

        if success:
            messages.success(request, "Face recognition model trained successfully.")
        else:
            messages.error(request, "No training images found.")

    except Exception as e:
        messages.error(request, f"Training failed: {str(e)}")

    return redirect("home")


def take_attendance(request):
    try:
        result = recognize_and_attend()

        if result == "Model not trained":
            messages.error(request, "Please train the model first.")
        else:
            messages.success(request, "Attendance marked successfully.")

    except Exception as e:
        messages.error(request, f"Attendance failed: {str(e)}")

    return redirect("home")


def attendance_report(request):
    records = Attendance.objects.select_related("student").order_by("-date", "-time")

    return render(
        request,
        "attendance.html",
        {
            "records": records
        }
    )