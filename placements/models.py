from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    BRANCH_CHOICES = [
        ('CSE', 'Computer Engineering'),
        ('IT', 'Information Technology'),
        ('ENTC', 'Electronics & Telecom'),
        ('MECH', 'Mechanical'),
        ('CIVIL', 'Civil'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    backlogs = models.PositiveIntegerField(default=0)
    skills = models.CharField(max_length=300, help_text="Comma-separated, e.g. Python, Django, HTML")
    phone = models.CharField(max_length=15, blank=True)
    resume = models.FileField(
        upload_to='resumes/', blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="PDF only, max 5 MB."
    )

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.branch})"

    def skills_list(self):
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def get_completion_percentage(self):
        fields_to_check = [
            self.branch,
            self.cgpa,
            self.skills,
            self.phone,
            self.resume,
        ]
        
        # Count how many of these fields have data filled in
        completed = sum(1 for field in fields_to_check if field)
        total = len(fields_to_check)
        
        return int((completed / total) * 100) if total > 0 else 0


class Company(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='company_profile',
        help_text="Login account for this company, created by the Placement Cell (optional)."
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    job_role = models.CharField(max_length=200)
    package_lpa = models.DecimalField(max_digits=6, decimal_places=2, help_text="Package in LPA")
    drive_date = models.DateField()
    application_deadline = models.DateField()

    # Eligibility criteria fields (kept on Company for simplicity — could be split out)
    eligible_branches = models.CharField(
        max_length=200, blank=True,
        help_text="Comma-separated branch codes, e.g. CSE,IT (leave blank for all branches)"
    )
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    max_backlogs_allowed = models.PositiveIntegerField(default=0)
    required_skills = models.CharField(
        max_length=300, blank=True,
        help_text="Comma-separated, optional. Leave blank if no specific skill required."
    )

    def __str__(self):
        return f"{self.name} - {self.job_role}"

    def eligible_branch_list(self):
        if not self.eligible_branches.strip():
            return None  # None means "all branches allowed"
        return [b.strip().upper() for b in self.eligible_branches.split(',') if b.strip()]

    def required_skill_list(self):
        return [s.strip().lower() for s in self.required_skills.split(',') if s.strip()]

    def is_eligible(self, student: Student):
        """Core eligibility engine: returns (bool, list_of_reasons_if_not_eligible)."""
        reasons = []

        branches = self.eligible_branch_list()
        if branches is not None and student.branch not in branches:
            reasons.append(f"Branch {student.get_branch_display()} not eligible.")

        if student.cgpa < self.min_cgpa:
            reasons.append(f"CGPA {student.cgpa} below required {self.min_cgpa}.")

        if student.backlogs > self.max_backlogs_allowed:
            reasons.append(f"Backlogs ({student.backlogs}) exceed allowed ({self.max_backlogs_allowed}).")

        required = self.required_skill_list()
        if required:
            student_skills = [s.lower() for s in student.skills_list()]
            missing = [s for s in required if s not in student_skills]
            if missing:
                reasons.append(f"Missing required skills: {', '.join(missing)}.")

        return (len(reasons) == 0, reasons)


class Application(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW', 'Interview'),
        ('SELECTED', 'Selected'),
        ('REJECTED', 'Rejected'),
    ]

    INTERVIEW_MODE_CHOICES = [
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='applications')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    applied_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    remarks = models.TextField(blank=True)

    # Interview scheduling
    interview_datetime = models.DateTimeField(blank=True, null=True)
    interview_mode = models.CharField(max_length=10, choices=INTERVIEW_MODE_CHOICES, blank=True)
    interview_location = models.CharField(
        max_length=300, blank=True,
        help_text="Venue address (offline) or meeting link (online)"
    )

    class Meta:
        unique_together = ('student', 'company')
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.student} -> {self.company} [{self.status}]"

    def has_interview_scheduled(self):
        return bool(self.interview_datetime)
