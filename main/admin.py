from django.contrib import admin

# Register your models here.
# myapp/main/admin.py
from django.contrib import admin
from .models import Doctor, Admission, LabResult

# This makes the Doctor model manageable from the admin page
admin.site.register(Doctor)
admin.site.register(Admission)
admin.site.register(LabResult)