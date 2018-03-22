from django.contrib import admin
from procedure.models import Patient, Endoscopy


# class ExamAdmin(admin.ModelAdmin):
#     list_display=('exam_date','patient_name', 'hospital_no')
#     list_filter=['exam_date']
#     search_fields=('patient_name','hospital_no')
#
# admin.site.register(Exam, ExamAdmin)

class PatientAdmin(admin.ModelAdmin):
    list_display=('name', 'hospital_no')
    list_filter=['name']
    search_fields=('name','hospital_no')

admin.site.register(Patient, PatientAdmin)

class EndoscopyAdmin(admin.ModelAdmin):
    list_display=('date', 'type', 'id')
    list_filter=['date', 'id']
    search_fields=('date','type', 'id')

admin.site.register(Endoscopy, EndoscopyAdmin)
