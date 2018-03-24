"""procedure URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from procedure import views

urlpatterns = [
    url(r'^add_endoscopy/$', views.add_endoscopy, name='add_endoscopy'),
    url(r'^add_patient_initial/$', views.AddingPatient.as_view(), name='add_patient_initial'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^bx_input_for_ajax/$', views.bx_input_for_ajax, name='bx_input_for_ajax'),
    url(r'^bx_noti_for_ajax/$', views.bx_noti_for_ajax, name='bx_noti_for_ajax'),
    url(r'^reading_input_for_ajax/$', views.reading_input_for_ajax, name='reading_input_for_ajax'),
    url(r'^phone/$', views.phone, name="phone"),
    url(r'^thisyearsummary/$', views.thisyear, name="thisyearsummary"),
    url(r'^homethisyear/$', views.homegraph, name="homethisyear"),
    url(r'^thismonth_for_ajax/$', views.thismonth_for_ajax, name="thismonth_for_ajax"),
    url(r'^each_day_patient_list_for_ajax/$', views.each_day_patient_list_for_ajax, name="each_day_patient_list_for_ajax"),
    url(r'^noti_summary/$', views.noti_summary, name="noti_summary"),
    url(r'^each_day_mouse_on_for_ajax/$', views.each_day_mouse_on_for_ajax, name="each_day_mouse_on_for_ajax"),
    url(r'^each_day_patient_info/(?P<pk>[0-9]+)/$', views.each_day_patient_info, name="each_day_patient_info"),
    url(r'^each_day_patient_info/$', views.each_day_patient_info, name="each_day_patient_info"),
    url(r'^re_visit_patient_info/(?P<pk>[0-9]+)/$', views.re_visit_patient_info, name="re_visit_patient_info"),
    url(r'^endo_delete/(?P<pk>[0-9]+)/$', views.EndoDeleteView.as_view(), name="endo_delete"),
    url(r'^re_visit_patient_info/$', views.re_visit_patient_info, name="re_visit_patient_info"),
    url(r'^(?P<pk>[0-9]+)/patient_info_update/$', views.PatientInfoUpdateview.as_view(), name="patient_info_update"),
    url(r'^(?P<pk>[0-9]+)/endoscopy_info_update/$', views.EndoscopyInfoUpdateview.as_view(), name="endoscopy_info_update"),
    url(r'^(?P<pk>[0-9]+)/endoscopy_info_update_for_revisit/$', views.EndoscopyInfoUpdateForRevisitview.as_view(), name="endoscopy_info_update_for_revisit"),
]
