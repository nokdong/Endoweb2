from datetime import date, datetime
import collections
import sys
import json
from collections import OrderedDict

from django import forms
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.shortcuts import render, render_to_response, redirect
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect, HttpResponse

from endo.views import LoginRequiredMixin
from procedure.forms import ProcedureSearchForm, AddingPatientInitalForm, PatientModelForm, EndoscopyModelForm
from procedure.models import  Patient, Endoscopy
from bokeh.plotting import figure, save, output_file, ColumnDataSource
from bokeh.layouts import column
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import Legend, HoverTool



class HomeView(TemplateView):
    template_name = "home2.html"


# class ExamModelForm(LoginRequiredMixin, forms.ModelForm):
#     class Meta:
#         model = Exam
#         fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
#                   'patient_sex', 'patient_birth',
#                   'patient_phone', 'exam_Dx', 'exam_procedure', 'Bx_result', 'follow_up']
#         widgets = {'exam_type': forms.CheckboxSelectMultiple}
#         widgets = {'exam_procedure': forms.CheckboxSelectMultiple}
#
#
# class ExamCreateView(LoginRequiredMixin, CreateView):
#     form_class = ExamModelForm
#     model = Exam
#     success_url = reverse_lazy("procedure:add")
#
#     def form_valid(self, form):
#         return super(ExamCreateView, self).form_valid(form)
#
# '''
# def post_update_search(request):
#     template_name = 'procedure/post_search.html'
#     return render(request, template_name, request_token)
# '''

# 환자 입력 클래스. 존재하는 환자와 처음 입력하는 환자를 구분해서 진행된다.
class AddingPatient(LoginRequiredMixin, FormView):
    form_class = AddingPatientInitalForm
    template_name = 'procedure/add_patient_initial.html'

    def form_valid(self, form):
        hospital_no = '%s' % self.request.POST['search_id']
        context = {}
        try:
            patient = Patient.objects.get(hospital_no=hospital_no)
            endoscopy_list = Endoscopy.objects.filter(Q(patient_id=patient.id))
            endoscopyform = EndoscopyModelForm
            context['patient'] = patient
            context['age'] = age(patient.birth)
            context['endoscopy_list'] = endoscopy_list
            context['endoscopyform'] = endoscopyform
            context['fk'] = patient.id
            return render(self.request, 'procedure/existing_patient_adding_endoscopy.html', context)
        except Patient.DoesNotExist:
            patient = Patient()
            patient.hospital_no = hospital_no
            patient_form = PatientModelForm(instance=patient)
            endoscopy_form = EndoscopyModelForm
            context['patient_form'] = patient_form
            context['endoscopy_form'] = endoscopy_form
        return render(self.request, 'procedure/nonexisting_patient_adding_endoscopy.html', context)


def add_endoscopy(request):
    if 'fk' in request.POST:
        endoscopy = Endoscopy(patient_id=request.POST['fk'])
        endoscopy_form = EndoscopyModelForm(request.POST, instance=endoscopy)
        if endoscopy_form.is_valid():
            endoscopy_form.save()
    else:
        print (request.POST)
        patient_form = PatientModelForm(request.POST)
        if patient_form.is_valid():
            created_patient = patient_form.save()
            endoscopy=Endoscopy(patient_id = created_patient.id)
            endoscopy_form = EndoscopyModelForm(request.POST, instance=endoscopy)
            if endoscopy_form.is_valid():
                created_patient.save()
                endoscopy_form.save()

    return HttpResponseRedirect('/procedure/add_patient_initial')



# 검색 클래스뷰
class SearchView(LoginRequiredMixin, FormView):
    form_class = ProcedureSearchForm
    template_name = 'procedure/post_search.html'

    def form_valid(self, form):
        #global request_token
        first_date = '%s' % self.request.POST['first_date']
        last_date = '%s' % self.request.POST['last_date']
        name = '%s' % self.request.POST['name']
        hospital_no = '%s' % self.request.POST['hospital_no']
        exam_type = self.request.POST['type']
        Dx = '%s' % self.request.POST['Dx']
        procedure = self.request.POST.getlist('procedure')
        Bx_result = '%s' % self.request.POST['Bx_result']

        context = {}
        patient_list={}
        searched_list = []
        searched_list_forloop = []

        if name =='' and hospital_no =='':

            if first_date != '' and last_date != '':
                endoscopy_list = Endoscopy.objects.filter(date__gte=first_date, date__lte=last_date)
                searched_list.append('날짜')
                searched_list_forloop.append('date')
            elif first_date != '' and last_date == '':
                endoscopy_list = Endoscopy.objects.filter(date__gte=first_date)
                searched_list.append('날짜')
                searched_list_forloop.append('date')
            elif first_date == '' and last_date != '':
                endoscopy_list = Endoscopy.objects.filter(date__lte=last_date)
                searched_list.append('날짜')
                searched_list_forloop.append('date')
            else :
                endoscopy_list = Endoscopy.objects.all()
            if exam_type != 'all':
                endoscopy_list = endoscopy_list.filter(type__exact = list(exam_type))
                searched_list.append('검사종류')
                searched_list_forloop.append('type')
            if Dx != '':
                endoscopy_list = endoscopy_list.filter(Dx__contains=Dx)
                searched_list.append('내시경진단')
                searched_list_forloop.append('Dx')
            if procedure !=[]:
                for each_exam in endoscopy_list:
                    common = set(each_exam.procedure).intersection(set(procedure))
                    if len(common) == 0:
                        endoscopy_list = endoscopy_list.exclude(id = each_exam.id)
                searched_list.append('시술')
                searched_list_forloop.append('procedure')
            if Bx_result != '':
                endoscopy_list = endoscopy_list.filter(Bx_result__contains=Bx_result)
                searched_list.append('조직소견')
                searched_list_forloop.append('Bx_result')
            num = len(endoscopy_list)
            for endo in endoscopy_list:
                patient = Patient.objects.get(id = endo.patient_id)
                patient_list[patient.name] = collections.OrderedDict()
                patient_list[patient.name]['hospital_no']=patient.hospital_no
                patient_list[patient.name]['id'] = patient.id
                for search in searched_list_forloop:
                    value = getattr(endo, search)
                    patient_list[patient.name][search]=value
                    #if isinstance(value, date):
                    #    context[patient.name][search] = value
                    #else : context[patient.name][search] = value.strip()
            searched_list = ['이름', '등록번호'] + searched_list
            context['searched_list'] = searched_list
            context['patient_list'] = patient_list
            context['patient_number'] = len(context['patient_list'])
            context['form']=form
        else :
            if name !='':
                finded_patient_list = Patient.objects.filter(Q(name__icontains = name))
                for patient in finded_patient_list:
                    patient_list[patient.name]=collections.OrderedDict()
                    patient_list[patient.name]['hospital_no'] = patient.hospital_no
                    patient_list[patient.name]['sex'] = patient.sex
                    patient_list[patient.name]['birth'] = patient.birth
                    patient_list[patient.name]['id'] = patient.id
            if hospital_no !='':
                finded_patient_list = Patient.objects.filter(Q(hospital_no__icontains = hospital_no))
                for patient in finded_patient_list:
                    patient_list[patient.name]=collections.OrderedDict()
                    patient_list[patient.name]['hospital_no'] = patient.hospital_no
                    patient_list[patient.name]['sex'] = patient.sex
                    patient_list[patient.name]['birth'] = patient.birth
                    patient_list[patient.name]['id'] = patient.id
            searched_list = ['이름', '등록번호', '성별', '생일']
            context['searched_list'] = searched_list
            context['patient_list'] = patient_list
            context['patient_number'] = len(context['patient_list'])
            context['form'] = form

        return render(self.request, self.template_name, context)


# class BxUpdateview(LoginRequiredMixin, UpdateView):
#     model = Exam
#     template_name = 'procedure/Bx_update.html'
#     fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
#               'patient_sex', 'patient_birth', 'patient_phone', 'exam_Dx', 'exam_procedure', 'Bx_result',
#               'Bx_result_call', 'follow_up']
#     success_url = reverse_lazy('procedure:biopsy')
#
#
# class BxCallUpdateview(LoginRequiredMixin, UpdateView):
#     model = Exam
#     template_name = 'procedure/Bx_update.html'
#     fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
#               'patient_sex', 'patient_birth', 'patient_phone', 'exam_Dx', 'exam_procedure', 'Bx_result',
#               'Bx_result_call', 'follow_up']
#     success_url = reverse_lazy('procedure:Bx_call')


# class SearchUpdateview(LoginRequiredMixin, UpdateView):
#     model = Exam
#     fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
#               'patient_sex', 'patient_birth', 'patient_phone', 'exam_Dx', 'exam_procedure', 'Bx_result',
#               'Bx_result_call', 'follow_up',
#               'phone_check', 're_visit']
#     template_name = 'procedure/post_search_update.html'
#     success_url = reverse_lazy('procedure:post_update_search')
#
#
# class TodayUpdateview(LoginRequiredMixin, UpdateView):
#     model = Exam
#     fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
#               'patient_sex', 'patient_birth', 'patient_phone', 'exam_Dx', 'exam_procedure', 'Bx_result', 'follow_up']
#     success_url = reverse_lazy('procedure:today')
#
#
# class MonthUpdateview(LoginRequiredMixin, UpdateView):
#     model = Exam
#     fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
#               'patient_sex', 'patient_birth', 'patient_phone', 'exam_Dx', 'exam_procedure', 'Bx_result', 'follow_up']
#     success_url = reverse_lazy('procedure:thismonth')
#
#
# class BxListView(LoginRequiredMixin, ListView):
#     template_name = 'procedure/Bx_list.html'
#     context_object_name = 'object_list'
#
#     def get_queryset(self):
#         result = Exam.objects.filter(Q(exam_procedure__icontains='Bx') |
#                                      Q(exam_procedure__icontains='Polypectomy') |
#                                      Q(exam_procedure__icontains='EMR')).distinct()
#         return result
#
#
# class BxCallView(LoginRequiredMixin, ListView):
#     template_name = 'procedure/Bx_call.html'
#     context_object_name = 'object_list'
#
#     def get_queryset(self):
#         result = Exam.objects.filter(Q(exam_date__gte=date(2017, 2, 27)) &
#                                      (Q(exam_procedure__icontains='Bx') |
#                                       Q(exam_procedure__icontains='Polypectomy') |
#                                       Q(exam_procedure__icontains='EMR'))).distinct()
#         return result
#

# class ReadingUpdateview(LoginRequiredMixin, UpdateView):
#     model = Exam
#     fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
#               'patient_sex', 'patient_birth', 'patient_phone', 'exam_Dx', 'exam_procedure', 'Bx_result', 'follow_up']
#     success_url = reverse_lazy('procedure:readinglist')
#
#
# class ReadingListView(LoginRequiredMixin, ListView):
#     template_name = 'procedure/reading_list.html'
#     context_object_name = 'object_list'
#
#     def get_queryset(self):
#         result = Exam.objects.filter(exam_Dx='.')
#         return result


def add_month(date, months):
    month = date.month + int(months) - 1
    year = int(date.year + (month / 12))
    month = (month % 12) + 1
    day = date.day
    new_date = date.replace(year=year, month=month, day=1)
    return new_date


@login_required
def phone(request):
    today = date.today()
    all_endoscopy = Endoscopy.objects.all()

    context = {}
    will_call_list={}
    called_list={}
    visited_list ={}
    for endoscopy in all_endoscopy:
        patient_id = endoscopy.patient_id
        patient = Patient.objects.get(id = patient_id)
        patient_info = collections.OrderedDict()
        call_date = add_month(endoscopy.date, endoscopy.followup_period)
        if today.year == call_date.year and today.month == call_date.month:
            if endoscopy.date.year == today.year and endoscopy.date.month == today.month:
                continue;
            else:
                if endoscopy.re_visit_call == '.':
                    patient_info['name'] = patient.name
                    patient_info['sex']=patient.sex
                    patient_info['hospital_no'] = patient.hospital_no
                    patient_info['birth']=patient.birth
                    patient_info['age']=age(patient.birth)
                    patient_info['phone']=patient.phone
                    patient_info['date']=endoscopy.date
                    patient_info['endo_type']=','.join([each[0] for each in endoscopy.type])
                    patient_info['doc']=endoscopy.doc
                    patient_info['Dx']=endoscopy.Dx
                    patient_info['Bx_result']=endoscopy.Bx_result
                    will_call_list[patient_id]=patient_info
                elif endoscopy.re_visit_call != '.':
                    if endoscopy.re_visit == True:
                        patient_info['name'] = patient.name
                        patient_info['sex'] = patient.sex
                        patient_info['hospital_no'] = patient.hospital_no
                        patient_info['birth'] = patient.birth
                        patient_info['age'] = age(patient.birth)
                        patient_info['phone'] = patient.phone
                        patient_info['date'] = endoscopy.date
                        patient_info['endo_type'] = ','.join([each[0] for each in endoscopy.type])
                        patient_info['doc'] = endoscopy.doc
                        patient_info['Dx'] = endoscopy.Dx
                        patient_info['Bx_result'] = endoscopy.Bx_result
                        patient_info['dialog']=endoscopy.re_visit_call
                        visited_list[patient_id]=patient_info
                    else:
                        patient_info['name'] = patient.name
                        patient_info['sex'] = patient.sex
                        patient_info['hospital_no'] = patient.hospital_no
                        patient_info['birth'] = patient.birth
                        patient_info['age'] = age(patient.birth)
                        patient_info['phone'] = patient.phone
                        patient_info['date'] = endoscopy.date
                        patient_info['endo_type'] = ','.join([each[0] for each in endoscopy.type])
                        patient_info['doc'] = endoscopy.doc
                        patient_info['Dx'] = endoscopy.Dx
                        patient_info['Bx_result'] = endoscopy.Bx_result
                        patient_info['dialog'] = endoscopy.re_visit_call
                        called_list[patient_id]=patient_info
    will_call_list = OrderedDict(sorted(will_call_list.items(), key= lambda x: x[1]['date'], reverse=True))
    called_list = OrderedDict(sorted(called_list.items(), key=lambda x: x[1]['date'], reverse=True))
    visited_list = OrderedDict(sorted(visited_list.items(), key=lambda x: x[1]['date'], reverse=True))
    context['will_call_list'] = will_call_list
    context['called_list'] = called_list
    context['visited_list']=visited_list

    context['will_call_number'] = len(context['will_call_list'])
    context['visited_number'] = len(context['visited_list'])
    context['called_number'] = len(context['called_list']) + context['visited_number']
    context['total_number'] = context['will_call_number'] + context['called_number']
    if context['total_number'] == 0:
        context['phoned_fraction'], context['visited_fraction'] = 0, 0
    else:
        context['called_fraction'] = round(float(context['called_number']) / context['total_number'] * 100)
        context['visited_fraction'] = round(float(context['visited_number']) / context['total_number'] * 100)

    return render(request, 'procedure/phone_list.html', context)


# class PhoneCheck(LoginRequiredMixin, UpdateView):
#     model = Exam
#     template_name = 'procedure/phone_check.html'
#     fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
#               'patient_sex', 'patient_birth', 'patient_phone', 'exam_Dx', 'exam_procedure', 'Bx_result', 'phone_check',
#               'follow_up']
#     success_url = reverse_lazy('procedure:phone')
#
#
# class ReVisit(LoginRequiredMixin, UpdateView):
#     model = Exam
#     template_name = 'procedure/re_visit.html'
#     fields = ['exam_date', 'exam_type', 'exam_doc', 'exam_class', 'exam_place', 'patient_name', 'hospital_no',
#               'patient_sex', 'patient_birth', 'patient_phone', 'exam_Dx', 'exam_procedure', 'Bx_result', 'phone_check',
#               're_visit']
#     success_url = reverse_lazy('procedure:phone')


@login_required
def today(request):
    today = date.today()
    g_egd = 0  # 건진위내시경
    j_egd = 0  # 진료위내시경
    g_colon = 0  # 건진대장내시경
    j_colon = 0  # 진료대장내시경
    sig = 0

    all_patients = Exam.objects.all()
    context = {'object_list': [], 'g_egd': 0, 'j_egd': 0, 'total_egd': 0, 'g_colon': 0, 'j_colon': 0, 'total_colon': 0,
               'sig': 0}
    for patient in all_patients:
        if patient.exam_date == today:
            context['object_list'].append(patient)
            if 'E' in patient.exam_type:
                if patient.exam_class == '건진':
                    g_egd += 1
                elif patient.exam_class == "진료":
                    j_egd += 1
                elif patient.exam_class == "건진+진료":
                    g_egd += 1
            if 'C' in patient.exam_type:
                if patient.exam_class == "건진":
                    g_colon += 1
                elif patient.exam_class == "진료":
                    j_colon += 1
                elif patient.exam_class == "건진+진료":
                    j_colon += 1
            if 'S' in patient.exam_type: sig += 1
    context['g_egd'] = g_egd
    context['j_egd'] = j_egd
    context['total_egd'] = g_egd + j_egd
    context['g_colon'] = g_colon
    context['j_colon'] = j_colon
    context['total_colon'] = g_colon + j_colon
    context['sig'] = sig
    return render(request, 'procedure/today_list.html', context)

#
# @login_required
# def thismonth(request):
#     g_egd = 0  # 건진위내시경
#     j_egd = 0  # 진료위내시경
#     g_colon = 0  # 건진대장내시경
#     j_colon = 0  # 진료대장내시경
#     sig = 0
#     first_colon = 0
#     second_colon = 0
#     first_polyp = 0
#     second_polyp = 0
#     first_adenoma = 0
#     second_adenoma = 0
#     today = date.today()
#     this_month = today.month
#     this_year = today.year
#
#     monthly_data = Exam.objects.filter(exam_date__year=this_year).filter(exam_date__month=this_month)
#     g_egd = monthly_data.filter(exam_type__contains='E').filter(exam_class__contains="건진").count()
#     j_egd = monthly_data.filter(exam_type__contains='E').filter(exam_class__contains="진료").exclude(
#         exam_class="건진+진료").count()
#     g_colon = monthly_data.filter(exam_type__contains='C').filter(exam_class__contains="건진").exclude(
#         exam_class="건진+진료").count()
#     j_colon = monthly_data.filter(exam_type__contains='C').filter(exam_class__contains="진료").count()
#     sig = monthly_data.filter(exam_type__contains='S').count()
#     first_colon = monthly_data.filter(exam_doc='이영재').filter(exam_type__contains='C').count()
#     second_colon = monthly_data.filter(exam_doc='김신일').filter(exam_type__contains='C').count()
#     first_polyp = monthly_data.filter(exam_doc='이영재').filter(exam_type__contains='C').filter(
#         exam_Dx__contains='polyp').count()
#     second_polyp = monthly_data.filter(exam_doc='김신일').filter(exam_type__contains='C').filter(
#         exam_Dx__contains='polyp').count()
#     first_adenoma = monthly_data.filter(exam_doc='이영재').filter(exam_type__contains='C').filter(
#         Bx_result__contains='adenoma').count()
#     second_adenoma = monthly_data.filter(exam_doc='김신일').filter(exam_type__contains='C').filter(
#         Bx_result__contains='adenoma').count()
#
#     context = {'object_list': [], 'g_egd': 0, 'j_egd': 0, 'total_egd': 0, 'g_colon': 0, 'j_colon': 0, 'total_colon': 0,
#                'sig': 0, 'first_colon': 0,
#                'first_polyp_rate': 0, 'first_adr': 0, 'second_colon': 0, 'second_polyp_rate': 0, 'second_adr': 0,
#                'total_polyp_rate': 0, 'total_adenoma_rate': 0}
#
#     context['object_list'] = monthly_data
#     context['g_egd'] = g_egd
#     context['j_egd'] = j_egd
#     context['total_egd'] = g_egd + j_egd
#     context['g_colon'] = g_colon
#     context['j_colon'] = j_colon
#     context['total_colon'] = g_colon + j_colon
#     context['sig'] = sig
#     context['first_colon'] = first_colon
#     context['second_colon'] = second_colon
#     if first_colon != 0:
#         context['first_polyp_rate'] = int(float(first_polyp) / first_colon * 100)
#         context['first_adr'] = int(float(first_adenoma) / first_colon * 100)
#     else:
#         context['first_polyp_rate'] = '0'
#     if second_colon != 0:
#         context['second_polyp_rate'] = int(float(second_polyp) / second_colon * 100)
#         context['second_adr'] = int(float(second_adenoma) / second_colon * 100)
#     else:
#         context['second_polyp_rate'] = '0'
#
#     if context['total_colon'] != 0:
#         context['total_polyp_rate'] = int(float(first_polyp + second_polyp) / context['total_colon'] * 100)
#         context['total_adenoma_rate'] = int(float(first_adenoma + second_adenoma) / context['total_colon'] * 100)
#     else:
#         context['total_polyp_rate'], context['total_adenoma_rate'] = '0', '0'
#
#     return render(request, 'procedure/this_month_list.html', context)


@login_required
def thismonth_for_ajax(request):
    g_egd = 0  # 건진위내시경
    j_egd = 0  # 진료위내시경
    g_colon = 0  # 건진대장내시경
    j_colon = 0  # 진료대장내시경
    sig = 0
    first_colon = 0
    second_colon = 0
    first_polyp = 0
    second_polyp = 0
    first_adenoma = 0
    second_adenoma = 0

    year = request.POST.get('year')
    month = request.POST.get('month')

    monthly_data = Endoscopy.objects.filter(date__year=year).filter(date__month=month)
    g_egd = monthly_data.filter(type__contains='E').filter(source__contains="건진").count()
    j_egd = monthly_data.filter(type__contains='E').filter(source__contains="진료").exclude(
        source="건진+진료").count()
    g_colon = monthly_data.filter(type__contains='C').filter(source__contains="건진").exclude(
        source="건진+진료").count()
    j_colon = monthly_data.filter(type__contains='C').filter(source__contains="진료").count()
    sig = monthly_data.filter(type__contains='S').count()
    first_colon = monthly_data.filter(doc='이영재').filter(type__contains='C').count()
    second_colon = monthly_data.filter(doc='김신일').filter(type__contains='C').count()
    first_polyp = monthly_data.filter(doc='이영재').filter(type__contains='C').filter(
        Dx__contains='polyp').count()
    second_polyp = monthly_data.filter(doc='김신일').filter(type__contains='C').filter(
        Dx__contains='polyp').count()
    first_adenoma = monthly_data.filter(doc='이영재').filter(type__contains='C').filter(
        Bx_result__contains='adenoma').count()
    second_adenoma = monthly_data.filter(doc='김신일').filter(type__contains='C').filter(
        Bx_result__contains='adenoma').count()

    context = {'g_egd': 0, 'j_egd': 0, 'total_egd': 0, 'g_colon': 0, 'j_colon': 0, 'total_colon': 0, 'sig': 0,
               'first_colon': 0, 'first_polyp_rate': 0, 'first_adr': 0, 'second_colon': 0, 'second_polyp_rate': 0,
               'second_adr': 0, 'total_polyp_rate': 0, 'total_adenoma_rate': 0}

    context['g_egd'] = g_egd
    context['j_egd'] = j_egd
    context['total_egd'] = g_egd + j_egd
    context['g_colon'] = g_colon
    context['j_colon'] = j_colon
    context['total_colon'] = g_colon + j_colon
    context['sig'] = sig
    context['first_colon'] = first_colon
    context['second_colon'] = second_colon
    if first_colon != 0:
        context['first_polyp_rate'] = int(float(first_polyp) / first_colon * 100)
        context['first_adr'] = int(float(first_adenoma) / first_colon * 100)
    else:
        context['first_polyp_rate'] = '0'
    if second_colon != 0:
        context['second_polyp_rate'] = int(float(second_polyp) / second_colon * 100)
        context['second_adr'] = int(float(second_adenoma) / second_colon * 100)
    else:
        context['second_polyp_rate'] = '0'

    if context['total_colon'] != 0:
        context['total_polyp_rate'] = int(float(first_polyp + second_polyp) / context['total_colon'] * 100)
        context['total_adenoma_rate'] = int(float(first_adenoma + second_adenoma) / context['total_colon'] * 100)
    else:
        context['total_polyp_rate'], context['total_adenoma_rate'] = '0', '0'

    return HttpResponse(json.dumps(context), content_type="application/json")

class PatientInfoUpdateview(LoginRequiredMixin, UpdateView):
    model = Patient
    fields = all
    fields = ['name', 'hospital_no', 'sex', 'birth', 'phone', 'address']
    template_name = 'procedure/patient_info_update.html'
    def get_success_url(self):
        return reverse('procedure:each_day_patient_info', kwargs={'pk':self.object.pk})

class EndoscopyInfoUpdateview(LoginRequiredMixin, UpdateView):
    model = Endoscopy
    fields = ['date', 'type', 'doc', 'source', 'place', 'Dx','procedure','Bx_result','Bx_result_call','followup_period',
              're_visit_call','re_visit','re_visit_date']
    template_name = 'procedure/endoscopy_info_update.html'
    def get_success_url(self):
        return reverse('procedure:each_day_patient_info', kwargs={'pk':self.object.patient_id})

class EndoscopyInfoUpdateForRevisitview(LoginRequiredMixin, UpdateView):
    model = Endoscopy
    fields = ['date', 'type', 'doc', 'source', 'place', 'Dx','procedure','Bx_result','Bx_result_call','followup_period',
              're_visit_call','re_visit','re_visit_date']
    template_name = 'procedure/endoscopy_info_update.html'
    def get_success_url(self):
        return reverse('procedure:re_visit_patient_info', kwargs={'pk':self.object.patient_id})


def each_day_patient_info(request, pk = None):
    if pk is None:
        patient_id = request.POST.get('patient_id')
        patient = Patient.objects.get(id=patient_id)
        endoscopy = Endoscopy.objects.filter(patient_id = patient_id)
    else :
        patient_id =pk
        patient = Patient.objects.get(id=patient_id)
        endoscopy = Endoscopy.objects.filter(patient_id=patient_id)
    context ={}
    context['url'] = '/procedure/each_day_patient_info_detail'
    context['patient_id'] = patient_id
    context['name'] = patient.name
    context['hospital_no'] = patient.hospital_no
    context['sex']=patient.sex
    context['birth'] = patient.birth
    context['age']=age(patient.birth)
    context['phone']=patient.phone
    context['address']=patient.address
    endo_context = {}
    for exam in endoscopy:
        endo_context[exam.date]={}
        endo_context[exam.date]['id']=exam.id
        endo_context[exam.date]['type']=exam.type
        endo_context[exam.date]['doc'] = exam.doc
        endo_context[exam.date]['source']=exam.source
        endo_context[exam.date]['place']=exam.place
        endo_context[exam.date]['Dx'] = exam.Dx
        endo_context[exam.date]['procedure']=exam.procedure
        endo_context[exam.date]['Bx_result'] = exam.Bx_result

    endo_context = collections.OrderedDict(sorted(endo_context.items(), reverse=True))
    context['endo_context'] = endo_context
    return render(request, 'procedure/each_day_patient_info.html', context)

def re_visit_patient_info(request, pk = None):
    if pk is None:
        patient_id = request.POST.get('patient_id')
        patient = Patient.objects.get(id=patient_id)
        endoscopy = Endoscopy.objects.filter(patient_id = patient_id)
    else :
        patient_id =pk
        patient = Patient.objects.get(id=patient_id)
        endoscopy = Endoscopy.objects.filter(patient_id=patient_id)
    context ={}
    context['url'] = '/procedure/each_day_patient_info_detail'
    context['patient_id'] = patient_id
    context['name'] = patient.name
    context['hospital_no'] = patient.hospital_no
    context['sex']=patient.sex
    context['birth'] = patient.birth
    context['age']=age(patient.birth)
    context['phone']=patient.phone
    context['address']=patient.address
    endo_context = {}
    for exam in endoscopy:
        endo_context[exam.date]={}
        endo_context[exam.date]['id']=exam.id
        endo_context[exam.date]['type']=exam.type
        endo_context[exam.date]['doc'] = exam.doc
        endo_context[exam.date]['source']=exam.source
        endo_context[exam.date]['place']=exam.place
        endo_context[exam.date]['Dx'] = exam.Dx
        endo_context[exam.date]['procedure']=exam.procedure
        endo_context[exam.date]['Bx_result'] = exam.Bx_result

    endo_context = collections.OrderedDict(sorted(endo_context.items(), reverse=True))
    context['endo_context'] = endo_context
    return render(request, 'procedure/re_visit_patient_info.html', context)

def each_day_mouse_on_for_ajax(request):
    selected_year = request.POST.get('year')
    selected_month = request.POST.get('month')
    selected_date = request.POST.get('date')
    context = {}
    fulldate = selected_year + "-" + str(int(selected_month) + 1) + "-" + selected_date
    each_day_endoscopy_list = Endoscopy.objects.filter(date=fulldate)
    g_egd = each_day_endoscopy_list.filter(type__contains='E').filter(source="건진").count()
    g_egd+= each_day_endoscopy_list.filter(type__contains='E').filter(source="건진+진료").count()
    j_egd = each_day_endoscopy_list.filter(type__contains='E').filter(source="진료").count()
    total_egd = g_egd + j_egd
    g_colon = each_day_endoscopy_list.filter(type__contains='C').filter(source="건진").count()
    j_colon = each_day_endoscopy_list.filter(type__contains='C').filter(source="진료").count()
    j_colon+= each_day_endoscopy_list.filter(type__contains='C').filter(source="건진+진료").count()
    total_colon = g_colon + j_colon
    sig = each_day_endoscopy_list.filter(type__contains='S').count()
    context['g_egd']=g_egd
    context['j_egd'] = j_egd
    context['total_egd'] = total_egd
    context['g_colon'] = g_colon
    context['j_colon'] = j_colon
    context['total_colon'] = total_colon
    context['sig'] = sig
    return HttpResponse(json.dumps(context), content_type="application/json")

# 메인보드에 조직검사 소견 미입력자 출력하는 함수입니다. home2.html의 조직검사-> 입력해주세요 를 클릭해서 bxInut 함수가 호출되면 이 함수로 연결됩니다.
def bx_input_for_ajax(request):
    context ={}
    endoscopy_without_Bx_result = Endoscopy.objects.filter(Q(procedure__icontains = 'Bx') | Q(procedure__icontains="Polypectomy")|Q(procedure__icontains="EMR")).distinct()
    endoscopy_without_Bx_result = endoscopy_without_Bx_result.filter(Q(Bx_result = '.') | Q(Bx_result=''))
    endo_list_num = endoscopy_without_Bx_result.count()
    for exam in endoscopy_without_Bx_result:
        patient = Patient.objects.get(id = exam.patient_id)
        patient_id = patient.id
        exam_date = exam.date.strftime('%y/%m/%d')
        hospital_no = patient.hospital_no
        patient_age = age(patient.birth)
        birth_string = patient.birth.strftime('%y/%m/%d')
        context[patient.name] = {'id': patient_id, 'date':exam_date, 'hospital_no': hospital_no, 'age': patient_age, 'birthday': birth_string,
                                 'type': exam.type, 'doc': exam.doc, 'sex': patient.sex, 'procedure':exam.procedure}
    context = OrderedDict(sorted(context.items(), key=lambda x: x[1]['date']))
    context['endo_list_num'] = endo_list_num
    return HttpResponse(json.dumps(context), content_type="application/json")

def bx_noti_for_ajax(request):
    context ={}
    endoscopy_without_Bx_noti = Endoscopy.objects.filter(Q(date__gte=date(2017, 2, 27)) &
                                                          (Q(procedure__icontains = 'Bx') | Q(procedure__icontains="Polypectomy")|Q(procedure__icontains="EMR")) &
                                                          (Q(Bx_result_call='.') | Q(Bx_result_call='')))
    endoscopy_without_Bx_noti = endoscopy_without_Bx_noti.exclude(Bx_result='.').exclude(Bx_result='')
    endo_list_num = endoscopy_without_Bx_noti.count()
    for exam in endoscopy_without_Bx_noti:
        patient = Patient.objects.get(id = exam.patient_id)
        patient_id = patient.id
        exam_date = exam.date.strftime('%y/%m/%d')
        hospital_no = patient.hospital_no
        patient_age = age(patient.birth)
        birth_string = patient.birth.strftime('%y/%m/%d')
        context[patient.name] = {'id': patient_id, 'date':exam_date, 'hospital_no': hospital_no, 'age': patient_age, 'birthday': birth_string,
                                 'type': exam.type, 'doc': exam.doc, 'sex': patient.sex, 'Bx_result':exam.Bx_result}
    context = OrderedDict(sorted(context.items(), key = lambda x: x[1]['date']))
    context['endo_list_num'] = endo_list_num
    return HttpResponse(json.dumps(context), content_type="application/json")

def reading_input_for_ajax(request):
    context = {}
    endoscopy_without_reading = Endoscopy.objects.filter(Dx = '.').distinct()
    endo_list_num = endoscopy_without_reading.count()
    for exam in endoscopy_without_reading:
        patient = Patient.objects.get(id=exam.patient_id)
        patient_id = patient.id
        exam_date = exam.date.strftime('%y/%m/%d')
        hospital_no = patient.hospital_no
        patient_age = age(patient.birth)
        birth_string = patient.birth.strftime('%y/%m/%d')
        context[patient.name] = {'id': patient_id, 'date': exam_date, 'hospital_no': hospital_no, 'age': patient_age,
                                 'birthday': birth_string, 'type': exam.type, 'doc': exam.doc, 'sex': patient.sex, 'procedure':exam.procedure}
    context = OrderedDict(sorted(context.items(), key=lambda x: x[1]['date']))
    context['endo_list_num'] = endo_list_num
    return HttpResponse(json.dumps(context), content_type="application/json")

def each_day_patient_list_for_ajax(request):
    selected_year = request.POST.get('year')
    selected_month = request.POST.get('month')
    selected_date = request.POST.get('date')
    context={}
    fulldate = selected_year + "-" + str(int(selected_month)+1) + "-" + selected_date
    fulldate_hangul = selected_year + "년 " + str(int(selected_month) + 1) + "월 " + selected_date+"일"
    each_day_endoscopy_list = Endoscopy.objects.filter(date = fulldate)
    g_egd = each_day_endoscopy_list.filter(type__contains='E').filter(source__contains="건진").count()
    j_egd = each_day_endoscopy_list.filter(type__contains='E').filter(source__contains="진료").count()
    total_egd = g_egd + j_egd
    g_colon = each_day_endoscopy_list.filter(type__contains='C').filter(source__contains="건진").count()
    j_colon = each_day_endoscopy_list.filter(type__contains='C').filter(source__contains="진료").count()
    total_colon  = g_colon + j_colon
    sig = each_day_endoscopy_list.filter(type__contains='S').count()
    for exam in each_day_endoscopy_list:
        patient = Patient.objects.get(id = exam.patient_id)
        patient_id = patient.id
        hospital_no = patient.hospital_no
        patient_age = age(patient.birth)
        birth_string = patient.birth.strftime('%y/%m/%d')
        context[patient.name]={'id':patient_id, 'hospital_no':hospital_no,  'age':patient_age, 'birthday':birth_string,
                               'type': exam.type, 'doc': exam.doc, 'sex':patient.sex, 'Dx':exam.Dx, 'procedure':exam.procedure,
                               'g_egd':g_egd, 'j_egd':j_egd, 'total_egd':total_egd, 'g_colon':g_colon, 'j_colon':j_colon, 'total_colon':total_colon,
                               'sig':sig
                               }
    context['selected_day'] = fulldate_hangul
    return HttpResponse(json.dumps(context), content_type="application/json")

def age(birth_date):
    today = date.today()
    y = today.year - birth_date.year
    if today.month < birth_date.month or today.month == birth_date.month and today.day < birth_date.day:
        y -= 1
    return y

def re_visited(current_year, current_month, objects):
    visited = 0
    call = 0
    for endoscopy in objects:
        follow_up_date = add_month(endoscopy.date, endoscopy.followup_period)
        if follow_up_date.year == current_year and follow_up_date.month == current_month and endoscopy.followup_period != 0:
            call += 1
            if endoscopy.re_visit == True:
                visited += 1
    return int(float(visited) / call * 100)


def thisyear(request):
    this_month = date.today().month

    g_egd = 0  # 건진위내시경
    j_egd = 0  # 진료위내시경
    g_colon = 0  # 건진대장내시경
    j_colon = 0  # 진료대장내시경
    sig = 0
    first_colon = 0
    second_colon = 0
    first_polyp = 0
    second_polyp = 0
    first_adenoma = 0
    second_adenoma = 0
    total_sum_re_visit = 0
    today = date.today()
    this_month = today.month
    this_year = today.year

    monthly_total_data = collections.OrderedDict()
    until_now_total = {'until_now_total_egd': 0, 'until_now_g_egd': 0, 'until_now_j_egd': 0,
                       'until_now_first_colon': 0, 'until_now_second_colon': 0, 'until_now_g_colon': 0,
                       'until_now_j_colon': 0, 'until_now_total_colon': 0,
                       'until_now_total_colon_including_sig': 0,
                       'until_now_first_polyp': 0, 'until_now_second_polyp': 0,
                       'until_now_average_first_pdr': 0, 'until_now_average_second_pdr': 0,
                       'until_now_total_average_pdr': 0,
                       'until_now_first_adenoma': 0, 'until_now_second_adenoma': 0,
                       'until_now_average_first_adr': 0, 'until_now_second_adr': 0, 'until_now_total_average_adr': 0,
                       'until_now_PEG': 0, 'until_now_re_visit': 0}

    for month in range(1, this_month + 1):
        context = {'g_egd': 0, 'j_egd': 0, 'total_egd': 0, 'g_colon': 0, 'j_colon': 0, 'total_colon': 0,
                   'sig': 0, 'sig_included_toal_colon': 0, 'j_colon_including_sig': 0,
                   'first_colon': 0, 'first_polyp_rate': 0, 'first_adr': 0,
                   'second_colon': 0, 'second_polyp_rate': 0, 'second_adr': 0,
                   'total_polyp_rate': 0, 'total_adenoma_rate': 0, 'PEG': 0, 're_visit': 0}

        monthly_data = Endoscopy.objects.filter(date__year=this_year).filter(date__month=month)
        g_egd = monthly_data.filter(type__contains='E').filter(source__contains="건진").count()
        j_egd = monthly_data.filter(type__contains='E').filter(source__contains="진료").exclude(
            source="건진+진료").count()
        g_colon = monthly_data.filter(type__contains='C').filter(source__contains="건진").exclude(
            source="건진+진료").count()
        j_colon = monthly_data.filter(type__contains='C').filter(source__contains="진료").count()
        sig = monthly_data.filter(type__contains='S').count()
        first_colon = monthly_data.filter(doc='이영재').filter(type__contains='C').count()
        second_colon = monthly_data.filter(doc='김신일').filter(type__contains='C').count()
        first_polyp = monthly_data.filter(doc='이영재').filter(type__contains='C').filter(
            Dx__contains='polyp').count()
        second_polyp = monthly_data.filter(doc='김신일').filter(type__contains='C').filter(
            Dx__contains='polyp').count()
        first_adenoma = monthly_data.filter(doc='이영재').filter(type__contains='C').filter(
            Bx_result__contains='adenoma').count()
        second_adenoma = monthly_data.filter(doc='김신일').filter(type__contains='C').filter(
            Bx_result__contains='adenoma').count()
        PEG = monthly_data.filter(procedure=['PEG']).count()

        context['g_egd'] = g_egd
        context['j_egd'] = j_egd
        context['total_egd'] = g_egd + j_egd
        until_now_total['until_now_g_egd'] += g_egd
        until_now_total['until_now_j_egd'] += j_egd
        until_now_total['until_now_total_egd'] += context['total_egd']

        context['g_colon'] = g_colon
        context['j_colon'] = j_colon
        context['total_colon'] = g_colon + j_colon
        until_now_total['until_now_g_colon'] += g_colon
        until_now_total['until_now_j_colon'] += j_colon + sig
        until_now_total['until_now_total_colon_including_sig'] += g_colon + j_colon + sig

        context['sig'] = sig
        context['sig_included_total_colon'] = g_colon + j_colon + sig
        context['j_colon_including_sig'] = j_colon + sig
        context['first_colon'] = first_colon
        context['second_colon'] = second_colon

        context['PEG'] = PEG
        until_now_total['until_now_PEG'] += PEG

        context['re_visit'] = re_visited(this_year, month, Endoscopy.objects.all())
        total_sum_re_visit += context['re_visit']

        if first_colon != 0:
            until_now_total['until_now_first_colon'] += first_colon
            until_now_total['until_now_first_polyp'] += first_polyp
            context['first_polyp_rate'] = int(float(first_polyp) / first_colon * 100)
            until_now_total['until_now_first_adenoma'] += first_adenoma
            context['first_adr'] = int(float(first_adenoma) / first_colon * 100)
        else:
            context['first_polyp_rate'] = '0'

        if second_colon != 0:
            until_now_total['until_now_second_colon'] += second_colon
            until_now_total['until_now_second_polyp'] += second_polyp
            context['second_polyp_rate'] = int(float(second_polyp) / second_colon * 100)
            until_now_total['until_now_second_adenoma'] += second_adenoma
            context['second_adr'] = int(float(second_adenoma) / second_colon * 100)
        else:
            context['second_polyp_rate'] = '0'

        if context['total_colon'] != 0:
            context['total_polyp_rate'] = int(float(first_polyp + second_polyp) / context['total_colon'] * 100)
            context['total_adenoma_rate'] = int(float(first_adenoma + second_adenoma) / context['total_colon'] * 100)
        else:
            context['total_polyp_rate'], context['total_adenoma_rate'] = '0', '0'

        monthly_total_data[str(month)] = context

    until_now_total['until_now_total_colon'] = until_now_total['until_now_first_colon'] + until_now_total[
        'until_now_second_colon']
    until_now_total['until_now_average_first_pdr'] = int(float(until_now_total['until_now_first_polyp']) /
                                                         until_now_total['until_now_first_colon'] * 100)
    until_now_total['until_now_average_second_pdr'] = int(float(until_now_total['until_now_second_polyp']) /
                                                          until_now_total['until_now_second_colon'] * 100)
    until_now_total['until_now_total_average_pdr'] = int(
        float(until_now_total['until_now_first_polyp'] + until_now_total['until_now_second_polyp']) / until_now_total[
            'until_now_total_colon'] * 100)
    until_now_total['until_now_average_first_adr'] = int(float(until_now_total['until_now_first_adenoma']) /
                                                         until_now_total['until_now_first_colon'] * 100)
    until_now_total['until_now_average_second_adr'] = int(float(until_now_total['until_now_second_adenoma']) /
                                                          until_now_total['until_now_second_colon'] * 100)
    until_now_total['until_now_total_average_adr'] = int(
        float(until_now_total['until_now_first_adenoma'] + until_now_total['until_now_second_adenoma']) /
        until_now_total[
            'until_now_total_colon'] * 100)
    until_now_total['until_now_re_visit'] = int(float(total_sum_re_visit) / len(monthly_total_data))
    return render(request, 'procedure/this_year_summary.html',
                  {'monthly_total_data': monthly_total_data, 'until_now_total': until_now_total})


def year_data(year):
    egd = 0
    colon = 0

    all_endoscopy = Endoscopy.objects.all()

    all_month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    monthly_egd = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}
    monthly_colon = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}

    for endoscopy in all_endoscopy:
        endoscopy_year = endoscopy.date.year
        endoscopy_month = endoscopy.date.month
        for month in range(1, 13):
            if endoscopy_year == year and endoscopy_month == month:
                if 'E' in endoscopy.type:
                    monthly_egd[month] += 1
                if 'C' in endoscopy.type or 'S' in endoscopy.type:
                    monthly_colon[month] += 1

    return list(monthly_egd.values()), list(monthly_colon.values())
#
#
# def graph(request):
#     data = year_data()
#     data_source = SimpleDataSource(data=data)
#     chart = ColumnChart(data_source, options={'title': "올해 내시경 추이"})
#     context = {'chart': chart}
#     return render(request, 'procedure/year_graph.html', context)


@login_required
def homegraph(request):
    today = date.today()
    monthly_egd, monthly_colon = year_data(today.year)
    #total_months = [1,2,3,4,5,6,7,8,9,10,11,12]
    #egd_2015 = [436, 298, 155, 110, 54, 65, 67, 51, 61, 85, 114, 185]
    #colon_2015 =[19, 12, 29, 27, 11, 4, 19, 8, 10, 15, 19, 38]
    #egd_2016 = [291, 219, 102, 84, 65, 92, 73, 79, 70, 84, 123, 163]
    #colon_2016 = [20, 23, 40, 43, 30, 35, 28, 29, 17, 21, 29, 50]

    source = ColumnDataSource(
        data={'total_months':[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 'egd_2015':[436, 298, 155, 110, 54, 65, 67, 51, 61, 85, 114, 185],
              'egd_2016':[291, 219, 102, 84, 65, 92, 73, 79, 70, 84, 123, 163],
              'egd_2017':[220,259,160,110,107,96,98,85,84,75,111,184], 'monthly_egd':monthly_egd,
              'colon_2015':[19, 12, 29, 27, 11, 4, 19, 8, 10, 15, 19, 38], 'colon_2016':[20, 23, 40, 43, 30, 35, 28, 29, 17, 21, 29, 50],
              'colon_2017':[25,48,40,18,30,29,39,31,28,23,51,33],
              'monthly_colon':monthly_colon})

    egd = figure(x_axis_type ='datetime', x_axis_label ='월', y_axis_label = '개수', width=1000, height=330,  tools=[], toolbar_location = "above")
    #egd.background_fill_color = 'LightCyan'
    e1=egd.vbar(x='total_months', width=0.5, bottom=0, top='monthly_egd', color='firebrick', alpha = 0.8, source=source)
    egd.add_tools(HoverTool(renderers = [e1], tooltips=[("개수", '@monthly_egd')]))
    e2=egd.circle('total_months','egd_2017', size = 10,  color='navy', source=source)
    egd.add_tools(HoverTool(renderers=[e2], tooltips=[("개수", '@egd_2017')]))
    e3=egd.circle('total_months', 'egd_2016', size=10, color='DarkCyan', source=source)
    egd.add_tools(HoverTool(renderers=[e3], tooltips=[("개수", '@egd_2016')]))
    e4=egd.circle('total_months', 'egd_2015', size=10, color='yellow', source=source)
    egd.add_tools(HoverTool(renderers=[e4], tooltips=[("개수", '@egd_2015')]))

    egd_tab = Panel(child = egd, title = "위내시경 추이")

    egd_legend = Legend(items = [
        ("2018년", [e1]),
        ("2017년", [e2]),
        ("2016년", [e3]),
        ("2015년",[e4]),], location = (0,-30))
    egd_legend.border_line_color = 'SkyBlue'
    egd_legend.border_line_width = 3
    egd.add_layout(egd_legend, 'right')

    colon = figure(x_axis_type ='datetime', x_axis_label ='월', y_axis_label = '개수', width = 1000, height=330, tools=[], toolbar_location = "above")
    c1=colon.vbar(x='total_months', width=0.5, bottom=0, top='monthly_colon', color='firebrick', alpha = 0.8, source=source)
    colon.add_tools(HoverTool(renderers=[c1], tooltips=[("개수", '@monthly_colon')]))
    c2 =colon.circle('total_months','colon_2017', size = 10,  color='navy', source=source)
    colon.add_tools(HoverTool(renderers=[c2], tooltips=[("개수", '@colon_2017')]))
    c3 =colon.circle('total_months', 'colon_2016', size=10,  color='DarkCyan', source=source)
    colon.add_tools(HoverTool(renderers=[c3], tooltips=[("개수", '@colon_2016')]))
    c4 = colon.circle('total_months', 'colon_2015', size=10, color='yellow', source=source)
    colon.add_tools(HoverTool(renderers=[c4], tooltips=[("개수", '@colon_2015')]))

    colon_legend = Legend(items=[("2018년", [c1]), ("2017년", [c2]), ("2016년", [c3]), ("2015년", [c4]), ], location=(0, -30))
    colon_legend.border_line_color = 'SkyBlue'
    colon_legend.border_line_width = 3
    colon.add_layout(colon_legend, 'right')

    colon_tab = Panel(child=colon, title = "대장내시경 추이")
    layout = Tabs(tabs = [egd_tab, colon_tab])

    if sys.platform.startswith('win32'):
        output_file('procedure/templates/procedure/vbar.html')
        save(layout)
        return render(request, 'procedure/vbar.html')
    else:
        output_file('/home/nokdong/Endoweb2/procedure/templates/procedure/vbar.html')
        save(layout)
        return render(request, '/home/nokdong/Endoweb2/procedure/templates/procedure/vbar.html')

def home(request):
    none_Bx = 0  # Bx 결과 안들어 간 사람
    Bx_call = 0  # Bx 결과 전화 통보 해 줘야 할 사람
    none_reading = 0  # 판독 안들어 간 사람
    will_phone = 0  # 전화해야할 사람

    today_g_egd, today_j_egd = 0, 0
    today_g_colon, today_j_colon = 0, 0
    today_sig = 0

    month_g_egd, month_j_egd, month_total_egd = 0, 0, 0  # 이번달 건진위내시경, 진료위내시경
    month_g_colon, month_j_colon, month_total_colon = 0, 0, 0  # 이번달 건진대장내시경, 진료대장내시경
    month_sig = 0  # 이번달 직장내시경

    first_colon = 0  # 1내과대장
    second_colon = 0  # 2내과대장
    first_polyp = 0  # 1내과용종
    second_polyp = 0  # 2내과 용종
    first_adenoma = 0  # 1내과 선종
    second_adenoma = 0  # 2내과 선종
    first_polyp_rate = 0
    second_polyp_rate = 0
    first_adenoma_rate = 0
    second_adenoma_rate = 0
    total_polyp_rate, total_adenoma_rate = 0, 0

    today = date.today()
    this_month = today.month
    this_year = today.year

    all_endoscopy = Endoscopy.objects.all()
    each_day_endoscopy_list = Endoscopy.objects.filter(date =today)
    today_patient = Patient.objects.filter(id__in =[endoscopy.patient_id for endoscopy in each_day_endoscopy_list])

    today_patient_list={}
    for exam in each_day_endoscopy_list:
        patient = Patient.objects.get(id=exam.patient_id)
        hospital_no = patient.hospital_no
        patient_age = age(patient.birth)
        birth_string = patient.birth.strftime('%y/%m/%d')
        type = ''

        if 'E' in exam.type and 'C' in exam.type:
            type = 'E,C'
        elif 'E' in exam.type and 'S' in exam.type:
            type = 'E,S'
        elif 'E' in exam.type:
            type = 'E'
        elif 'C' in exam.type:
            type = 'C'
        elif 'S' in exam.type:
            type = 'S'
        today_patient_list[patient.name] = {'hospital_no': hospital_no, 'age': patient_age, 'birthday': birth_string,
                                 'type': type, 'doc': exam.doc,
                                 'sex': patient.sex, 'id':exam.patient_id, 'Dx':exam.Dx, 'procedure':exam.procedure }
    context = {'today':today, 'today_patient_list':today_patient_list, 'none_Bx': 0, 'Bx_call': 0, 'none_reading': 0, 'will_phone': 0,
               'today_g_egd': today_g_egd, 'today_j_egd': today_j_egd,
               'today_g_colon': today_g_colon, 'today_j_colon': today_j_colon, 'today_sig': 0,
               'today_total_egd': 0, 'today_total_colon': 0,
               'month_g_egd': month_g_egd, 'month_j_egd': month_j_egd,
               'month_g_colon': month_g_colon, 'month_j_colon': month_j_colon, 'month_sig': 0,
               'month_total_egd': month_total_egd,
               'month_total_colon': month_total_colon,
               'first_colon': first_colon, 'second_colon': second_colon,
               'first_polyp_rate': first_polyp_rate, 'second_polyp_rate': second_polyp_rate,
               'first_adenoma_rate': first_adenoma_rate, 'second_adenoma_rate': second_adenoma_rate,
               'total_polyp_rate': total_polyp_rate, 'total_adenoma_rate': total_adenoma_rate}

    for endoscopy in all_endoscopy:
        if endoscopy.procedure in [['EMR'], ['Polypectomy'], ['Bx'], ['Bx', 'EMR'], ['Bx', 'Polypectomy'],
                                      ['EMR', 'Polypectomy'], ['Bx', 'EMR', 'Polypectomy']] \
                and (endoscopy.Bx_result == '.' or endoscopy.Bx_result==''):
            none_Bx += 1
    context['none_Bx'] = none_Bx

    for endoscopy in all_endoscopy:
        if endoscopy.procedure in [['EMR'], ['Polypectomy'], ['Bx'], ['Bx', 'EMR'], ['Bx', 'Polypectomy'],
                                      ['Polypectomy', 'EMR'], ['Bx', 'Polypectomy', 'EMR'], ['Bx', 'CLO'], ['CLO'],
                                      ['CLO', 'EMR'], ['CLO', 'Polypectomy', 'EMR']] and endoscopy.Bx_result_call == '.' \
                and endoscopy.Bx_result !='.' and  endoscopy.date >= date(2017, 2, 27):
            Bx_call += 1
    context['Bx_call'] = Bx_call

    for endoscopy in all_endoscopy:
        if endoscopy.Dx == '.': none_reading += 1
    context['none_reading'] = none_reading

    patient_id_to_call=[]
    for endoscopy in all_endoscopy:
        call_date = add_month(endoscopy.date, endoscopy.followup_period)
        if today.year == call_date.year and today.month == call_date.month:
            if endoscopy.date.year == today.year and endoscopy.date.month == today.month:
                continue;
            else:
                if endoscopy.re_visit_call == '.':
                    if endoscopy.patient_id not in patient_id_to_call:
                        will_phone += 1
                        patient_id_to_call.append(endoscopy.patient_id)
    context['will_phone'] = will_phone

    for endoscopy in all_endoscopy:
        if endoscopy.date == today:
            if 'E' in endoscopy.type:
                if endoscopy.source == '건진':
                    today_g_egd += 1
                elif endoscopy.source == "진료":
                    today_j_egd += 1
                elif endoscopy.source == "건진+진료":
                    today_g_egd += 1
            if 'C' in endoscopy.type:
                if endoscopy.source == "건진":
                    today_g_colon += 1
                elif endoscopy.source == "진료":
                    today_j_colon += 1
                elif endoscopy.source == "건진+진료":
                    today_j_colon += 1
            if 'S' in endoscopy.type: today_sig += 1
    context['today_g_egd'], context['today_j_egd'], context['today_g_colon'], context[
        'today_j_colon'] = today_g_egd, today_j_egd, today_g_colon, today_j_colon
    context['today_sig'] = today_sig
    context['today_total_egd'] = today_g_egd + today_j_egd
    context['today_total_colon'] = today_g_colon + today_j_colon

    for endoscopy in all_endoscopy:
        if endoscopy.date.year == this_year and endoscopy.date.month == this_month:
            if 'E' in endoscopy.type:
                if endoscopy.source == '건진':
                    month_g_egd += 1
                elif endoscopy.source == "진료":
                    month_j_egd += 1
                elif endoscopy.source == "건진+진료":
                    month_g_egd += 1

            if 'C' in endoscopy.type:
                if endoscopy.doc == "이영재":
                    first_colon += 1
                    if 'Polypectomy' in endoscopy.procedure or 'EMR' in endoscopy.procedure:
                        first_polyp += 1
                    if 'adenoma' in endoscopy.Bx_result:
                        first_adenoma += 1
                elif endoscopy.doc == "김신일":
                    second_colon += 1
                    if 'Polypectomy' in endoscopy.procedure or 'EMR' in endoscopy.procedure:
                        second_polyp += 1
                    if 'adenoma' in endoscopy.Bx_result:
                        second_adenoma += 1

                if endoscopy.source == "건진":
                    month_g_colon += 1
                elif endoscopy.source == "진료":
                    month_j_colon += 1
                elif endoscopy.source == "건진+진료":
                    month_j_colon += 1

            if 'S' in endoscopy.type: month_sig += 1

    context['month_g_egd'] = month_g_egd
    context['month_j_egd'] = month_j_egd
    context['month_total_egd'] = month_g_egd + month_j_egd
    context['month_g_colon'] = month_g_colon
    context['month_j_colon'] = month_j_colon
    context['month_total_colon'] = month_g_colon + month_j_colon
    context['month_sig'] = month_sig
    context['first_colon'] = first_colon
    context['second_colon'] = second_colon
    if first_colon != 0:
        context['first_polyp_rate'] = int(float(first_polyp) / first_colon * 100)
        context['first_adenoma_rate'] = int(float(first_adenoma) / first_colon * 100)
    else:
        context['first_polyp_rate'], context['first_adenoma_rate'] = '0', '0'
    if second_colon != 0:
        context['second_polyp_rate'] = int(float(second_polyp) / second_colon * 100)
        context['second_adenoma_rate'] = int(float(second_adenoma) / second_colon * 100)
    else:
        context['second_polyp_rate'], context['second_adenoma_rate'] = '0', '0'

    if context['month_total_colon'] != 0:
        context['total_polyp_rate'] = int(float(first_polyp + second_polyp) / context['month_total_colon'] * 100)
        context['total_adenoma_rate'] = int(float(first_adenoma + second_adenoma) / context['month_total_colon'] * 100)
    else:
        context['total_polyp_rate'], context['total_adenoma_rate'] = '0', '0'

    return render(request, 'home2.html', context)
