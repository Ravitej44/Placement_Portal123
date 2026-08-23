from django.contrib import admin
from .models import Student, Company, Application


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'cgpa', 'backlogs', 'resume_link')
    list_filter = ('branch',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def resume_link(self, obj):
        if obj.resume:
            return obj.resume.url
        return "—"
    resume_link.short_description = "Resume"


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'job_role', 'package_lpa', 'drive_date', 'application_deadline', 'min_cgpa', 'has_login')
    list_filter = ('drive_date',)
    search_fields = ('name', 'job_role')
    raw_id_fields = ('user',)
    fieldsets = (
        ('Company Login (optional)', {
            'fields': ('user',),
            'description': (
                "To let this company log in and manage its own applicants: first create a User "
                "under Auth &rsaquo; Users (uncheck 'staff status'), then select it here."
            ),
        }),
        ('Drive Details', {
            'fields': ('name', 'description', 'job_role', 'package_lpa', 'drive_date', 'application_deadline'),
        }),
        ('Eligibility Criteria', {
            'fields': ('eligible_branches', 'min_cgpa', 'max_backlogs_allowed', 'required_skills'),
        }),
    )

    def has_login(self, obj):
        return obj.user is not None
    has_login.boolean = True
    has_login.short_description = "Company Login"


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'company', 'status', 'interview_datetime', 'applied_on')
    list_filter = ('status', 'company')
    search_fields = ('student__user__username', 'company__name')
    fields = (
        'student', 'company', 'status', 'remarks',
        'interview_datetime', 'interview_mode', 'interview_location',
    )

    # Note: interview fields only make sense once status reaches INTERVIEW,
    # but left editable regardless so the cell can schedule ahead of time.
