from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from account.serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, UserChangePasswordSerializer, SendPasswordResetEmailSerializer, UserPasswordResetSerializer,EmailSerializer, OTPVerificationSerializer, CorrespondenceAddressSerializer, ResidentialAddressSerializer, EducationDetailsAppearingSerializer, EducationDetailsPassedSerializer
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from account.models import OTP
from account.models import CorrespondenceAddress, ResidentialAddress, EducationDetailsAppearing, EducationDetailsPassed


from django.http import HttpResponse

def hello_world(request):
    return HttpResponse("Hello, World!")




def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):

    renderer_classes = [UserRenderer]

    def post(self, request, format=None):

        serializer = UserRegistrationSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):

            email = serializer.validated_data.get('email')

            # Check if the email is verified

            try:
                otp_entry = OTP.objects.get(email=email)
                if not otp_entry.is_verified:
                    return Response(
                        {"error": "Email not verified. Please verify your email before registering."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except OTP.DoesNotExist:
                return Response(
                    {"error": "No OTP verification record found for this email. Please verify your email."},
                    status=status.HTTP_400_BAD_REQUEST
                )
           
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({
                            'token':token, 
                            'msg':'Registration Successful'},
                            status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, 
                        status=status.HTTP_400_BAD_REQUEST)
    


class UserLoginView(APIView):

    renderer_classes = [UserRenderer]

    def post(self, request, format=None):

        serializer = UserLoginSerializer(data = request.data)

        if serializer.is_valid(raise_exception=True):

            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email = email, password = password)

            if user is not None:
                token = get_tokens_for_user(user)
                return Response({
                    'token':token,
                    'msg':'Login Successful'},
                    status=status.HTTP_200_OK)
            
            else:
                return Response({'errors':{'non_field_errors':
                                           ['Email or Password is not valid']}},
                                    status=status.HTTP_404_NOT_FOUND)
            


class UserProfileView(APIView):

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        # if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)


# class UserProfileView(APIView):
#     renderer_classes = [UserRenderer]
#     permission_classes = [IsAuthenticated]

#     def get(self, request, format=None):
#         serializer = UserProfileSerializer(request.user)
#         return Response(serializer.data, status=status.HTTP_200_OK)

    

class UserChangePasswordView(APIView):

    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        serializer = UserChangePasswordSerializer(data=request.data,
                                                  context={'user':request.user})
        
        if serializer.is_valid(raise_exception=True):
            
            return Response({
                    'msg':'Password Change Successful'},
                    status=status.HTTP_200_OK)
        
        return Response(serializer.errors, 
                        status=status.HTTP_400_BAD_REQUEST)
    

class SendPasswordResetEmailView(APIView):

    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            
            return Response({
                    'msg':'Password Reset Link Sent. Please check your email'},
                    status=status.HTTP_200_OK)
        
        return Response(serializer.errors, 
                        status=status.HTTP_400_BAD_REQUEST)
    

class UserPasswordResetView(APIView):

    renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format=None):

        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Reset Successful'},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class SendOTPView(APIView):

    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            otp_entry = serializer.save()
            # Send OTP via email
            send_mail(
                'National Scholarship Exam Registration',
                f'Your OTP is: {otp_entry.otp}',
                settings.DEFAULT_FROM_EMAIL,
                [otp_entry.email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class VerifyOTPView(APIView):

#     renderer_classes = [UserRenderer]

#     def post(self, request):
#         serializer = OTPVerificationSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyOTPView(APIView):

    renderer_classes = [UserRenderer]

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





# class CorrespondenceAddressView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """
#         Fetch the correspondence address for the authenticated user.
#         """
#         try:
#             address = request.user.correspondence_address
#             serializer = CorrespondenceAddressSerializer(address)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except CorrespondenceAddress.DoesNotExist:
#             return Response({'message': 'Correspondence address not found.'}, status=status.HTTP_404_NOT_FOUND)

#     def post(self, request):
#         """
#         Create a correspondence address for the authenticated user.
#         """
#         # We don't need to explicitly pass the user ID, it's automatically fetched from the request
#         serializer = CorrespondenceAddressSerializer(data=request.data, context={'request': request})

#         if serializer.is_valid():
#             serializer.save()  # The serializer's create method will automatically associate the user
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def put(self, request):
#         """
#         Update the correspondence address for the authenticated user.
#         """
#         try:
#             address = request.user.correspondence_address
#         except CorrespondenceAddress.DoesNotExist:
#             return Response({'message': 'Correspondence address not found.'}, status=status.HTTP_404_NOT_FOUND)

#         # Use partial=True to allow updating only some fields
#         serializer = CorrespondenceAddressSerializer(address, data=request.data, partial=True, context={'request': request})

#         if serializer.is_valid():
#             serializer.save()  # Automatically associates the user
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class CorrespondenceAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetch the correspondence address for the authenticated user.
        """
        try:
            address = request.user.correspondence_address
            serializer = CorrespondenceAddressSerializer(address)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CorrespondenceAddress.DoesNotExist:
            return Response({'message': 'Correspondence address not found.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a correspondence address for the authenticated user.
        """
        # We don't need to explicitly pass the user ID, it's automatically fetched from the request
        serializer = CorrespondenceAddressSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()  # The serializer's create method will automatically associate the user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update the correspondence address for the authenticated user.
        """
        try:
            address = request.user.correspondence_address
        except CorrespondenceAddress.DoesNotExist:
            return Response({'message': 'Correspondence address not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Use partial=True to allow updating only some fields
        serializer = CorrespondenceAddressSerializer(address, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()  # Automatically associates the user
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class ResidentialAddressView(APIView):
    permission_classes = [IsAuthenticated]



    def get(self, request):
        """
        Fetch the residential address for the authenticated user
        """
        try:
            address = request.user.residential_address
            serializer = ResidentialAddressSerializer(address)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ResidentialAddress.DoesNotExist:
            return Response({'message': 'Residential address not found.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a residential address for the authenticated user
        Only if the correspondence address has residentialSame set to True

        """
        try:
            correspondence_address = request.user.correspondence_address
            if correspondence_address.residentialAddressSame:
                return Response({'message': 'Cannot create residential address as residential address is same as the correspondence address.'},
                                status=status.HTTP_400_BAD_REQUEST)
        except CorrespondenceAddress.DoesNotExist:
            return Response({'message': 'Correspondence address not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ResidentialAddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate the address with the authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update the residential address for the authenticated user
        """
        try:
            address = request.user.residential_address
        except ResidentialAddress.DoesNotExist:
            return Response({'message': 'Residential address not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ResidentialAddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class EducationDetailsAppearingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetch the education details for the authenticated user
        """
        try:
            details = request.user.education_details_appearing
            serializer = EducationDetailsAppearingSerializer(details)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EducationDetailsAppearing.DoesNotExist:
            return Response({'message': 'Education details not found.'}, status=status.HTTP_404_NOT_FOUND)
        


    def post(self, request):
        """
        Create education details for the authenticated user
        Ensure the user does not already have passed education details.

        """

         # Check if the user already has passed education details
        if hasattr(request.user, 'education_details_passed'):  # Change made here
            return Response({'message': 'User already has passed education details. Cannot add appearing details.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = EducationDetailsAppearingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate with the authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update the education details for the authenticated user
        """
        try:
            details = request.user.education_details_appearing
        except EducationDetailsAppearing.DoesNotExist:
            return Response({'message': 'Education details not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationDetailsAppearingSerializer(details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class EducationDetailsPassedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetch the education details for the authenticated user
        """
        try:
            details = request.user.education_details_passed
            serializer = EducationDetailsPassedSerializer(details)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EducationDetailsPassed.DoesNotExist:
            return Response({'message': 'Education details not found.'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create education details for the authenticated user
        Ensure the user does not already have appearing education details.
        """
        # Check if the user already has appearing education details
        if hasattr(request.user, 'education_details_appearing'):  # Change made here
            return Response({'message': 'User already has appearing education details. Cannot add passed details.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        serializer = EducationDetailsPassedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Associate with the authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update the education details for the authenticated user
        """
        try:
            details = request.user.education_details_passed
        except EducationDetailsPassed.DoesNotExist:
            return Response({'message': 'Education details not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EducationDetailsPassedSerializer(details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from account.profile import get_profile_completion_status


class ProfileCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status = get_profile_completion_status(request.user)
        return Response(status, status=200)