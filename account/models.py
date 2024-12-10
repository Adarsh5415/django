from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import uuid

from django.utils import timezone
from datetime import timedelta

def add(a,b):
    return a+b


# class UserManager(BaseUserManager):
#     def create_user(self, email, name, tc, password=None, password2=None):
#         """
#         Creates and saves a User with the given email, tc and password.
#         """
#         if not email:
#             raise ValueError("Users must have an email address")

#         user = self.model(
#             email=self.normalize_email(email),
#             name=name,
#             tc = tc
#         )

#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email,  name, tc, password=None):
#         """
#         Creates and saves a superuser with the given email, name, tc and password.
#         """
#         user = self.create_user(
#             email,
#             password=password,
#             name = name,
#             tc = tc
#         )
#         user.is_admin = True
#         user.save(using=self._db)
#         return user


# class User(AbstractBaseUser):
#     email = models.EmailField(
#         verbose_name="email",
#         max_length=255,
#         unique=True,
#     )
#     name = models.CharField(max_length=200)
#     tc = models.BooleanField()
#     is_active = models.BooleanField(default=True)
#     is_admin = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add = True)
#     updated_at = models.DateTimeField(auto_now = True)

#     objects = UserManager()

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["name","tc"]

#     def __str__(self):
#         return self.email

#     def has_perm(self, perm, obj=None):
#         "Does the user have a specific permission?"
#         # Simplest possible answer: Yes, always
#         return self.is_admin

#     def has_module_perms(self, app_label):
#         "Does the user have permissions to view the app `app_label`?"
#         # Simplest possible answer: Yes, always
#         return True

#     @property
#     def is_staff(self):
#         "Is the user a member of staff?"
#         # Simplest possible answer: All admins are staff
#         return self.is_admin





from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, name, guardianName, dob, aadhar, tc, password=None):
        """
        Creates and saves a User with the given email, guardian name, date of birth, Aadhaar, tc, and password.
        """
        if not email:
            raise ValueError("Users must have an email address")
        
        user = self.model(
            email=self.normalize_email(email),
            name=name,
            guardianName=guardianName,
            dob=dob,
            aadhar=aadhar,
            tc=tc,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, guardianName, dob, aadhar, tc, password=None):
        """
        Creates and saves a superuser with the given email, guardian name, date of birth, Aadhaar, tc, and password.
        """
        user = self.create_user(
            email,
            name=name,
            guardianName=guardianName,
            dob=dob,
            aadhar=aadhar,
            tc=tc,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200)
    guardianName = models.CharField(max_length=200)
    dob = models.DateField()
    aadhar = models.CharField(max_length=12, unique=True)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "guardianName", "dob", "aadhar", "tc"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin
    
    @property
    def correspondence_address(self):
        return getattr(self, 'correspondence_address', None)

    


# class OTP(models.Model):
#     email = models.EmailField(unique=True)
#     otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_verified = models.BooleanField(default=False)

#     def __str__(self):
#         return self.email


class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    expiry_time = models.DateTimeField()  # Add expiry time for OTP

    def save(self, *args, **kwargs):
        # Set the expiry time when the OTP is generated (e.g., 5 minutes after creation)
        if not self.expiry_time:
            self.expiry_time = timezone.now() + timedelta(minutes=0.5)  # Set OTP expiry to 5 minutes
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if the OTP has expired"""
        return timezone.now() > self.expiry_time

    def __str__(self):
        return self.email



class CorrespondenceAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="correspondence_address")
    countrySelected = models.CharField(max_length=100)
    streetAddress = models.CharField(max_length=255)
    localityOrVillage = models.CharField(max_length=255)
    selectedState = models.CharField(max_length=100)
    citySelected = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    residentialAddressSame = models.BooleanField(default=True)

    def __str__(self):
        return f"Correspondence Address for {self.user.email}"

    class Meta:
        verbose_name = "Correspondence Address"
        verbose_name_plural = "Correspondence Addresses"



class ResidentialAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="residential_address")
    countrySelected = models.CharField(max_length=100)
    streetAddress = models.CharField(max_length=255)
    localityOrVillage = models.CharField(max_length=255)
    selectedState = models.CharField(max_length=100)
    citySelected = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)

    def __str__(self):
        return f"Residential Address for {self.user.email}"

    class Meta:
        verbose_name = "Residential Address"
        verbose_name_plural = "Residential Addresses"








class EducationDetailsAppearing(models.Model):
    STANDARD_CHOICES = [
        ("10th Appearing", "10th Appearing"),
        ("12th Appearing", "12th Appearing"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="education_details_appearing")
    standard = models.CharField(max_length=20, choices=STANDARD_CHOICES)
    board = models.CharField(max_length=255)
    school = models.CharField(max_length=255)
    registration_no = models.CharField(max_length=50)
    subjects = models.TextField()

    def __str__(self):
        return f"Education Details for {self.user.name} ({self.standard})"

    class Meta:
        verbose_name = "Education Details Appearing"
        verbose_name_plural = "Education Details Appearing"




class EducationDetailsPassed(models.Model):
    STANDARD_CHOICES = [
        ("12th Passed", "12th Passed"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="education_details_passed")
    standard = models.CharField(max_length=20, choices=STANDARD_CHOICES)
    board = models.CharField(max_length=255)
    school = models.CharField(max_length=255)
    roll_no = models.CharField(max_length=50)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    subjects = models.TextField()

    def __str__(self):
        return f"{self.standard} Details for {self.user.name}"

    class Meta:
        verbose_name = "Education Details Passed"
        verbose_name_plural = "Education Details Passed"

