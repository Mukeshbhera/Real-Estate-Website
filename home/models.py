from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from uuid import uuid4
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from home.models import *
from pytz import timezone
from django.utils.timezone import now
from django.utils import timezone

class User(AbstractUser):
    name            = models.CharField(max_length=200, null=True, blank=True)
    mobile          = models.CharField(max_length=200, null=True, blank=True)
    email           = models.CharField(max_length=200, unique=True)
    is_admin        = models.BooleanField(default=False)
    is_team_leader  = models.BooleanField(default=False)
    is_staff_new    = models.BooleanField(default=False)
    login_time      = models.DateTimeField(default=timezone.now)
    logout_time     = models.DateTimeField(null=True, blank=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    updated_date    = models.DateTimeField(auto_now=True)

    @property
    def is_active(self):
        return self.logout_time is None

    @property
    def duration(self):
        if self.logout_time:
            duration = self.logout_time - self.login_time
        else:
            duration = timezone.now() - self.login_time

        return int(duration.total_seconds())

    def _str_(self):
        return f"{self.username} - {self.login_time} to {self.logout_time if self.logout_time else 'Active'}"


class UserActivityLog(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    login_time      = models.DateTimeField(default=timezone.now)
    logout_time     = models.DateTimeField(null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True, null=True)

    def _str_(self):
        return f"{self.user.username} - {self.login_time} to {self.logout_time if self.logout_time else 'Active'}"
    

class Admin(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    admin_id        = models.CharField(max_length=200, unique=True, default=uuid4,)
    name            = models.CharField(max_length=200, null=True, blank=True)
    email           = models.CharField(max_length=200, unique=True)
    mobile          = models.CharField(max_length=200, null=True, blank=True)
    address         = models.CharField(max_length=200, null=True, blank=True)
    city            = models.CharField(max_length=25, null=True, blank=True)
    pincode         = models.CharField(max_length=6, null=True, blank=True)
    state           = models.CharField(max_length=30, null=True, blank=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    updated_date    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

class Team_Leader(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    admin           = models.ForeignKey(Admin, on_delete=models.CASCADE)
    team_leader_id  = models.CharField(max_length=200, unique=True, default=uuid4)
    name            = models.CharField(max_length=200, null=True, blank=True)
    email           = models.CharField(max_length=200, unique=True)
    mobile          = models.CharField(max_length=200, null=True, blank=True)
    address         = models.CharField(max_length=200, null=True, blank=True)
    city            = models.CharField(max_length=25, null=True, blank=True)
    pincode         = models.CharField(max_length=6, null=True, blank=True)
    state           = models.CharField(max_length=30, null=True, blank=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    updated_date    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class Staff(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    team_leader     = models.ForeignKey(Team_Leader, on_delete=models.CASCADE)
    staff_id        = models.CharField(max_length=200, unique=True, default=uuid4)
    name            = models.CharField(max_length=200, null=True, blank=True)
    email           = models.CharField(max_length=200, unique=True)
    mobile          = models.CharField(max_length=200, null=True, blank=True)
    address         = models.CharField(max_length=200, null=True, blank=True)
    city            = models.CharField(max_length=25, null=True, blank=True)
    pincode         = models.CharField(max_length=6, null=True, blank=True)
    state           = models.CharField(max_length=30, null=True, blank=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    updated_date    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
    
class Team_LeadData(models.Model):
    STATUS_LEAD = (
        ('Leads', 'Leads'),
        ('Intrested', 'Intrested'),
        ('Not Interested', 'Not Interested'),
        ('Other Location', 'Other Location'),
        ('Not Picked', 'Not Picked'),
        ('Lost', 'Lost'),
    )
    team_leader = models.ForeignKey(Team_Leader, on_delete=models.CASCADE, null=True, blank=True)
    assigned_to = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    name        = models.CharField(max_length=255)
    email       = models.CharField(max_length=200, null=True, blank=True)
    call        = models.CharField(max_length=255, blank=True, null=True)
    send        = models.CharField(max_length=255, blank=True, null=True)
    status      = models.CharField(max_length=255,default='Leads', choices=STATUS_LEAD)
    message     = models.TextField(null=True, blank=True)
    created_date    = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_date    = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    

class LeadUser(models.Model):
    STATUS_LEAD = (
        ('Leads', 'Leads'),
        ('Intrested', 'Intrested'),
        ('Not Interested', 'Not Interested'),
        ('Other Location', 'Other Location'),
        ('Not Picked', 'Not Picked'),
        ('Lost', 'Lost'),
    )
    team_leader = models.ForeignKey(Team_Leader, on_delete=models.CASCADE, null=True, blank=True)
    assigned_to = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    name        = models.CharField(max_length=255)
    email       = models.CharField(max_length=200, null=True, blank=True)
    call        = models.CharField(max_length=255, blank=True, null=True)
    send        = models.CharField(max_length=255, blank=True, null=True)
    status      = models.CharField(max_length=255,default='Leads', choices=STATUS_LEAD)
    message     = models.TextField(null=True, blank=True)
    created_date    = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_date    = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name
    

class ProjectFile(models.Model):
    file        = models.FileField(upload_to='project/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.file.name
    
class Marketing(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    admin       = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True, blank=True)
    team_leader = models.ForeignKey(Team_Leader, on_delete=models.CASCADE, null=True, blank=True)
    staff       = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    source      = models.CharField(max_length=50, null=True, blank=True)
    message     = models.TextField(null=True, blank=True)
    media_file  = models.FileField(upload_to ='marketing_media/', null=True, blank=True)
    url         = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.source
    
class ActivityLog(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    admin           = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True, blank=True)
    team_leader     = models.ForeignKey(Team_Leader, on_delete=models.CASCADE, null=True, blank=True)
    staff           = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    description     = models.CharField(max_length=200, null=True, blank=True)
    ip_address      = models.CharField(max_length=15, null=True, blank=True)
    created_date    = models.DateTimeField(default=timezone.now)
    updated_date    = models.DateTimeField(auto_now=True)

    def __st__(self):
        return self.user



class Local(models.Model):
    user = models.CharField(max_length=200)
    localls = models.CharField(max_length=300, null=True, blank=True)
    locallss = models.URLField(null=True, blank=True)