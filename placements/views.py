from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages

from .forms import SignUpForm, StudentProfileForm, ApplicationUpdateForm
from .models import Student, Company, Application


class PlacementLoginView(LoginView):
    template_name = 'registration/login.html'


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            auth_login(request, user)
            return redirect('complete_profile')
    else:
        form = SignUpForm()
    return render(request, 'placements/signup.html', {'form': form})


@login_required
def complete_profile_view(request):
    if hasattr(request.user, 'company_profile'):
        return redirect('company_dashboard')

    student, _ = Student.objects.get_or_create(
        user=request.user,
        defaults={'branch': 'CSE', 'cgpa': 0, 'skills': ''}
    )
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('dashboard')
    else:
        form = StudentProfileForm(instance=student)
    return render(request, 'placements/profile.html', {'form': form})


@login_required
def dashboard_view(request):
    if hasattr(request.user, 'company_profile'):
        return redirect('company_dashboard')

    student = get_object_or_404(Student, user=request.user)
    applications = student.applications.select_related('company')
    applied_company_ids = set(applications.values_list('company_id', flat=True))

    companies = []
    for company in Company.objects.all().order_by('drive_date'):
        eligible, reasons = company.is_eligible(student)
        companies.append({
            'company': company,
            'eligible': eligible,
            'reasons': reasons,
            'already_applied': company.id in applied_company_ids,
        })

    return render(request, 'placements/dashboard.html', {
        'student': student,
        'companies': companies,
        'applications': applications,
    })


@login_required
def apply_view(request, company_id):
    if hasattr(request.user, 'company_profile'):
        return redirect('company_dashboard')

    student = get_object_or_404(Student, user=request.user)
    company = get_object_or_404(Company, id=company_id)
    eligible, reasons = company.is_eligible(student)

    if not eligible:
        messages.error(request, "You are not eligible for this drive: " + " ".join(reasons))
        return redirect('dashboard')

    Application.objects.get_or_create(student=student, company=company)
    messages.success(request, f"Applied to {company.name} successfully.")
    return redirect('dashboard')


@login_required
def company_dashboard_view(request):
    company = get_object_or_404(Company, user=request.user)
    applications = company.applications.select_related('student__user').order_by('-applied_on')
    return render(request, 'placements/company_dashboard.html', {
        'company': company,
        'applications': applications,
    })


@login_required
def company_update_application_view(request, application_id):
    company = get_object_or_404(Company, user=request.user)
    application = get_object_or_404(Application, id=application_id, company=company)

    if request.method == 'POST':
        form = ApplicationUpdateForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application updated — the student has been notified by email.")
            return redirect('company_dashboard')
    else:
        form = ApplicationUpdateForm(instance=application)

    return render(request, 'placements/company_update.html', {'form': form, 'application': application})
