from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages, auth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import LeadUser
from .models import Admin, Team_Leader, Staff, ProjectFile, Team_LeadData
from django.contrib.auth.models import User
from home.models import *
from django.contrib.auth import authenticate, login as auth_login
import pandas as pd
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .form import ProjectFileForm
User = get_user_model()
from .models import UserActivityLog
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404


@login_required(login_url='login')
def super_admin(request):
    if request.method == 'GET':
        user = request.user
        if user.email != 'admin@gmail.com':
            messages.error(request, "You do not have permission to access this page.")
            
            if request.user.is_superuser:
                user_type = "Super User"
            if request.user.is_admin:
                user_type = "Admin User"
            if request.user.is_team_leader:
                user_type = "Team leader User"
            if request.user.is_staff_new:
                user_type = "Staff User"

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            tagline = f"Log-out user[Email : {request.user.email}, {user_type}, IP : {ip}]"

            ActivityLog.objects.create(
                user = request.user,
                description = tagline,
                ip_address = ip
            )
            logout(request)
            return redirect('login') 
        user = user.username
        us = User.objects.get(email=user)
        users = Admin.objects.filter(user=us)
    return render(request, "admin_user.html", {'users': users})


@login_required(login_url='login')
def admin_add(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        mobile = request.POST['mobile']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']

        if username:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Email Already Exists")
                return redirect('admin_add')

        if username:
            if User.objects.filter(email=username).exists():
                messages.error(request, "Email Already Exists")
                return redirect('admin_add')

        user = User.objects.create(username=username, password=password,
                email=username, name=name, mobile=mobile, is_admin=True)
        user.set_password(password)
        user.save()

        admin = Admin.objects.create(
            user=request.user,
            email=username,
            name=name,
            mobile=mobile,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
        )
        messages.success(request, "Admin Created Successfully.")
        return redirect('super_admin')
    context = {
        'messages': messages.get_messages(request),
    }
    return render(request, 'admin_add.html', context)


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Email/Username or Password Incorrect")
            return redirect('login')
        if user is not None:
            auth.login(request, user)
            if request.user.is_superuser:
                user_type = "Super User"
            if request.user.is_admin:
                user_type = "Admin User"
            if request.user.is_team_leader:
                user_type = "Team leader User"
            if request.user.is_staff_new:
                user_type = "Staff User"

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')

            tagline = f"Log-In user[Email : {request.user.email}, {user_type}, IP : {ip}]"
            user = request.user
            if request.user.is_admin:
                admin_email = user.email
                admin_instance = Admin.objects.filter(email=admin_email).last()
                my_user = admin_instance.user
                ActivityLog.objects.create(
                    user = my_user,
                    description = tagline,
                    ip_address = ip
                )
            if request.user.is_team_leader:
                admin_email = user.email
                admin_instance = Team_Leader.objects.filter(email=admin_email).last()
                my_user1 = admin_instance.admin
                ActivityLog.objects.create(
                    admin = my_user1,
                    description = tagline,
                    ip_address = ip
                )

            if request.user.is_staff_new:
                admin_email = user.email
                admin_instance = Staff.objects.filter(email=admin_email).last()
                my_user2 = admin_instance.team_leader
                ActivityLog.objects.create(
                    team_leader = my_user2,
                    description = tagline,
                    ip_address = ip
                )

            # if not request.user.is_superuser:
                # ActivityLog.objects.create(
                #     user = my_user,
                #     admin = my_user1,
                #     team_leader = my_user2,
                #     description = tagline,
                #     ip_address = ip
                # )
            if user.is_superuser:
                messages.success(request, "Super User Login Successful")
                return redirect('super_admin')
            elif user.is_admin:
                user1 = user.username
                user = Admin.objects.get(email=user1)
                messages.success(request, "Admin Login Successful")
                return redirect('team_leader_user')
            elif user.is_team_leader:
                messages.success(request, "Team Leader Login Successful")
                return redirect('staff_user')
            elif user.is_staff_new:
                request.session['staff_email'] = user.email
                messages.success(request, "Staff Login Successful")
                return redirect('leads')
            else:
                messages.error(request, "User role not recognized")
                return redirect('login')
            
    return render(request, 'Login.html')


def team_dashboard(request):
    return render(request, "admin_dashboard/index.html")


@login_required(login_url='login')
def team_leader_user(request):
    if request.method == 'GET':
        user = request.user
        user1 = user.username
        us = Admin.objects.get(email=user1)
        users = Team_Leader.objects.filter(admin=us)

    return render(request, "admin_dashboard/team_leader_user.html", {'users': users})


# @login_required(login_url='login')
# def home(request):
#     return render(request, "admin_dashboard/team_leader/index.html")


@login_required(login_url='login')
def view_profile(request):
    if request.method == 'GET':
        if request.user:
            admin = LeadUser.objects.get(email=request.user.username)
            return render(request, 'admin_dashboard/team_leader/view-profile.html', {'admin': admin})
    if request.method == 'POST':
        admin = LeadUser.objects.get(email=request.user.username)
        new_email = request.POST['email']
        username = request.user.username
        user = Staff.objects.get(username=username)
        if new_email != admin.email and LeadUser.objects.filter(email=new_email).exclude(id=admin.id).exists():
            messages.error(request, "Email Already Exists")
            return redirect('view_profile')

        user.email = request.POST['email']
        user.username = request.POST['email']

        admin.name = request.POST.get('name', admin.name)
        admin.email = new_email
        admin.call = request.POST.get('call', admin.call)
        admin.save()
        user.save()
        messages.success(
            request, 'Your profile has been successfully updated.')
        return redirect('leads')

    return render(request, "admin_dashboard/team_leader/user-profile.html")

# def staff(request):
#     users = Staff.objects.all()
#     return render(request, "home/staff.html", {'users': users})

@login_required(login_url='login')
def logout_view(request):
    # if request.session['staff_email']:
    #     del request.session['staff_email']
    if request.user:
        request.user.is_login = False
        request.user.save()
    if request.user.is_superuser:
        user_type = "Super User"
    if request.user.is_admin:
        user_type = "Admin User"
    if request.user.is_team_leader:
        user_type = "Team leader User"
    if request.user.is_staff_new:
        user_type = "Staff User"

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    tagline = f"Log-out user[Email : {request.user.email}, {user_type}, IP : {ip}]"

    user = request.user
    if request.user.is_admin:
        admin_email = user.email
        admin_instance = Admin.objects.filter(email=admin_email).last()
        my_user = admin_instance.user
        ActivityLog.objects.create(
            user = my_user,
            description = tagline,
            ip_address = ip
        )
    if request.user.is_team_leader:
        admin_email = user.email
        admin_instance = Team_Leader.objects.filter(email=admin_email).last()
        my_user1 = admin_instance.admin
        ActivityLog.objects.create(
            admin = my_user1,
            description = tagline,
            ip_address = ip
        )

    if request.user.is_staff_new:
        admin_email = user.email
        admin_instance = Staff.objects.filter(email=admin_email).last()
        my_user2 = admin_instance.team_leader
        ActivityLog.objects.create(
            team_leader = my_user2,
            description = tagline,
            ip_address = ip
        )
    # if request.user.is_team_leader:
    #     admin_email = user.email
    #     admin_instance = Team_Leader.objects.filter(email=admin_email).last()
    #     my_user = admin_instance.user
    # ActivityLog.objects.create(
    #     user = my_user,
    #     description = tagline,
    #     ip_address = ip
    # )

    logout(request)
    messages.success(request, "Logout Successfully")
    return render(request, 'login.html')

@login_required(login_url='login')
def status_update(request):
    if request.method == 'POST':
        merchant_id = request.POST.get('leads_id')
        print(merchant_id, 'AAAAAAAAAAAAAAAA')

        if request.user.is_superuser:
            user_type = "Super User"
        elif request.user.is_admin:
            user_type = "Admin User"
        elif request.user.is_team_leader:
            user_type = "Team Leader User"
        elif request.user.is_staff_new:
            user_type = "Staff User"

        if merchant_id:
            new_status = request.POST.get('new_status')
            try:
                # Update status for LeadUser
                status_update_user = LeadUser.objects.get(id=merchant_id)
                tagline = f"Lead status changed from {status_update_user.status} to {new_status} by user[Email: {request.user.email}, {user_type}]"
                status_update_user.status = new_status
                status_update_user.save()

                # Log activity for LeadUser
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')

                if request.user.is_staff_new:
                    admin_email = request.user.email
                    admin_instance = Staff.objects.filter(email=admin_email).last()
                    my_user2 = admin_instance.team_leader
                    ActivityLog.objects.create(
                        team_leader=my_user2,
                        description=tagline,
                        ip_address=ip
                    )
            except LeadUser.DoesNotExist:
                # Handle the case where LeadUser does not exist
                pass

            try:
                # Update status for Team_LeadData
                status_update_team_lead = Team_LeadData.objects.get(id=merchant_id)
                tagline_team_lead = f"Lead status changed from {status_update_team_lead.status} to {new_status} by user[Email: {request.user.email}, {user_type}]"
                status_update_team_lead.status = new_status
                status_update_team_lead.save()

                # Log activity for Team_LeadData
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')

                if request.user.is_staff_new:
                    admin_email = request.user.email
                    admin_instance = Team_Leader.objects.filter(email=admin_email).last()
                    my_user2 = admin_instance.team_leader
                    ActivityLog.objects.create(
                        team_leader=my_user2,
                        description=tagline_team_lead,
                        ip_address=ip
                    )
            except Team_LeadData.DoesNotExist:
                # Handle the case where Team_LeadData does not exist
                pass

        return redirect('leads')
    return render(request, 'admin_dashboard/team_leader/leads.html')



# @login_required(login_url='login')
# def status_update(request):
#     if request.method == 'POST':
#         merchant_id = request.POST.get('leads_id')
#         print(merchant_id, 'AAAAAAAAAAAAAAAA')

#         if request.user.is_superuser:
#             user_type = "Super User"
#         if request.user.is_admin:
#             user_type = "Admin User"
#         if request.user.is_team_leader:
#             user_type = "Team leader User"
#         if request.user.is_staff_new:
#             user_type = "Staff User"

#         if merchant_id:
#             new_status = request.POST.get('new_status')
#             status_update_user = LeadUser.objects.get(id=merchant_id)
#             tagline = f"Lead status change from {status_update_user.status} to {new_status} by user[Email : {request.user.email}, {user_type}]"
#             status_update_user.status = new_status
#             status_update_user.save()

#             x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#             if x_forwarded_for:
#                 ip = x_forwarded_for.split(',')[0]
#             else:
#                 ip = request.META.get('REMOTE_ADDR')

#             user = request.user
#             if request.user.is_staff_new:
#                 admin_email = user.email
#                 admin_instance = Staff.objects.filter(email=admin_email).last()
#                 my_user2 = admin_instance.team_leader
#                 ActivityLog.objects.create(
#                     team_leader = my_user2,
#                     description = tagline,
#                     ip_address = ip
#                 )

#         return redirect('leads')
#     return render(request, 'admin_dashboard/team_leader/leads.html', {'status_update_user': status_update_user})





@login_required(login_url='login')
def staff_user(request):
    if request.method == 'GET':
        user = request.user
        user1 = user.username
        us = Team_Leader.objects.get(email=user1)
        users = Staff.objects.filter(team_leader=us)
        now = timezone.now()

        user_logs = []
        logged_in_count = 0
        logged_out_count = 0

        for staff in users:
            last_log = UserActivityLog.objects.filter(user=staff.user).order_by('-login_time').first()
            if last_log:
                if last_log.logout_time:
                    status = 'Inactive'
                    duration = str(last_log.logout_time - last_log.login_time).split('.')[0]
                    logged_out_count+=1
                else:
                    status = 'Active'
                    duration = str(now - last_log.login_time).split('.')[0]
                    logged_in_count+=1
            else:
                status = 'No data'
                duration = 'No data'
                logged_out_count+=1
            user_logs.append({
                'user': staff.user,
                'username':staff.name,
                'mobile': staff.mobile,
                'email': staff.user.email,
                'created_date': staff.user.date_joined,
                # 'updated_date':staff.user.updated_date,
                'status': status,
                'duration': duration,
                'id' : staff.id
            })

        total_staff=logged_in_count+logged_out_count

# -------------------- xxx ------------------------------------------

        user = request.user
        total_leads, total_interested_leads, total_not_interested_leads, other_location_leads, not_picked_leads, lost_leads = 0, 0, 0, 0, 0, 0
        total_leads_instance = []
        total_interested_leads_instance = []
        total_not_interested_leads_instance = []
        other_location_leads_instance = []
        not_picked_leads_instance = []
        lost_leads_instance = []
        
        try:
            team_lead = Team_Leader.objects.get(user=user)
        except Team_Leader.DoesNotExist:
            team_lead = None

        if team_lead:
            # Team leader's unassigned leads
            leads2 = Team_LeadData.objects.filter(assigned_to=None, team_leader=team_lead)
            total_uplode_leads = leads2.count()

            # Staff assigned to the team leader
            staff_members = Staff.objects.filter(team_leader=team_lead)
            
            # Collect data for each staff member
            for staff in staff_members:
                staff_leads = LeadUser.objects.filter(assigned_to=staff)
                total_leads += staff_leads.filter(status="Leads").count()
                total_interested_leads += staff_leads.filter(status="Intrested").count()
                total_not_interested_leads += staff_leads.filter(status="Not Interested").count()
                other_location_leads += staff_leads.filter(status="Other Location").count()
                not_picked_leads += staff_leads.filter(status="Not Picked").count()
                lost_leads += staff_leads.filter(status="Lost").count()

                total_leads_instance += staff_leads.filter(status="Leads")
                total_interested_leads_instance += staff_leads.filter(status="Intrested")
                total_not_interested_leads_instance += staff_leads.filter(status="Not Interested")
                other_location_leads_instance += staff_leads.filter(status="Other Location")
                not_picked_leads_instance += staff_leads.filter(status="Not Picked")
                lost_leads_instance += staff_leads.filter(status="Lost")

            # Add team leader's own data
            total_leads += leads2.filter(status="Leads").count()
            total_interested_leads += leads2.filter(status="Intrested").count()
            total_not_interested_leads += leads2.filter(status="Not Interested").count()
            other_location_leads += leads2.filter(status="Other Location").count()
            not_picked_leads += leads2.filter(status="Not Picked").count()
            lost_leads += leads2.filter(status="Lost").count()

            total_leads_instance += leads2.filter(status="Leads")
            total_interested_leads_instance += leads2.filter(status="Intrested")
            total_not_interested_leads_instance += leads2.filter(status="Not Interested")
            other_location_leads_instance += leads2.filter(status="Other Location")
            not_picked_leads_instance += leads2.filter(status="Not Picked")
            lost_leads_instance += leads2.filter(status="Lost")

        else:
            leads2 = Team_LeadData.objects.none()

        context = {
            'user_logs': user_logs,
            'total_staff':total_staff,
            'logged_in_count': logged_in_count,
            'logged_out_count': logged_out_count,
            'total_uplode_leads':total_uplode_leads,
            'leads2': leads2,
            'total_leads': total_leads,
            'total_interested_leads': total_interested_leads,
            'total_not_interested_leads': total_not_interested_leads,
            'other_location_leads': other_location_leads,
            'not_picked_leads': not_picked_leads,
            'lost_leads': lost_leads,

            'total_leads_instance': total_leads_instance,
            'total_interested_leads_instance': total_interested_leads_instance,
            'total_not_interested_leads_instance': total_not_interested_leads_instance,
            'other_location_leads_instance': other_location_leads_instance,
            'not_picked_leads_instance': not_picked_leads_instance,
            'lost_leads_instance': lost_leads_instance,
            }

        return render(request, "admin_dashboard/staff/staff_user.html", context)
    
def all_leads_data(request, tag):
    user = request.user
    total_leads, total_interested_leads, total_not_interested_leads, other_location_leads, not_picked_leads, lost_leads = 0, 0, 0, 0, 0, 0
    total_leads_instance = []
    total_interested_leads_instance = []
    total_not_interested_leads_instance = []
    other_location_leads_instance = []
    not_picked_leads_instance = []
    lost_leads_instance = []
    
    try:
        team_lead = Team_Leader.objects.get(user=user)
    except Team_Leader.DoesNotExist:
        team_lead = None

    if team_lead:
        # Team leader's unassigned leads
        leads2 = Team_LeadData.objects.filter(assigned_to=None, team_leader=team_lead)
        total_uplode_leads = leads2.count()

        # Staff assigned to the team leader
        staff_members = Staff.objects.filter(team_leader=team_lead)
        
        # Collect data for each staff member
        for staff in staff_members:
            staff_leads = LeadUser.objects.filter(assigned_to=staff)
            total_leads += staff_leads.filter(status="Leads").count()
            total_interested_leads += staff_leads.filter(status="Intrested").count()
            total_not_interested_leads += staff_leads.filter(status="Not Interested").count()
            other_location_leads += staff_leads.filter(status="Other Location").count()
            not_picked_leads += staff_leads.filter(status="Not Picked").count()
            lost_leads += staff_leads.filter(status="Lost").count()

            total_leads_instance += staff_leads.filter(status="Leads")
            total_interested_leads_instance += staff_leads.filter(status="Intrested")
            total_not_interested_leads_instance += staff_leads.filter(status="Not Interested")
            other_location_leads_instance += staff_leads.filter(status="Other Location")
            not_picked_leads_instance += staff_leads.filter(status="Not Picked")
            lost_leads_instance += staff_leads.filter(status="Lost")

        # Add team leader's own data
        total_leads += leads2.filter(status="Leads").count()
        total_interested_leads += leads2.filter(status="Intrested").count()
        total_not_interested_leads += leads2.filter(status="Not Interested").count()
        other_location_leads += leads2.filter(status="Other Location").count()
        not_picked_leads += leads2.filter(status="Not Picked").count()
        lost_leads += leads2.filter(status="Lost").count()

        total_leads_instance += leads2.filter(status="Leads")
        total_interested_leads_instance += leads2.filter(status="Intrested")
        total_not_interested_leads_instance += leads2.filter(status="Not Interested")
        other_location_leads_instance += leads2.filter(status="Other Location")
        not_picked_leads_instance += leads2.filter(status="Not Picked")
        lost_leads_instance += leads2.filter(status="Lost")

    else:
        leads2 = Team_LeadData.objects.none()
    
    if tag == 'total_leads_tag':
        context = {
            'leads' : total_leads_instance,
        }
    if tag == 'total_interested_tag':
        context = {
            'leads' : total_interested_leads_instance,
        }
    if tag == 'total_not_interested_tag':
        context = {
            'leads' : total_not_interested_leads_instance,
        }
    if tag == 'total_other_location_tag':
        context = {
            'leads' : other_location_leads_instance,
        }
    if tag == 'total_not_picked_tag':
        context = {
            'leads' : not_picked_leads_instance,
        }
    if tag == 'total_lost_tag':
        context = {
            'leads' : lost_leads_instance,
        }
    # context = {
    #     'total_uplode_leads':total_uplode_leads,
    #     'leads2': leads2,
    #     'total_leads': total_leads,
    #     'total_interested_leads': total_interested_leads,
    #     'total_not_interested_leads': total_not_interested_leads,
    #     'other_location_leads': other_location_leads,
    #     'not_picked_leads': not_picked_leads,
    #     'lost_leads': lost_leads,

    #     'total_leads_instance': total_leads_instance,
    #     'total_interested_leads_instance': total_interested_leads_instance,
    #     'total_not_interested_leads_instance': total_not_interested_leads_instance,
    #     'other_location_leads_instance': other_location_leads_instance,
    #     'not_picked_leads_instance': not_picked_leads_instance,
    #     'lost_leads_instance': lost_leads_instance,
    #     }
    return render(request, "admin_dashboard/staff/all_leads_data.html", context)





# @login_required(login_url='login')
# def lead(request):
#     print('LLLLLLLLLLLLLLLLLLLLL')

#     user = request.user

#     user1 = user.username
#     us = Team_Leader.objects.get(email=user1)
#     users = Staff.objects.filter(team_leader=us)
#     users = Team_Leader.objects.filter(status="Leads")
    

#     user_logs = []
#     for staff in users:
#         user_logs.append({
#                 'user': staff.user,
#                 'username':staff.name,
#                 'mobile': staff.mobile,
#                 'email': staff.user.email,
#             })


#     total_leads, total_lost_leads, total_customer, total_maybe = 0, 0, 0, 0

#     try:
#         team_lead = Team_Leader.objects.get(user=user)
#     except Team_Leader.DoesNotExist:
#         team_lead = None

#     if team_lead:
#         # Team leader's unassigned leads
#         leads2 = Team_LeadData.objects.filter(assigned_to=None, team_leader=team_lead)
#         total_uplode_leads = leads2.count()
#         leads3=LeadUser.objects.filter(status="Intrested")
#         customer_count=leads3.count()
#         leads4=LeadUser.objects.filter(status="Lost")
#         lost_count=leads4.count()
#         # Staff assigned to the team leader
#         staff_members = Staff.objects.filter(team_leader=team_lead)
        
#         # Collect data for each staff member
#         for staff in staff_members:
#             staff_leads = LeadUser.objects.filter(assigned_to=staff)
#             total_leads += staff_leads.filter(status="Leads").count()
#             total_lost_leads += staff_leads.filter(status="Lost_Leads").count()
#             total_customer += staff_leads.filter(status="Customer").count()
#             total_maybe += staff_leads.filter(status="Maybe").count()

#         # Add team leader's own data
#         total_leads += leads2.filter(status="Leads").count()
#         total_lost_leads += leads2.filter(status="Lost_Leads").count()
#         total_customer += leads2.filter(status="Customer").count()
#         total_maybe += leads2.filter(status="Maybe").count()
#     else:
#         leads2 = Team_LeadData.objects.none()
#         leads3= Team_LeadData.objects.none()

#     context = {
#         'total_uplode_leads':total_uplode_leads,
#         'leads2': leads2,
#         'total_leads': total_leads,
#         'total_lost_leads': total_lost_leads,
#         'total_customer': total_customer,
#         'total_maybe': total_maybe,
#         'user_logs': user_logs,
#         'leads3':leads3,
#         'customer_count':customer_count,
#         'leads4':leads4,
#         'lost_count':lost_count,
#     }

#     return render(request, "admin_dashboard/staff/lead.html", context)







@login_required(login_url='login')
def staff_dashboard(request):
    return render(request, "admin_dashboard/staff/index.html")


@login_required(login_url='login')
def view_profile(request):
    if request.method == 'GET':
        if request.user:
            admin = User.objects.get(email=request.user.email)
            return render(request, 'view-profile.html', {'admin': admin})
    if request.method == 'POST':
        admin = User.objects.get(email=request.user.email)
        new_email = request.POST['email']
        username = request.user.username
        user = User.objects.get(username=username)
        if new_email != admin.email and User.objects.filter(email=new_email).exclude(id=admin.id).exists():
            messages.error(request, "Email Already Exists")
            return redirect('view_profile')

        user.email = request.POST['email']
        user.username = request.POST['email']

        admin.name = request.POST.get('name', admin.name)
        admin.email = new_email
        admin.save()
        user.save()
        messages.success(
            request, 'Your profile has been successfully updated.')
        return redirect('super_admin')

    return render(request, "user-profile.html")

@login_required(login_url='login')
def admin_view_profile(request):
    if request.method == 'GET':
        if request.user:
            admin = Admin.objects.get(email=request.user.email)
            return render(request, 'admin_dashboard/view-profile.html', {'admin': admin})

    if request.method == 'POST':
        admin = get_object_or_404(Admin, email=request.user.email)
        new_email = request.POST.get('email')

        if new_email != admin.email and Admin.objects.filter(email=new_email).exclude(id=admin.id).exists():
            messages.error(request, "Email Already Exists")
            return redirect('admin_view_profile')

        admin.email = new_email
        admin.name = request.POST.get('name')
        admin.mobile = request.POST.get('mobile')
        admin.address = request.POST.get('address')
        admin.city = request.POST.get('city')
        admin.state = request.POST.get('state')
        admin.pincode = request.POST.get('pincode')

        admin.save()
        messages.success(
            request, 'Your profile has been successfully updated.')
        return redirect('team_leader_user')

    return render(request, "admin_dashboard/user-profile.html")


@login_required(login_url='login')
def team_view_profile(request):
    if request.method == 'GET':
        if request.user:
            admin = Team_Leader.objects.get(email=request.user.email)
            return render(request, 'admin_dashboard/staff/view-profile.html', {'admin': admin})

    if request.method == 'POST':
        admin = get_object_or_404(Team_Leader, email=request.user.email)
        new_email = request.POST.get('email')

        if new_email != admin.email and Team_Leader.objects.filter(email=new_email).exclude(id=admin.id).exists():
            messages.error(request, "Email Already Exists")
            return redirect('team_view_profile')

        admin.email = new_email
        admin.name = request.POST.get('name')
        admin.mobile = request.POST.get('mobile')
        admin.address = request.POST.get('address')
        admin.city = request.POST.get('city')
        admin.state = request.POST.get('state')
        admin.pincode = request.POST.get('pincode')

        admin.save()
        messages.success(
            request, 'Your profile has been successfully updated.')
        return redirect('staff_user')

    return render(request, "admin_dashboard/staff/user-profile.html")


@login_required(login_url='login')
def staff_view_profile(request):
    if request.method == 'GET':
        if request.user:
            admin = Staff.objects.get(email=request.user.email)
            return render(request, "admin_dashboard/team_leader/view-profile.html", {'admin': admin})

    if request.method == 'POST':
        admin = get_object_or_404(Staff, email=request.user.email)
        new_email = request.POST.get('email')

        if new_email != admin.email and Staff.objects.filter(email=new_email).exclude(id=admin.id).exists():
            messages.error(request, "Email Already Exists")
            return redirect('staff_view_profile')

        admin.email = new_email
        admin.name = request.POST.get('name')
        admin.mobile = request.POST.get('mobile')
        admin.address = request.POST.get('address')
        admin.city = request.POST.get('city')
        admin.state = request.POST.get('state')
        admin.pincode = request.POST.get('pincode')

        admin.save()
        messages.success(
            request, 'Your profile has been successfully updated.')
        return redirect('leads')

    return render(request, "admin_dashboard/team_leader/view-profile.html")


# @login_required(login_url='login')
# def update_user(request):
#     users = LeadUser.objects.all()

#     if request.method == 'POST':
#         merchant_id = request.POST.get('leads_id')
#         new_status = request.POST.get('new_status')

#         if merchant_id and new_status:
#             try:
#                 user_to_update = LeadUser.objects.get(id=merchant_id)
#                 user_to_update.status = new_status
#                 user_to_update.save()

#                 # Recalculate statistics after update
#                 total_leads = LeadUser.objects.filter(status='Leads').count()
#                 total_lost_leads = LeadUser.objects.filter(status='Lost_Leads').count()
#                 total_customer = LeadUser.objects.filter(status='Customer').count()
#                 total_maybe = LeadUser.objects.filter(status='Maybe').count()

#                 return render(request, "admin_dashboard/team_leader/leads.html", {
#                     'users': users,
#                     'total_leads': total_leads,
#                     'total_lost_leads': total_lost_leads,
#                     'total_customer': total_customer,
#                     'total_maybe': total_maybe,
#                 })

#             except LeadUser.DoesNotExist:
#                 pass

#     return redirect('lead')


@login_required(login_url='login')
def add_team_leader_user(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        mobile = request.POST['mobile']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Email Already Exists")
            return redirect('add_team_leader_user')

        if User.objects.filter(email=username).exists():
            messages.error(request, "Email Already Exists")
            return redirect('add_team_leader_user')

        user = User.objects.create_user(
            username=username, password=password, email=username, name=name, mobile=mobile, is_team_leader=True)
        user.set_password(password)
        user.save()
        admin_email = request.user.email
        admin1 = Admin.objects.get(email=admin_email)

        admin2 = Team_Leader.objects.create(
            admin=admin1,
            user=user,
            name=name,
            email=username,
            mobile=mobile,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
        )
        current_user = request.user
        super_admin = admin1.user

        if request.user.is_superuser:
                user_type = "Super User"
        if request.user.is_admin:
            user_type = "Admin User"
        if request.user.is_team_leader:
            user_type = "Team leader User"
        if request.user.is_staff_new:
            user_type = "Staff User"

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        tagline = f"Team Lead({name}) created by user[Email : {request.user.email}, {user_type}]"

        ActivityLog.objects.create(
            user = super_admin,
            description = tagline,
            ip_address = ip
        )

        messages.success(request, "Team Leader Created Successfully.")
        return redirect('team_leader_user')

    context = {
        'messages': messages.get_messages(request),
    }
    return render(request, "admin_dashboard/add_team_leader_user.html", context)


@login_required(login_url='login')
def add_staff(request):

    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        mobile = request.POST['mobile']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Email Already Exists")
            return redirect('add_staff')

        if User.objects.filter(email=username).exists():
            messages.error(request, "Email Already Exists")
            return redirect('add_staff')

        user = User.objects.create_user(
            username=username, password=password, email=username, name=name, mobile=mobile, is_staff_new=True)
        user.set_password(password)
        user.save()

        # team_leader_user = request.user
        admin_email = request.user.email
        team_leader = Team_Leader.objects.get(email=admin_email)

        staff = Staff.objects.create(
            team_leader=team_leader,
            user=user,
            name=name,
            email=username,
            mobile=mobile,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
        )

        if request.user.is_superuser:
            user_type = "Super User"
        if request.user.is_admin:
            user_type = "Admin User"
        if request.user.is_team_leader:
            user_type = "Team leader User"
        if request.user.is_staff_new:
            user_type = "Staff User"

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        tagline = f"staff : {staff.name} created by user[Email : {request.user.email}, {user_type}]"

        login_user = request.user
        admin_email = login_user.email
        admin_instance = Team_Leader.objects.filter(email=admin_email).last()
        my_user1 = admin_instance.admin
        ActivityLog.objects.create(
            admin = my_user1,
            description = tagline,
            ip_address = ip
        )

        messages.success(request, "Staff Created Successfully.")
        return redirect('staff_user')
    context = {
        'messages': messages.get_messages(request),
    }

    return render(request, "admin_dashboard/staff/add_staff.html", context)


def adminedit(request, id):
    admin = get_object_or_404(Admin, id=id)
    
    if request.method == 'GET':
        admin = Admin.objects.get(id=id)
        return render(request, 'edit.html', {'admin': admin})

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']
        city = request.POST['city']
        pincode = request.POST['pincode']
        state = request.POST['state']

        admin.name = name
        admin.email = email
        admin.mobile = mobile
        admin.address = address
        admin.city = city
        admin.pincode = pincode
        admin.state = state

        admin.save()
        messages.success(request, 'Your Admin Edit successfully updated.')

    return redirect('super_admin')


def teamedit(request, id):
    teamleader = get_object_or_404(Team_Leader, id=id)
    if request.method == 'GET':
        teamleader = Team_Leader.objects.get(id=id)
        return render(request, 'admin_dashboard/teamleadedit.html', {'teamleader': teamleader})


    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']
        city = request.POST['city']
        pincode = request.POST['pincode']
        state = request.POST['state']

        teamleader.name = name
        teamleader.email = email
        teamleader.mobile = mobile
        teamleader.address = address
        teamleader.city = city
        teamleader.pincode = pincode
        teamleader.state = state

        teamleader.save()
        messages.success(request, 'Your Team Leader Edit successfully updated.')
    return redirect('team_leader_user')


def staffedit(request, id):
    if request.method == 'GET':
        staff = get_object_or_404(Staff, id=id)
        return render(request, 'admin_dashboard/staff/editstaff.html', {'staff': staff})

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']
        city = request.POST['city']
        pincode = request.POST['pincode']
        state = request.POST['state']

        staff = get_object_or_404(Staff, id=id)
        staff.name = name
        staff.email = email
        staff.mobile = mobile
        staff.address = address
        staff.city = city
        staff.pincode = pincode
        staff.state = state

        staff.save()
        messages.success(request, 'Your Staff Edit successfully updated.')
    return redirect('staff_user')



@login_required(login_url='login')
def project(request):
    files = ProjectFile.objects.all()
    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

    else:
        form = ProjectFileForm()
    return render(request, 'admin_dashboard/team_leader/project.html', {'files': files, 'form': form})



def send_file_to_client(request, file_id):
    project_file = get_object_or_404(ProjectFile, id=file_id)
    LeadUser.objects.filter(send=True).update(
        send=False) 
    return redirect('leads')


@csrf_exempt
def update_send_status(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        user_id = data.get('id')
        new_send_status = data.get('send')

        try:
            user = LeadUser.objects.get(id=user_id)
            user.send = new_send_status
            user.save()
            return JsonResponse({'success': True, 'new_send_status': new_send_status})
        except LeadUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})



def bulk_from(request):
    if request.method == 'POST':
        assigned_id = request.POST.get('assigned_id')
        selected_lead_ids = request.POST.getlist('user_ids')
        request.session['selected_lead_ids'] = selected_lead_ids

        if not selected_lead_ids:
            messages.error(request, 'Assigned ID is missing.')
            return redirect('bulk_from')

        if not selected_lead_ids:
            messages.error(request, 'No leads selected.')
            return redirect('bulk_from')
        
        if selected_lead_ids:
            messages.error(request, 'Selected Leads Successfully')
            return redirect('bulk_from')

        try:
            assigned_user = get_object_or_404(Staff, id=assigned_id)
            for lead_id in selected_lead_ids:
                teams_leaders = Team_LeadData.objects.get(id=lead_id)
                lead_user = LeadUser.objects.create(
                    id=assigned_user,
                )
                lead_user.save()
            messages.success(request, 'Leads have been successfully assigned.')
        except Staff.DoesNotExist:
            messages.error(request, 'Assigned user does not exist.')
        except LeadUser.DoesNotExist:
            messages.error(request, 'One or more selected leads do not exist.')

    selected_lead_ids = request.session.get('selected_lead_ids', [])

    user = request.user
    user1 = user.username
    us = Team_Leader.objects.get(email=user1)
    staff_users2 = Staff.objects.filter(team_leader=us)
    lead_users = LeadUser.objects.all()

    context = {
        'staff_users2': staff_users2,
        'lead_users': lead_users,
        'selected_lead_ids': selected_lead_ids, 
    }
    return render(request, "admin_dashboard/staff/bulk_from.html", context)




def bulk_from_data(request):
    if request.method == 'POST':
        selected_lead_ids = request.session.get('selected_lead_ids', [])
        assigned_id = request.POST.get('assigned_id', [])
        selected_lead_ids = selected_lead_ids[0].split(',')
        # Ensure selected_lead_ids is a list of strings
        if isinstance(selected_lead_ids, str):
            selected_lead_ids = selected_lead_ids.split(',')
        teams_leader = Staff.objects.get(id=assigned_id)


        action = request.POST.get('action')

        # Process the action based on the value of `action`
        if action == 'assign_leads':

            selected_lead_ids = [lead_id.strip() for lead_id in selected_lead_ids if lead_id.strip()]
            
            
            teams_leader = get_object_or_404(Staff, id=assigned_id)
            email = request.user.email
            team_leader_instance = Team_Leader.objects.filter(email=email).last()
            
            for lead_id1 in selected_lead_ids:
                try:
                    if lead_id1.strip():
                        lead_id_int = int(lead_id1)
                    
                        teams_leaders = Team_LeadData.objects.get(id=lead_id_int)
                        teams_leaders.assigned_to = teams_leader  # Replace new_assigned_to with the new value
                        teams_leaders.save()
                        lead_user = LeadUser(
                            name=teams_leaders.name,
                            email=teams_leaders.email,
                            call=teams_leaders.call,
                            send=False,
                            status="Leads",
                            assigned_to=teams_leader,
                            team_leader=team_leader_instance,
                            )
                        lead_user.save()
                except ValueError:
                    print(f"Invalid ID value: ")
                except Team_LeadData.DoesNotExist:
                    print(f"Team_LeadData with id {lead_id_str} does not exist.")
            
            messages.success(request, 'Leads have been successfully assigned.')
        elif action == 'delete_leads':
            if isinstance(selected_lead_ids, str):
                selected_lead_ids = selected_lead_ids.split(',')
            
            selected_lead_ids = [lead_id.strip() for lead_id in selected_lead_ids if lead_id.strip()]
            
            for lead_id_str in selected_lead_ids:
                try:
                    lead_id_int = int(lead_id_str)
                    lead_to_delete = get_object_or_404(Team_LeadData, id=lead_id_int)
                    lead_to_delete.delete()
                except ValueError:
                    print(f"Invalid ID value: {lead_id_str}")
                except Team_LeadData.DoesNotExist:
                    print(f"Team_LeadData with id {lead_id_str} does not exist.")
            
            messages.success(request, 'Selected leads have been successfully deleted.')

        return redirect('lead')

    # If GET request, or after form submission, render the page
    selected_lead_ids = request.session.get('selected_lead_ids', [])
    staff_users = Staff.objects.all()
    lead_users = LeadUser.objects.all()

    context = {
        'staff_users': staff_users,
        'lead_users': lead_users,
        'selected_lead_ids': selected_lead_ids,
    }
    return render(request, "admin_dashboard/staff/bulk_from.html", context)




def excel_upload(request):
    if request.method == 'POST':
        excel_file = request.FILES['excel_file']
        df = pd.read_excel(excel_file)
        user_count =df.shape[0]
        duplicates = []
        team_leader = Team_Leader.objects.get(user=request.user)

        for i, row in df.iterrows():
            try:
                lead_user, created = Team_LeadData.objects.get_or_create(
                    call=row['call'],
                    defaults={
                        'name': row['name'],
                        'send': row['send'],
                        'status': row['status'],
                        'team_leader': team_leader
                    }
                )
                if not created:
                    lead_user.name = row['name']
                    lead_user.send = row['send']
                    lead_user.status = row['status']
                    lead_user.team_leader = team_leader
                    lead_user.save()
            except IntegrityError:
                duplicates.append(row['call'])
                continue

        message = "Excel file uploaded successfully!"
        users = Team_LeadData.objects.all()

        return redirect("lead")
        # return render(request, "admin_dashboard/staff/lead.html", {'message': message, 'users': users, 'duplicates': duplicates, 'user_count':user_count})

    users = Team_LeadData.objects.filter(assigned_to = None, team_leader=team_leader)
    return render(request, "admin_dashboard/staff/importlead.html", {'users': users})



@login_required(login_url='login')
def leads(request):
    staff_email = request.session.get('staff_email', '')
    try:
        staff = Staff.objects.get(email=staff_email)
    except Staff.DoesNotExist:
        staff = None
    if staff:
        users = LeadUser.objects.filter(status="Leads", assigned_to=staff)
        interested = LeadUser.objects.filter(status="Intrested", assigned_to=staff)
        not_interested = LeadUser.objects.filter(status="Not Interested", assigned_to=staff)
        other_location = LeadUser.objects.filter(status="Other Location", assigned_to=staff)
        not_picked = LeadUser.objects.filter(status="Not Picked", assigned_to=staff)
        lost = LeadUser.objects.filter(status="Lost", assigned_to=staff)
    else:
        users = LeadUser.objects.none()
    total_leads = users.count()
    
    total_interested_leads = interested.count()
    total_not_interested_leads = not_interested.count()
    total_other_location_leads = other_location.count()
    total_not_picked_leads = not_picked.count()
    total_lost_leads = lost.count()

    whatsapp_marketing = Marketing.objects.filter(source="whatsapp").last()

    return render(request, "admin_dashboard/team_leader/leads.html", {'users': users, 
                                                                      'total_interested_leads': total_interested_leads, 
                                                                      'total_leads': total_leads, 
                                                                      'total_lost_leads': total_lost_leads, 
                                                                      'total_not_interested_leads': total_not_interested_leads,
                                                                      'total_other_location_leads': total_other_location_leads, 
                                                                      'total_not_picked_leads': total_not_picked_leads, 
                                                                      'whatsapp_marketing': whatsapp_marketing})


def lost_leads(request):
    staff_email = request.session.get('staff_email', '')
    try:
        staff = Staff.objects.get(email=staff_email)
    except Staff.DoesNotExist:
        staff = None
    if staff:
        users_lead_lost = LeadUser.objects.filter(status="Intrested", assigned_to=staff)
    else:
        users_lead_lost = LeadUser.objects.none()
    return render(request, "admin_dashboard/team_leader/lost_leads.html", {'users_lead_lost': users_lead_lost, })


def import_leads(request):
    return render(request, "admin_dashboard/staff/importlead.html")



@login_required(login_url='login')
def assigned(request,email):
    staff = get_object_or_404(Staff, email=email)
    if request.method == 'GET':
        abc = Staff.objects.get(email=email)
    # staff_email = request.session.get('staff_email', '')
    try:
        staff = abc
    except Staff.DoesNotExist:
        staff = None
    
    if staff:
        assign = LeadUser.objects.filter(assigned_to=staff)

    else:
        assign = LeadUser.objects.none()
    
    assign_count=assign.count()
    
    return render(request, "admin_dashboard/staff/assigned.html", {'assign': assign,'assign_count':assign_count})

# def team_leader_staff_interested_leads(request, id):
#     my_staff = Staff.objects.filter(id=id).last()
#     email = request.user.email
#     team_leader_instance = Team_Leader.objects.filter(email=email).last()
#     interested_leads = LeadUser.objects.filter(assigned_to=my_staff, status='Intrested', team_leader=team_leader_instance)
#     print(interested_leads, 'HHHHHHHHHHHHHHHH')
#     context = {
#         'assign': interested_leads,
#     }
#     return render(request, "admin_dashboard/staff/assigned.html", context)
def team_leader_staff_interested_leads(request, id):
    my_staff = Staff.objects.filter(id=id).last()
    email = request.user.email
    team_leader_instance = Team_Leader.objects.filter(email=email).last()

    total_interested_leads_instance = LeadUser.objects.filter(
        assigned_to=my_staff, status="Intrested", team_leader=team_leader_instance).count()
    total_not_interested_leads_instance = LeadUser.objects.filter(assigned_to=my_staff,
                                                                status="Not Interested", team_leader=team_leader_instance).count()
    other_location_leads_instance = LeadUser.objects.filter(
        assigned_to=my_staff, status="Other Location", team_leader=team_leader_instance).count()
    not_picked_leads_instance = LeadUser.objects.filter(
        assigned_to=my_staff, status="Not Picked", team_leader=team_leader_instance).count()
    lost_leads_instance = LeadUser.objects.filter(
        assigned_to=my_staff, status="Lost", team_leader=team_leader_instance).count()
    interested_leads = LeadUser.objects.filter(
        assigned_to=my_staff, status='Intrested', team_leader=team_leader_instance)

#     interested_leads = LeadUser.objects.filter(assigned_to=my_staff, status='Intrested', team_leader=team_leader_instance)

    context = {
        'assign': interested_leads,
        'total_interested_leads_instance': total_interested_leads_instance,
        'total_not_interested_leads_instance': total_not_interested_leads_instance,
        'other_location_leads_instance': other_location_leads_instance,
        'not_picked_leads_instance': not_picked_leads_instance,
        'lost_leads_instance': lost_leads_instance,
    }
    return render(request, "admin_dashboard/staff/assigned.html", context)



@login_required(login_url='login')
def customer(request):
    staff_email = request.session.get('staff_email', '')
    try:
        staff = Staff.objects.get(email=staff_email)
    except Staff.DoesNotExist:
        staff = None
    if staff:
        customer_lead_lost = LeadUser.objects.filter(status="Not Interested", assigned_to=staff)
    else:
        customer_lead_lost = LeadUser.objects.none()
    return render(request, "admin_dashboard/team_leader/customer.html", {'customer_lead_lost': customer_lead_lost})


@login_required(login_url='login')
def maybe(request):
    staff_email = request.session.get('staff_email', '')
    try:
        staff = Staff.objects.get(email=staff_email)
    except Staff.DoesNotExist:
        staff = None
    if staff:
        lead_maybe = LeadUser.objects.filter(status="Other Location", assigned_to=staff)
    else:
        lead_maybe = LeadUser.objects.none()
    return render(request, "admin_dashboard/team_leader/follow.html", {'lead_maybe': lead_maybe})

@login_required(login_url='login')
def not_picked(request):
    staff_email = request.session.get('staff_email', '')
    try:
        staff = Staff.objects.get(email=staff_email)
    except Staff.DoesNotExist:
        staff = None
    if staff:
        lead_maybe = LeadUser.objects.filter(status="Not Picked", assigned_to=staff)
    else:
        lead_maybe = LeadUser.objects.none()
    return render(request, "admin_dashboard/team_leader/not_picked.html", {'lead_maybe': lead_maybe})

@login_required(login_url='login')
def lost(request):
    staff_email = request.session.get('staff_email', '')
    try:
        staff = Staff.objects.get(email=staff_email)
    except Staff.DoesNotExist:
        staff = None
    if staff:
        lead_maybe = LeadUser.objects.filter(status="Lost", assigned_to=staff)
    else:
        lead_maybe = LeadUser.objects.none()
    return render(request, "admin_dashboard/team_leader/lost.html", {'lead_maybe': lead_maybe})



@login_required(login_url='login')
def lead(request):
    user = request.user
    total_leads, total_interested_leads, total_not_interested_leads, other_location_leads, not_picked_leads, lost_leads = 0, 0, 0, 0, 0, 0

    try:
        team_lead = Team_Leader.objects.get(user=user)
    except Team_Leader.DoesNotExist:
        team_lead = None

    user = request.user

    user1 = user.username
    us = Team_Leader.objects.get(email=user1)
    users = Staff.objects.filter(team_leader=us)

    user_logs = []
    for staff in users:
        user_logs.append({
                'user': staff.user,
                'username':staff.name,
                'mobile': staff.mobile,
                'email': staff.user.email,
                'id' : staff.id,
        })

    if team_lead:
        # Team leader's unassigned leads
        leads2 = Team_LeadData.objects.filter(assigned_to=None, team_leader=team_lead)
        total_uplode_leads = leads2.count()

        # Staff assigned to the team leader
        staff_members = Staff.objects.filter(team_leader=team_lead)
        
        # Collect data for each staff member
        for staff in staff_members:
            staff_leads = LeadUser.objects.filter(assigned_to=staff)
            total_leads += staff_leads.filter(status="Leads").count()
            total_interested_leads += staff_leads.filter(status="Intrested").count()
            total_not_interested_leads += staff_leads.filter(status="Not Interested").count()
            other_location_leads += staff_leads.filter(status="Other Location").count()
            not_picked_leads += staff_leads.filter(status="Not Picked").count()
            lost_leads += staff_leads.filter(status="Lost").count()

        # Add team leader's own data
        total_leads += leads2.filter(status="Leads").count()
        total_interested_leads += leads2.filter(status="Intrested").count()
        total_not_interested_leads += leads2.filter(status="Not Interested").count()
        other_location_leads += leads2.filter(status="Other Location").count()
        not_picked_leads += leads2.filter(status="Not Picked").count()
        lost_leads += leads2.filter(status="Lost").count()
    else:
        leads2 = Team_LeadData.objects.none()

    context = {
        'total_uplode_leads':total_uplode_leads,
        'leads2': leads2,
        'total_leads': total_leads,
        'total_interested_leads': total_interested_leads,
        'total_not_interested_leads': total_not_interested_leads,
        'other_location_leads': other_location_leads,
        'not_picked_leads': not_picked_leads,
        'lost_leads': lost_leads,
        'user_logs': user_logs,
    }

    return render(request, "admin_dashboard/staff/lead.html", context)



def activitylogs(request):
    if request.method == "GET":
        if request.user.is_superuser:
            logs = ActivityLog.objects.all().order_by('-created_date')
            context = {
                'logs': logs,
            }
            return render(request, "activity_log.html", context)
        if request.user.is_admin:
            user_email = request.user.email
            admin_user = Admin.objects.filter(email=user_email).last()
            logs = ActivityLog.objects.filter(admin=admin_user).order_by('-created_date')
            context = {
                'logs': logs,
            }
            return render(request, "admin_dashboard/activity_log.html", context)
        
        if request.user.is_team_leader:
            user_email = request.user.email
            admin_user = Team_Leader.objects.filter(email=user_email).last()
            logs = ActivityLog.objects.filter(team_leader=admin_user).order_by('-created_date')
            context = {
                'logs': logs,
            }
            return render(request, "admin_dashboard/staff/activity_log.html", context)
        
        if request.user.is_staff_new:
            logs = ActivityLog.objects.filter(user=request.user).order_by('-created_date')
            context = {
                'logs': logs,
            }
            return render(request, "admin_dashboard/team_leader/activity_log.html", context)

    return render(request, "activity_log.html", context)


def edit_record(request, source):
    record = Marketing.objects.filter(source=source).last()
    if record:
        data = {
            'id': record.id,
            'source': record.source,
            'url': record.url,
            'message': record.message,
            'media_file': record.media_file.url if record.media_file else '',
        }
    else:
        data = {
            'source': source,
        }
    return JsonResponse(data)

def update_record(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # record_id = data.get('id')
        source = data.get('source')
        message = data.get('message')
        url = data.get('url')
        media_file = data.get('media_file')

        user = request.user
        marketing = Marketing.objects.create(
            user = user,
            source = source,
            message = message,
            url = url,
            media_file = media_file
        )
        
        return JsonResponse({'message': 'Record updated successfully', 'status':'200'})
    return HttpResponse(status=400)

def export_users(request):
    if request.method == 'POST':
        columns = ['name', 'call', 'send', 'status']
        df = pd.DataFrame(columns=columns)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        df.to_csv(path_or_buf=response, index=False)

        return response
    else:
        return HttpResponse("Invalid request method.")
    

def teamleader_perticular_leads(request, id):
    staff_leads = LeadUser.objects.filter(assigned_to=id).order_by('-created_date') 
    context = {
        'staff_leads': staff_leads
    }
    return render(request, 'admin_dashboard/staff/perticular_leads.html', context)


@login_required(login_url='login')
def customer_details(request,email):
    
    staff = get_object_or_404(Staff, email=email)
    if request.method == 'GET':
        abc = Staff.objects.get(email=email)
    # staff_email = request.session.get('staff_email', '')
    if staff:
        users_lead_lost = LeadUser.objects.filter(status="Intrested", assigned_to=staff)
    else:
        users_lead_lost = LeadUser.objects.none()
  

    assign_count=users_lead_lost.count()
    print(f"Assigned leads for staff with email {staff}: {users_lead_lost}")

    return render(request, "admin_dashboard/staff/customer_details.html", {'users_lead_lost': users_lead_lost,'assign_count':assign_count})

# def lost(request):
#     # staff_email = request.session.get('staff_email', '')
#     # try:
#     #     staff = Staff.objects.get(email=staff_email)
#     # except Staff.DoesNotExist:
#     #     staff = None
#     # if staff:
#     lead_maybe = LeadUser.objects.filter(status="Lost", assigned_to=staff)
#     # else:
#     #     lead_maybe = LeadUser.objects.none()
#     return render(request, "admin_dashboard/team_leader/lost.html", {'lead_maybe': lead_maybe})

@login_required(login_url='login')
def teamcustomer(request):
    users = Team_LeadData.objects.filter(status="Intrested")
    return render(request, "admin_dashboard/staff/customer.html",{'users': users,})

@login_required(login_url='login')
def teamlost_leads(request):
    users = Team_LeadData.objects.filter(status="Not Interested")
    return render(request, "admin_dashboard/staff/lost_leads.html",{'users': users,})

@login_required(login_url='login')
def teammaybe(request):
    users = Team_LeadData.objects.filter(status="Other Location")
    return render(request, "admin_dashboard/staff/follow.html", {'users': users,})

@login_required(login_url='login')
def teamnot_picked(request):
    users = Team_LeadData.objects.filter(status="Not Picked")
    return render(request, "admin_dashboard/staff/not_picked.html", {'users': users,})

@login_required(login_url='login')
def teamlost(request):
    users = Team_LeadData.objects.filter(status="Lost")
    return render(request, "admin_dashboard/staff/lost.html", {'users': users,})

def get_lead_user_data(request, id):
    lead_user = get_object_or_404(LeadUser, id=id)
    data = {
        'id': lead_user.id,
        'status': lead_user.status,
        'message': lead_user.message  
    }
    return JsonResponse(data)

@csrf_exempt
def update_lead_user(request, id):
    lead_user = get_object_or_404(LeadUser, id=id)
    if request.method == 'POST':
        lead_user.status = request.POST.get('status')
        lead_user.message = request.POST.get('message')  
        lead_user.save()
        return JsonResponse({'message': 'Success'})
    return JsonResponse({'message': 'Failed'}, status=400)


