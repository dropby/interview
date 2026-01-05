from django.urls import path
from healthcare import views

urlpatterns = [
    # Facilities
    path('facilities/', views.facility_list, name='facility_list'),
    path('facilities/<int:facility_id>/', views.facility_detail, name='facility_detail'),
    path('facilities/<int:facility_id>/patients/', views.facility_patients, name='facility_patients'),
    path('facilities/<int:facility_id>/doctors/', views.facility_doctors, name='facility_doctors'),

    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/search/', views.search_patients, name='search_patients'),
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/create/<int:facility_id>/', views.create_patient, name='create_patient'),
    path('patients/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),
    path('patients/export/', views.patient_export, name='patient_export'),
    path('patients/report/<int:facility_id>/', views.calculate_patient_report, name='patient_report'),

    # Notes
    path('notes/', views.noteList, name='note_list'),
    path('notes/<int:note_id>/', views.noteDetail, name='note_detail'),
    path('notes/create/<int:patient_id>/', views.createNote, name='create_note'),
    path('notes/<int:note_id>/delete/', views.deleteNote, name='delete_note'),
    path('notes/patient/<int:patient_id>/', views.patientNotes, name='patient_notes'),
]
