from django.db import models
from multiselectfield import MultiSelectField
from datetime import date
from django import forms

# class Exam(models.Model):
#
#     exam_date=models.DateField('검사 날짜', default=date.today,)
#     exam_type=MultiSelectField('내시경 종류', max_length=20, max_choices=3,choices=(('E', 'EGD'),('C','Colonoscopy'), ('S','Sigmoidoscopy')))
#     exam_doc=models.CharField('의사', max_length=30, choices=(('이영재','이영재'),('김신일','김신일')), default='김신일')
#     exam_class=models.CharField('건진/진료',max_length=30, choices=(('건진',"건진"),('진료',"진료"),('건진+진료',"건진+진료")), default='건진')
#     exam_place=models.CharField('외래/입원', max_length=20, choices=(('입원', '입원'), ('외래', '외래')), default='외래')
#     patient_name=models.CharField('환자 이름', max_length=50)
#     hospital_no=models.CharField('환자등록 번호', max_length=10)
#     patient_sex=models.CharField('성별',max_length=10, choices=(('M',"남자"),('F', "여자")), default='M')
#     patient_birth=models.DateField('생일', auto_now=False)
#     patient_phone=models.CharField("전화번호", max_length=15, default="010-")
#     exam_Dx=models.CharField("내시경 진단명",max_length=200)
#     exam_procedure=MultiSelectField("시술", max_length=20, max_choices=5, choices=(('None','None'),('Bx',"Bx"),('CLO','CLO'),('Polypectomy', "Polypectomy"),("EMR",'EMR'),
#                                                            ('ForeignBody','Foreign Body Remove'),('BleedingControl','Bleeding Control'),('PEG','PEG')))
#     Bx_result=models.CharField("조직검사 결과", max_length=200, default=".")
#     Bx_result_call=models.CharField("조직검사 결과 알려주었나요?", max_length=100, default=".")
#     follow_up=models.IntegerField("추적검사 기간", default=0)
#     phone_check=models.CharField("전화 통화 결과", max_length=50, default='.')
#     re_visit=models.BooleanField("재방문", default=False)
#
#     class Meta:
#         ordering=['-exam_date']
#
#     def save(self, *args, **kwargs):
#         super(Exam, self).save(*args, **kwargs)

class Patient(models.Model):
    name = models.CharField('환자 이름', max_length=15)
    hospital_no = models.CharField('환자등록 번호', max_length=10)
    sex = models.CharField('성별', max_length=10, choices=(('M', "남자"), ('F', "여자")), default='M')
    birth = models.DateField('생일', auto_now=False)
    phone = models.CharField("전화번호", max_length=15, default="010-")
    address = models.CharField("주소", max_length=30, blank=True)

    class Meta:
        ordering=['name']

    def save(self, *args, **kwargs):
        super(Patient, self).save(*args, **kwargs)

class Endoscopy(models.Model):
    patient = models.ForeignKey(Patient, null=True)
    date = models.DateField('검사 날짜', default=date.today, )
    type = MultiSelectField('내시경 종류', max_length=20, max_choices=3,
                                 choices=(('E', 'EGD'), ('C', 'Colonoscopy'), ('S', 'Sigmoidoscopy')))
    doc = models.CharField('의사', max_length=10, choices=(('이영재', '이영재'), ('김신일', '김신일')), default='김신일')
    source = models.CharField('건진/진료', max_length=10, choices=(('건진', "건진"), ('진료', "진료"), ('건진+진료', "건진+진료")),
                                  default='건진')
    place = models.CharField('외래/입원', max_length=10, choices=(('입원', '입원'), ('외래', '외래')), default='외래')
    sleep = models.CharField('수면/일반', max_length=6, choices=(('수면','수면'), ('일반','일반')), default='수면')
    Dx = models.CharField("내시경 진단명", max_length=200)
    procedure = MultiSelectField("시술", max_length=20, max_choices=5, choices=(
    ('None', 'None'), ('Bx', "Bx"), ('CLO', 'CLO'), ('Polypectomy', "Polypectomy"), ("EMR", 'EMR'),
    ('ForeignBody', 'Foreign Body Remove'), ('BleedingControl', 'Bleeding Control'), ('PEG', 'PEG')))
    Bx_result = models.CharField("조직검사 결과", max_length=200, default="", blank=True)
    Bx_result_call = models.CharField("조직검사 전화 통보 내용", max_length=50, default="", blank=True)
    followup_period = models.IntegerField("추적검사 기간", default=24)
    re_visit_call = models.CharField("재방문 전화 통화 내용", max_length=50, default="", blank=True)
    re_visit = models.BooleanField("재방문", default=False)
    re_visit_date=models.DateField("재방문 날짜", default="1900-01-01", blank=True)

    class Meta:
        ordering=['date']

    def save(self, *args, **kwargs):
        super(Endoscopy, self).save(*args, **kwargs)
