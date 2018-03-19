from django import forms
from django.forms import inlineformset_factory, CheckboxSelectMultiple, RadioSelect

from procedure.models import Patient, Endoscopy

from django.forms import widgets


from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})

MONTHS = {
    1:'1', 2:'2', 3:'3', 4:'4',
    5:'5', 6:'6', 7:'7', 8:'8',
    9:'9', 10:'10', 11:'11', 12:'12'
}

class PatientModelForm(forms.ModelForm):
    class Meta:
        model=Patient
        fields = '__all__'
        #이전 모델에서 사용하던 위젯, 앞으로 필요없어질 것으로 보이는 코드이다.
        #widgets={'exam_type':forms.CheckboxSelectMultiple}
        #widgets={'exam_procedure':forms.CheckboxSelectMultiple}

class AddingPatientInitalForm(forms.Form):
    search_id = forms.CharField(label="등록번호", required=True)

class EndoscopyModelForm(forms.ModelForm):
    class Meta:
        model = Endoscopy
        fields = ('date', 'type','doc','source', 'place', 'sleep', 'Dx','procedure','followup_period','followup_date')
        #widgets = forms.SelectMultiple(attrs={'display':'inline-block'})


class ProcedureSearchForm(forms.Form):
    name=forms.CharField(label="이름", required=False)
    hospital_no = forms.CharField(label = "등록번호", required=False)
    type = forms.ChoiceField(label="검사종류", widget=RadioSelect(attrs = {"checked":"C"}),
                                     choices=[['E','위내시경'], ['C','대장내시경'],['S','직장내시경'], ["EC",'위/대장내시경'],
                                              [['E','S'], '위/직장내시경'],["all",'모든검사']], required=False )
    Dx = forms.CharField(label ="내시경 진단", required=False)
    procedure = forms.MultipleChoiceField(label="시술", widget=CheckboxSelectMultiple,
                                          choices=[['None', 'None'],['Bx','Bx'],['CLO', 'CLO'],['Polypectomy','Polypectomy'],['EMR','EMR'],
                                                   ['ForeignBody','Foreign body remove'],['BleedingControl','Bleeding Control'],
                                                   ['PEG','PEG']], required=False)
    Bx_result = forms.CharField(label="조직검사 결과", required=False)
    first_date = forms.DateField(label="FROM",  required=False, widget=DateInput())
    last_date = forms.DateField(label="TO", required=False, widget=DateInput())
