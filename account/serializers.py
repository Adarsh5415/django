from rest_framework import serializers
from account.models import User, CorrespondenceAddress, ResidentialAddress, EducationDetailsAppearing, EducationDetailsPassed
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from . import utils
from django.core.exceptions import ValidationError

from .models import OTP
import random




# class UserRegistrationSerializer(serializers.ModelSerializer):

#     password2 = serializers.CharField(style={'input_type':'password'},
#                                       write_only = True)
#     class Meta:
#         model=User
#         fields = ['email', 'name', 'password', 'password2', 'tc']
#         extra_kwargs = {
#             'password':{'write_only':True}
#         }

    
#     def validate(self, attrs):

#         password = attrs.get('password')
#         password2 = attrs.get('password2')

#         if password != password2:
#             raise serializers.ValidationError("Password and Confirm Password does not match")

#         return attrs
    
#     def create(self, validate_data):
#         return User.objects.create_user(**validate_data)



class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'guardianName', 'dob', 'aadhar', 'password', 'password2', 'tc']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password do not match")

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)

    

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255)
    class Meta:
        model = User
        fields = ['email', 'password']





class UserChangePasswordSerializer(serializers.Serializer):

    password = serializers.CharField(max_length=255, style=
                                     {'input_type':'password'},
                                     write_only=True)
    password2 = serializers.CharField(max_length=255, style=
                                     {'input_type':'password'},
                                     write_only=True)
    
    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):

        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')

        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password does not match")

        user.set_password(password)
        user.save()

        return attrs
    

class SendPasswordResetEmailSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=255)
    
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            
            user = User.objects.get(email = email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded UID', uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('Password Reset Token', token)
            link = 'http://localhost:4200/api/user/reset/' + uid + '/' + token
            print('Password Reset Link', link)
            # send email
            body = 'Click the following link to reset the password '+ link
            data = {
                'subject':"Reset Your Password",
                'body': body,
                'to_email':user.email
            }
            utils.Util.send_email(data)
            return attrs
        else:
            raise ValidationError("You are not a Registered User")
        


class UserPasswordResetSerializer(serializers.Serializer):

    password = serializers.CharField(max_length=255, style=
                                     {'input_type':'password'},
                                     write_only=True)
    password2 = serializers.CharField(max_length=255, style=
                                     {'input_type':'password'},
                                     write_only=True)
    
    
    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):

        try:

            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password does not match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError("Token is  Invalid or Expired")
            

            user.set_password(password)
            user.save()

            return attrs
        
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise ValidationError("Token is  Invalid or Expired")
        




class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create_otp(self):
        otp = random.randint(100000, 999999)
        return str(otp)

    def save(self):
        email = self.validated_data['email']
        otp = self.create_otp()

        # Save or update OTP
        otp_entry, created = OTP.objects.update_or_create(
            email=email,
            defaults={'otp': otp, 'is_verified': False}
        )
        return otp_entry


# class OTPVerificationSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     otp = serializers.CharField(max_length=6)

#     def validate(self, data):
#         try:
#             otp_entry = OTP.objects.get(email=data['email'])
#         except OTP.DoesNotExist:
#             raise serializers.ValidationError("Email not found.")

#         if otp_entry.otp != data['otp']:
#             raise serializers.ValidationError("Invalid OTP.")

#         if otp_entry.is_verified:
#             raise serializers.ValidationError("Email already verified.")

#         return data

#     def save(self):
#         otp_entry = OTP.objects.get(email=self.validated_data['email'])
#         otp_entry.is_verified = True
#         otp_entry.save()


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            otp_entry = OTP.objects.get(email=data['email'])
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Email not found.")

        if otp_entry.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP.")

        if otp_entry.is_verified:
            raise serializers.ValidationError("Email already verified.")

        if otp_entry.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        return data

    def save(self):
        otp_entry = OTP.objects.get(email=self.validated_data['email'])
        otp_entry.is_verified = True
        otp_entry.save()





class CorrespondenceAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrespondenceAddress
        fields = ['countrySelected', 'streetAddress', 'localityOrVillage', 'selectedState', 'citySelected', 'pincode', 'residentialAddressSame']

    def create(self, validated_data):
        # Automatically assign the user from the request context
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # This ensures the user is always set correctly (though it's not strictly necessary for updates)
        validated_data['user'] = self.context['request'].user
        return super().update(instance, validated_data)
    



class ResidentialAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentialAddress
        fields = ['countrySelected', 'streetAddress', 'localityOrVillage', 'selectedState', 'citySelected', 'pincode']

    def create(self, validated_data):
        # Automatically assign the user from the request context
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # This ensures the user is always set correctly (though it's not strictly necessary for updates)
        validated_data['user'] = self.context['request'].user
        return super().update(instance, validated_data)
    




class EducationDetailsAppearingSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDetailsAppearing
        fields = ['standard', 'board', 'school', 'registration_no', 'subjects']

    def validate_board(self, value):
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Board must contain at least one alphabet.")
        return value

    def validate_school(self, value):
        if any(not char.isalnum() and char != ' ' for char in value):
            raise serializers.ValidationError("School name must not contain special characters.")
        return value

    def validate_subjects(self, value):
        if any(not char.isalnum() and char not in [',', ' '] for char in value):
            raise serializers.ValidationError("Subjects must not contain special characters except ',' and spaces.")
        return value
    




class EducationDetailsPassedSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationDetailsPassed
        fields = ['standard', 'board', 'school', 'roll_no', 'marks_obtained', 'subjects']

    def validate_board(self, value):
        if any(not char.isalnum() and char != ' ' for char in value):
            raise serializers.ValidationError("Board must not contain special characters.")
        return value

    def validate_school(self, value):
        if any(not char.isalnum() and char != ' ' for char in value):
            raise serializers.ValidationError("School name must not contain special characters.")
        return value

    def validate_subjects(self, value):
        if any(not char.isalnum() and char not in [',', ' '] for char in value):
            raise serializers.ValidationError("Subjects must not contain special characters except ',' and spaces.")
        return value
    





class UserProfileSerializer(serializers.ModelSerializer):
    # Including all fields related to the User
    correspondence_address = CorrespondenceAddressSerializer(read_only=True)
    residential_address = ResidentialAddressSerializer(read_only=True)
    education_details_appearing = EducationDetailsAppearingSerializer(read_only=True)
    education_details_passed = EducationDetailsPassedSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'guardianName', 'dob', 'aadhar', 
            'correspondence_address', 'residential_address', 
            'education_details_appearing', 'education_details_passed'
        ]
        # You can also add any other related models if needed




    

    

    
