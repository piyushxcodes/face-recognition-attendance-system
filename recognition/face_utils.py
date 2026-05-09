import cv2
import os
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime
from django.conf import settings
from .models import Student, Attendance


# Haarcascade path
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


# -----------------------------
# CAPTURE FACE SAMPLES
# -----------------------------
def capture_face_samples(student_id, name):
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    detector = cv2.CascadeClassifier(CASCADE_PATH)

    sample_num = 0

    # Save inside media/TrainingImage
    save_path = settings.MEDIA_ROOT / "TrainingImage"
    save_path.mkdir(parents=True, exist_ok=True)

    while True:
        ret, img = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(50, 50)
        )

        for (x, y, w, h) in faces:
            sample_num += 1

            face = gray[y:y+h, x:x+w]

            file_name = save_path / f"user.{student_id}.{sample_num}.jpg"

            cv2.imwrite(
                str(file_name),
                face
            )

            cv2.rectangle(
                img,
                (x, y),
                (x + w, y + h),
                (255, 0, 0),
                2
            )

            cv2.putText(
                img,
                f"Sample: {sample_num}/500",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        cv2.imshow("Capturing Face Samples - Press Q to Quit", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if sample_num >= 500:
            break

    cam.release()
    cv2.destroyAllWindows()

    return sample_num


# -----------------------------
# GET TRAINING IMAGES
# -----------------------------
def get_images_and_labels(path):
    if not os.path.exists(path):
        return [], []

    image_paths = [
        os.path.join(path, file)
        for file in os.listdir(path)
        if file.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    face_samples = []
    ids = []

    for image_path in image_paths:
        try:
            pil_image = Image.open(image_path).convert("L")
            image_np = np.array(pil_image, "uint8")

            file_name = os.path.split(image_path)[-1]

            # Expected: user.<student_id>.<sample>.jpg
            parts = file_name.split(".")

            if len(parts) < 4:
                continue

            student_id = parts[1]

            # Keep only numeric IDs if possible
            if not str(student_id).isdigit():
                numeric_id = "".join(filter(str.isdigit, str(student_id)))

                if not numeric_id:
                    continue

                student_id = numeric_id

            ids.append(int(student_id))
            face_samples.append(image_np)

        except Exception:
            continue

    return face_samples, ids


# -----------------------------
# TRAIN MODEL
# -----------------------------
def train_faces():
    training_path = settings.MEDIA_ROOT / "TrainingImage"

    label_path = settings.MEDIA_ROOT / "TrainingImageLabel"
    label_path.mkdir(parents=True, exist_ok=True)

    model_path = label_path / "Trainner.yml"

    if not training_path.exists():
        return False

    faces, ids = get_images_and_labels(str(training_path))

    if len(faces) == 0 or len(ids) == 0:
        return False

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.train(
        faces,
        np.array(ids)
    )

    recognizer.save(str(model_path))

    return True


# -----------------------------
# MARK ATTENDANCE
# -----------------------------
def mark_attendance(student_id):
    try:
        student = Student.objects.get(student_id=str(student_id))
    except Student.DoesNotExist:
        return

    now = datetime.now()
    today = now.date()

    # Prevent duplicate attendance
    already_marked = Attendance.objects.filter(
        student=student,
        date=today
    ).exists()

    if already_marked:
        return

    Attendance.objects.create(
        student=student,
        date=today,
        time=now.time(),
        status="Present"
    )

    # Ensure attendance folder exists
    attendance_dir = settings.ATTENDANCE_DIR
    attendance_dir.mkdir(parents=True, exist_ok=True)

    csv_file = attendance_dir / f"Attendance_{today}.csv"

    data = {
        "ID": [student.student_id],
        "Name": [student.name],
        "Department": [student.department],
        "Date": [str(today)],
        "Time": [now.strftime("%H:%M:%S")],
        "Status": ["Present"]
    }

    df = pd.DataFrame(data)

    if csv_file.exists():
        df.to_csv(
            csv_file,
            mode="a",
            header=False,
            index=False
        )
    else:
        df.to_csv(
            csv_file,
            index=False
        )


# -----------------------------
# LIVE FACE RECOGNITION
# -----------------------------
def recognize_and_attend():
    model_path = settings.MEDIA_ROOT / "TrainingImageLabel" / "Trainner.yml"

    if not model_path.exists():
        return "Model not trained"

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(model_path))

    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        ret, img = cam.read()

        if not ret:
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(50, 50)
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(
                img,
                (x, y),
                (x + w, y + h),
                (225, 0, 0),
                2
            )

            try:
                predicted_id, confidence = recognizer.predict(
                    gray[y:y+h, x:x+w]
                )

                # Lower confidence = better match
                if confidence < 60:
                    try:
                        student = Student.objects.get(
                            student_id=str(predicted_id)
                        )

                        display_text = f"{student.name} ({student.student_id})"

                        mark_attendance(predicted_id)

                    except Student.DoesNotExist:
                        display_text = "Unknown"

                else:
                    display_text = "Unknown"

            except Exception:
                display_text = "Unknown"

            cv2.putText(
                img,
                display_text,
                (x, y - 10),
                font,
                0.8,
                (255, 255, 255),
                2
            )

        cv2.imshow("Live Attendance - Press Q to Quit", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()

    return "Attendance completed"