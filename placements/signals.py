"""
Email notification logic.

Uses a pre_save signal to detect what changed (status or interview
schedule) by comparing against the database, then sends the right
email after the save completes in post_save.
"""
from django.core.mail import send_mail
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Application

STATUS_MESSAGES = {
    'SHORTLISTED': "Good news — you've been shortlisted for {company}. Check your dashboard for next steps.",
    'INTERVIEW': "Your interview for {company} has been scheduled. Check your dashboard for details.",
    'SELECTED': "Congratulations! You've been selected for {company}.",
    'REJECTED': "Your application to {company} was not successful this time. Keep applying — more drives are coming up.",
}


@receiver(pre_save, sender=Application)
def stash_previous_state(sender, instance, **kwargs):
    """Before saving, remember the old status/interview time so post_save can compare."""
    if instance.pk:
        try:
            old = Application.objects.get(pk=instance.pk)
            instance._old_status = old.status
            instance._old_interview_datetime = old.interview_datetime
        except Application.DoesNotExist:
            instance._old_status = None
            instance._old_interview_datetime = None
    else:
        instance._old_status = None
        instance._old_interview_datetime = None


@receiver(post_save, sender=Application)
def notify_on_change(sender, instance, created, **kwargs):
    student_email = instance.student.user.email
    if not student_email:
        return  # nothing to send to

    company_name = instance.company.name

    if created:
        send_mail(
            subject=f"Application received — {company_name}",
            message=(
                f"Hi {instance.student.user.first_name or instance.student.user.username},\n\n"
                f"Your application to {company_name} ({instance.company.job_role}) "
                f"has been received. We'll notify you as your status updates.\n\n"
                f"— Placement Cell"
            ),
            from_email=None,
            recipient_list=[student_email],
            fail_silently=True,
        )
        return

    old_status = getattr(instance, '_old_status', None)
    old_interview = getattr(instance, '_old_interview_datetime', None)

    # Status changed → send the matching notification
    if old_status is not None and old_status != instance.status and instance.status in STATUS_MESSAGES:
        send_mail(
            subject=f"Placement Update — {company_name} [{instance.get_status_display()}]",
            message=(
                f"Hi {instance.student.user.first_name or instance.student.user.username},\n\n"
                + STATUS_MESSAGES[instance.status].format(company=company_name) +
                f"\n\n— Placement Cell"
            ),
            from_email=None,
            recipient_list=[student_email],
            fail_silently=True,
        )

    # Interview newly scheduled or rescheduled → separate email with details
    if instance.interview_datetime and instance.interview_datetime != old_interview:
        send_mail(
            subject=f"Interview Scheduled — {company_name}",
            message=(
                f"Hi {instance.student.user.first_name or instance.student.user.username},\n\n"
                f"Your interview for {company_name} ({instance.company.job_role}) is scheduled:\n\n"
                f"Date & Time: {instance.interview_datetime.strftime('%d %b %Y, %I:%M %p')}\n"
                f"Mode: {instance.get_interview_mode_display() if instance.interview_mode else 'TBD'}\n"
                f"Venue/Link: {instance.interview_location or 'TBD'}\n\n"
                f"Please be prepared and check your dashboard for any updates.\n\n"
                f"— Placement Cell"
            ),
            from_email=None,
            recipient_list=[student_email],
            fail_silently=True,
        )
