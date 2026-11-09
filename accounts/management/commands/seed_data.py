"""Management command to seed the database with demo data."""

import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from jobs.models import Department, JobPosting
from candidates.models import CandidateProfile, Application
from interviews.models import Interview

User = get_user_model()

DEPARTMENTS = [
    ("Engineering", "Software development and infrastructure"),
    ("Marketing", "Brand, growth, and content marketing"),
    ("Design", "UI/UX and product design"),
    ("Human Resources", "People operations and talent acquisition"),
    ("Data Science", "Analytics, ML, and data engineering"),
    ("DevOps", "Infrastructure, CI/CD, and cloud operations"),
    ("Product", "Product management and strategy"),
    ("Sales", "Revenue and business development"),
]

JOBS = [
    {"title": "Software Developer", "type": "FULL_TIME", "level": "MID", "skills": ["Python", "Django", "REST", "PostgreSQL", "Git"]},
    {"title": "Systems Administrator", "type": "FULL_TIME", "level": "MID", "skills": ["Linux", "Docker", "AWS", "Ansible", "Terraform"]},
    {"title": "Cybersecurity Analyst", "type": "FULL_TIME", "level": "MID", "skills": ["Python", "Linux", "SQL", "Git"]},
    {"title": "Data Scientist", "type": "FULL_TIME", "level": "SENIOR", "skills": ["Python", "Machine Learning", "TensorFlow", "SQL", "NLP"]},
    {"title": "DevOps Engineer", "type": "FULL_TIME", "level": "SENIOR", "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Terraform"]},
    {"title": "Frontend Developer", "type": "FULL_TIME", "level": "MID", "skills": ["JavaScript", "React", "TypeScript", "CSS", "Tailwind"]},
    {"title": "UX Designer", "type": "FULL_TIME", "level": "MID", "skills": ["Figma", "CSS", "HTML"]},
    {"title": "Product Manager", "type": "FULL_TIME", "level": "SENIOR", "skills": ["Agile", "Scrum"]},
    {"title": "Backend Engineer", "type": "REMOTE", "level": "SENIOR", "skills": ["Python", "Django", "PostgreSQL", "Redis", "Docker"]},
    {"title": "ML Engineer", "type": "REMOTE", "level": "SENIOR", "skills": ["Python", "PyTorch", "Deep Learning", "Docker", "AWS"]},
]

CANDIDATE_NAMES = [
    ("Aminur", "Rahman"), ("Fatima", "Akter"), ("Ravi", "Kumar"),
    ("Sarah", "Johnson"), ("Chen", "Wei"), ("Priya", "Sharma"),
    ("James", "Wilson"), ("Aisha", "Hassan"), ("Carlos", "Garcia"),
    ("Yuki", "Tanaka"), ("Elena", "Petrov"), ("David", "Kim"),
    ("Nadia", "Ali"), ("Michael", "Brown"), ("Sophia", "Lee"),
]


class Command(BaseCommand):
    help = "Seed the database with demo data for SmartHire"

    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding SmartHire database...")

        # Create admin
        admin, _ = User.objects.get_or_create(
            email="admin@smarthire.com",
            defaults={"first_name": "Admin", "last_name": "User", "role": "ADMIN", "is_staff": True, "is_superuser": True, "is_verified": True},
        )
        if _:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Admin user created (admin@smarthire.com / admin123)"))

        # Create recruiter
        recruiter, _ = User.objects.get_or_create(
            email="recruiter@smarthire.com",
            defaults={"first_name": "HR", "last_name": "Manager", "role": "RECRUITER", "is_verified": True},
        )
        if _:
            recruiter.set_password("recruiter123")
            recruiter.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Recruiter user created"))

        # Departments
        dept_objs = {}
        for name, desc in DEPARTMENTS:
            dept, _ = Department.objects.get_or_create(name=name, defaults={"description": desc})
            dept_objs[name] = dept
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(DEPARTMENTS)} departments created"))

        # Jobs
        dept_names = list(dept_objs.keys())
        job_objs = []
        now = timezone.now()
        for i, j in enumerate(JOBS):
            status_choice = random.choice(["PUBLISHED", "PUBLISHED", "PUBLISHED", "ON_HOLD"])
            job, _ = JobPosting.objects.get_or_create(
                title=j["title"],
                posted_by=recruiter,
                defaults={
                    "department": dept_objs[dept_names[i % len(dept_names)]],
                    "description": f"We are looking for a talented {j['title']} to join our team.",
                    "requirements": f"Required skills: {', '.join(j['skills'])}. 2+ years experience.",
                    "responsibilities": f"As a {j['title']}, you will design, build, and maintain systems.",
                    "location": random.choice(["San Francisco, CA", "New York, NY", "Remote", "London, UK", "Berlin, DE"]),
                    "job_type": j["type"],
                    "experience_level": j["level"],
                    "salary_min": random.randint(60, 100) * 1000,
                    "salary_max": random.randint(110, 180) * 1000,
                    "openings": random.randint(2, 5),
                    "closed_count": random.randint(0, 3),
                    "deadline": (now + timedelta(days=random.randint(14, 90))).date(),
                    "status": status_choice,
                    "skills_required": j["skills"],
                },
            )
            job_objs.append(job)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(JOBS)} job postings created"))

        # Candidates
        candidate_users = []
        for first, last in CANDIDATE_NAMES:
            email = f"{first.lower()}.{last.lower()}@example.com"
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={"first_name": first, "last_name": last, "role": "CANDIDATE", "is_verified": True},
            )
            if _:
                user.set_password("candidate123")
                user.save()
            candidate_users.append(user)

            skills = random.sample(
                ["Python", "JavaScript", "React", "Django", "Docker", "AWS", "SQL", "Git", "Linux", "Machine Learning", "TypeScript", "Node.js"],
                k=random.randint(3, 7),
            )
            CandidateProfile.objects.get_or_create(
                user=user,
                defaults={
                    "skills": skills,
                    "experience_years": random.randint(1, 12),
                    "education": random.choice(["BSc Computer Science", "MSc Software Engineering", "PhD AI", "BEng IT", "MBA"]),
                    "current_company": random.choice(["Google", "Meta", "Amazon", "Microsoft", "Startup Inc", "Freelance", ""]),
                    "current_position": random.choice(["Developer", "Engineer", "Analyst", "Designer", "Manager", ""]),
                    "expected_salary": random.randint(50, 150) * 1000,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(CANDIDATE_NAMES)} candidates created"))

        # Applications
        statuses = ["NEW", "SCREENING", "QUALIFIED", "INTERVIEW_SCHEDULED", "INTERVIEWED", "OFFERED", "HIRED", "REJECTED"]
        app_count = 0
        for user in candidate_users:
            jobs_to_apply = random.sample(job_objs, k=min(random.randint(1, 4), len(job_objs)))
            for job in jobs_to_apply:
                if job.status != "PUBLISHED":
                    continue
                Application.objects.get_or_create(
                    candidate=user,
                    job=job,
                    defaults={
                        "status": random.choice(statuses),
                        "ai_match_score": round(random.uniform(20, 98), 1),
                        "cover_letter": f"I am excited to apply for the {job.title} position.",
                    },
                )
                app_count += 1
        self.stdout.write(self.style.SUCCESS(f"  ✓ {app_count} applications created"))

        # Interviews
        scheduled_apps = Application.objects.filter(status__in=["INTERVIEW_SCHEDULED", "INTERVIEWED"])
        interview_count = 0
        for app_obj in scheduled_apps[:20]:
            Interview.objects.get_or_create(
                application=app_obj,
                defaults={
                    "interviewer": recruiter,
                    "scheduled_at": now + timedelta(days=random.randint(1, 30), hours=random.randint(9, 17)),
                    "duration_minutes": random.choice([30, 45, 60, 90]),
                    "interview_type": random.choice(["PHONE", "VIDEO", "TECHNICAL", "HR"]),
                    "status": "COMPLETED" if app_obj.status == "INTERVIEWED" else "SCHEDULED",
                    "meeting_link": "https://meet.google.com/abc-defg-hij",
                },
            )
            interview_count += 1
        self.stdout.write(self.style.SUCCESS(f"  ✓ {interview_count} interviews created"))

        self.stdout.write(self.style.SUCCESS("\n✅ Database seeded successfully!"))
        self.stdout.write("   Login: admin@smarthire.com / admin123")
        self.stdout.write("   Login: recruiter@smarthire.com / recruiter123")
        self.stdout.write("   Login: aminur.rahman@example.com / candidate123")
