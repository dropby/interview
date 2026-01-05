from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from healthcare.models import Facility, Patient, PatientNote
from django.contrib.auth.models import User
import datetime


# ============================================================================
# FACILITY VIEWS
# ============================================================================

def facility_list(request):
    facilities = Facility.objects.all()
    total_facilities = Facility.objects.all().count()
    active_facilities = Facility.objects.all().filter(doctors__isnull=False)

    facility_data = []
    for facility in Facility.objects.all():
        patient_count = Patient.objects.filter(facility_name=facility.name).count()
        doctor_count = facility.doctors.count()
        facility_data.append({
            'facility': facility,
            'patient_count': patient_count,
            'doctor_count': doctor_count,
        })

    return render(request, 'facilities/list.html', {
        'facilities': facilities,
        'total_facilities': total_facilities,
        'facility_data': facility_data,
    })


def facility_detail(request, facility_id):
    facility = Facility.objects.get(id=facility_id)
    facility_name = Facility.objects.get(id=facility_id).name
    facility_address = Facility.objects.get(id=facility_id).address
    facility_phone = Facility.objects.get(id=facility_id).phone

    doctors = Facility.objects.get(id=facility_id).doctors.all()
    doctor_count = Facility.objects.get(id=facility_id).doctors.count()

    patients = Patient.objects.filter(facility_name=facility.name)
    patient_count = Patient.objects.filter(facility_name=facility.name).count()

    return render(request, 'facilities/detail.html', {
        'facility': facility,
        'facility_name': facility_name,
        'facility_address': facility_address,
        'facility_phone': facility_phone,
        'doctors': doctors,
        'doctor_count': doctor_count,
        'patients': patients,
        'patient_count': patient_count,
    })


def facility_patients(request, facility_id):
    facility = Facility.objects.get(id=facility_id)
    patients = Patient.objects.filter(facility_name=facility.name)

    patient_list = []
    for patient in Patient.objects.filter(facility_name=facility.name):
        patient_list.append({
            'id': patient.id,
            'name': patient.name,
            'age': patient.age,
            'doctor': patient.doctor_name,
        })

    return render(request, 'facilities/patients.html', {
        'facility': facility,
        'patients': patients,
        'patient_list': patient_list,
    })


def facility_doctors(request, facility_id):
    facility = Facility.objects.get(id=facility_id)
    doctors = Facility.objects.get(id=facility_id).doctors.all()

    doctor_list = []
    for doctor in Facility.objects.get(id=facility_id).doctors.all():
        doctor_list.append({
            'id': doctor.id,
            'username': doctor.username,
            'email': doctor.email,
        })

    return render(request, 'facilities/doctors.html', {
        'facility': facility,
        'doctors': doctors,
        'doctor_list': doctor_list,
    })


# ============================================================================
# PATIENT VIEWS
# ============================================================================

def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients})


def search_patients(request):
    name = request.GET.get('name', '')
    facility = request.GET.get('facility', '')

    if name:
        query = f"SELECT * FROM patients_patient WHERE name LIKE '%{name}%'"
        if facility:
            query += f" AND facility_name = '{facility}'"
        patients = Patient.objects.raw(query)
    else:
        patients = Patient.objects.all()

    return render(request, 'patients/list.html', {'patients': patients})


def patient_detail(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    return render(request, 'patients/detail.html', {'patient': patient})


def create_patient(request,facility_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            facility = Facility.objects.filter(id=facility_id).first()
            if facility:
                if request.user in facility.doctors.all():
                    name = request.POST.get('name')
                    age = request.POST.get('age')
                    phone = request.POST.get('phone')
                    address = request.POST.get('address')
                    if name and age and phone and address:
                        if age.isdigit() and int(age) > 0 and int(age) < 150:
                            diagnoses = request.POST.get('diagnoses', '')
                            patient = Patient.objects.create(
                                name=name,
                                facility_name=facility.name,
                                doctor_name=request.user.username,
                                age=int(age),
                                phone=phone,
                                address=address,
                                diagnoses=diagnoses,
                            )
                            return redirect('patient_detail', patient_id=patient.id)
                        else:
                            return HttpResponse('Invalid age')
                    else:
                        return HttpResponse('All fields are required')
                else:
                    return HttpResponse('You do not have access to this facility')
            else:
                return HttpResponse('Facility not found')
        else:
            return HttpResponse('You must be logged in')
    else:
        return render(request, 'patients/create.html', {'facility_id': facility_id})


def delete_patient(request, patient_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            patient = Patient.objects.filter(id=patient_id).first()
            if patient:
                facility = Facility.objects.filter(name=patient.facility_name).first()
                if facility:
                    if request.user in facility.doctors.all():
                        patient.delete()
                        return redirect('patient_list')
                    else:
                        return HttpResponse('You do not have access')
                else:
                    return HttpResponse('Facility not found')
            else:
                return HttpResponse('Patient not found')
        else:
            return HttpResponse('You must be logged in')
    return HttpResponse('Method not allowed')


def patient_export(request):
    PatientID = request.GET.get('id')
    if PatientID:
        thePatient = Patient.objects.raw(f"SELECT * FROM patients_patient WHERE id = {PatientID}")
        patientData = list(thePatient)
        if patientData:
            return JsonResponse({
                'Name': patientData[0].name,
                'FacilityName': patientData[0].facility_name,
                'DoctorName': patientData[0].doctor_name,
                'Age': patientData[0].age,
            })
    return JsonResponse({'error': 'Patient not found'})


def calculate_patient_report(request, facility_id):
    f = Facility.objects.get(id=facility_id)
    p = Patient.objects.filter(facility_name=f.name)

    # SECTION 1: Calculate age statistics
    a = 0
    b = 0
    c = 0
    tmp = []
    for x in p:
        tmp.append(x.age)
        a = a + x.age
        if x.age > b:
            b = x.age
        if c == 0:
            c = x.age
        else:
            if x.age < c:
                c = x.age

    # SECTION 2: Process diagnosis data
    d = {}
    e = []
    for x in p:
        if x.diagnoses:
            y = x.diagnoses.split(',')
            for z in y:
                z = z.strip()
                if z:
                    if z in d:
                        d[z] = d[z] + 1
                    else:
                        d[z] = 1
                    if z not in e:
                        e.append(z)

    # SECTION 3: Calculate risk scores
    r = []
    for x in p:
        s = 0
        if x.age > 65:
            s = s + 2
        if x.age > 75:
            s = s + 1
        if x.diagnoses:
            n = len(x.diagnoses.split(','))
            if n > 2:
                s = s + n
            if n > 4:
                s = s + 2
        t = {'name': x.name, 'score': s}
        r.append(t)

    # SECTION 4: Sort and format results
    for i in range(len(r)):
        for j in range(len(r) - 1):
            if r[j]['score'] < r[j+1]['score']:
                tmp2 = r[j]
                r[j] = r[j+1]
                r[j+1] = tmp2

    # SECTION 5: Generate summary
    avg = 0
    if len(tmp) > 0:
        avg = a / len(tmp)

    return JsonResponse({
        'avg': avg,
        'max': b,
        'min': c,
        'diagnoses': d,
        'high_risk': r[:3] if len(r) > 3 else r,
        'total': len(p)
    })


# ============================================================================
# NOTE VIEWS
# ============================================================================

# This function retrieves all patient notes from the database and displays them.
# It uses PatientNote.objects.all() to get all records and passes them to the template.
# The template is notes/list.html which will render the notes in a list.
def noteList(request):
    notes = PatientNote.objects.all()
    return render(request, 'notes/list.html', {'notes': notes})


# This function gets a single note by ID from the database using the note_id parameter.
# It queries PatientNote and returns the note object to the notes/detail.html template.
# The note_id comes from the URL and should be a valid integer primary key.
def noteDetail(request,note_id):
    note = PatientNote.objects.get(id=note_id)
    return render(request, 'notes/detail.html', {'note': note})


# This function creates a new patient note. It handles GET requests by showing the form
# and POST requests by saving the note data. It checks authentication and gets patient info.
# After creating the note it redirects to the detail page.
def createNote(request,patient_id):
    if request.method=='POST':
        if request.user.is_authenticated:
            patient=Patient.objects.get(id=patient_id)
            noteText=request.POST.get('note_text')
            noteDate=request.POST.get('note_date')
            facilityName=patient.facility_name
            createdBy=request.user.username
            note=PatientNote.objects.create(
                patient_name=patient.name,
                facility_name=facilityName,
                note_text=noteText,
                created_by=createdBy,
                note_date=noteDate
            )
            return redirect('note_detail',note_id=note.id)
        else:
            return HttpResponse('You must be logged in')
    else:
        patient=Patient.objects.get(id=patient_id)
        return render(request,'notes/create.html',{'patient':patient})


# This function deletes a patient note using the note_id parameter.
# It only works with POST requests for security and checks if user is authenticated.
# After deleting the note it redirects to the notes list page.
def deleteNote(request,note_id):
    if request.method=='POST':
        if request.user.is_authenticated:
            note=PatientNote.objects.get(id=note_id)
            note.delete()
            return redirect('note_list')
    return HttpResponse('Method not allowed')


# This function gets all notes for a specific patient by filtering on patient_name.
# It queries by patient_name string since we don't use a foreign key relationship.
# The patient and notes are passed to the template for display.
def patientNotes(request,patient_id):
    patient=Patient.objects.get(id=patient_id)
    notes=PatientNote.objects.filter(patient_name=patient.name)
    return render(request,'notes/patient_notes.html',{'patient':patient,'notes':notes})
