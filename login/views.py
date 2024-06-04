from allauth.account.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
from django.db.models import Case, When


from .models import Report, ReportFile
from .forms import ReportForm, ResolvedFeedbackForm

class IndexView(TemplateView):
    template_name = "index.html"

class LogoutRedirectView(RedirectView):
    url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)

class CustomLoginView(LoginView):
    def get_success_url(self):
        return self.request.build_absolute_uri('/dashboard/')


def signout(request):
    logout(request)
    return redirect('/')

def is_site_admin(user):
    return user.is_authenticated and user.groups.filter(name='site_admin').exists()

@login_required
def custom_redirect(request):
    if request.user.is_superuser:
        return redirect('/admin/')
    if is_site_admin(request.user):
        return redirect('login:admin_dashboard')
    else:
        return redirect('login:user_dashboard')

@login_required
@user_passes_test(is_site_admin)
def admin_dashboard(request):
    all_reports = Report.objects.all().order_by(   #First sort by New, In Progress, Resolved
        Case(
            When(status='New', then=0),
            When(status='In Progress', then=1),
            When(status='Resolved', then=2),
            default=3
        ),
        '-published_date'       #Within the sorting of the 3 categories, sort by reverse chronological time
    )
    return render(request, 'admin_dashboard.html', {'user': request.user, 'all_reports': all_reports})

@login_required
def user_dashboard(request):
    # Logic for the user dashboard
    user_reports = Report.objects.filter(reporter=request.user).order_by( #logged-in user only gets access to their own past reports
        Case(   #Now ordering by status with resolved being first
            When(status='New', then=2),
            When(status='In Progress', then=1),
            When(status='Resolved', then=0),
            default=3
        ),
        '-published_date'  # Within the sorting of the 3 categories, sort by reverse chronological time
    )

    return render(request, 'user_dashboard.html', {'user': request.user, 'user_reports': user_reports})

@login_required
def user_profile(request):
    context = {
        'name': request.user.get_full_name(),
        'email': request.user.email,
    }
    return render(request, 'profile.html', context)

def report(request):  #method for user to submit a new whistleblowing report
    if request.method == 'POST':
        form = ReportForm(request.POST,  request.FILES)
        if form.is_valid():
            new_report = form.save(commit=False)
            if request.user.is_authenticated:
                new_report.reporter = request.user  #for logged-in user
            else:
                new_report.reporter = None    #anonymous users
            new_report.save()
            for file in request.FILES.getlist('file'):  # Make sure 'file' is the name attribute in your HTML form
                ReportFile.objects.create(report=new_report, file=file)

            return render(request, 'report_done.html') #redirect to new page after report is successfully submitted
    else:
        form = ReportForm()
    return render(request, 'report.html', {'form': form})

class ReportDone(generic.DetailView):
    template_name = "report_done.html"

class ReportResolved(generic.DetailView):
    template_name = "report_resolved.html"

@login_required
def report_detail(request, report_id):  #for displaying details of past reports for logged-in users and site admins
    report = get_object_or_404(Report, id=report_id)
    user_is_site_admin = is_site_admin(request.user)
    report_files = report.files.all()

    if user_is_site_admin:
        if report.status == 'New':    #when site admin opens report detail, then status changes from new to in progress
            report.status = 'In Progress'
            report.save()
        feedbackForm = handle_feedback(request, report)   #calls method for site admin to submit written text feedback about resolution
    else:
        feedbackForm = None     #if user is not site admin, they will not have the option to submit written feedback regarding the resolution
    return render(request, 'report_detail.html', {'report': report,  'report_files': report_files, 'form': feedbackForm, 'is_site_admin': user_is_site_admin})

@user_passes_test(is_site_admin)
def resolve_report(request, report_id):     #method used when site admin hits button to resolve the report
    report = get_object_or_404(Report, id=report_id)
    user_is_site_admin = is_site_admin(request.user)
    feedbackForm = handle_feedback(request, report)     #calls method for handling text feedback about resolution of report
    return render(request, 'report_detail.html', {'report': report, 'form': feedbackForm, 'is_site_admin': user_is_site_admin})

@user_passes_test(is_site_admin)
def handle_feedback(request, report):   #for handling written text feedback from site admin about resolving the report
    if request.method == 'POST':    #if site admin has hit the button to resolve a report/give feedback
        feedback_form = ResolvedFeedbackForm(request.POST)
        if feedback_form.is_valid():
            report.resolved_notes = feedback_form.cleaned_data['resolved_notes']    #gets text from feedback form and puts it in the report model
            report.status = 'Resolved'      #changes report status
            report.save()
    else:
        if report.resolved_notes: #if a site admin has already given feedback, then it will show up in the form for them to see (and they can still edit and re-submit the form)
            existing_data = {'resolved_notes': report.resolved_notes}
            feedback_form = ResolvedFeedbackForm(initial=existing_data) #form is initialized with the past submitted feedback
        else:
            feedback_form = ResolvedFeedbackForm()  #otherwise the form will show up as empty
    return feedback_form

@login_required
def delete_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if request.method == 'POST':
        report.delete()
        return redirect('login:user_dashboard') 
