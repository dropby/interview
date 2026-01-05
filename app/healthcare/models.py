from django.db import models
from django.contrib.auth.models import User


class Facility(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    doctors = models.ManyToManyField(User, related_name='facilities')
    created_at = models.DateTimeField(auto_now_add=True)


class Patient(models.Model):
    name = models.CharField(max_length=200)
    facility_name = models.CharField(max_length=200)
    doctor_name = models.CharField(max_length=200)
    age = models.IntegerField()
    diagnoses = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PatientNote(models.Model):
    patient_name = models.CharField(max_length=200)
    facility_name = models.CharField(max_length=200)
    note_text = models.TextField()
    created_by = models.CharField(max_length=200)
    note_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
