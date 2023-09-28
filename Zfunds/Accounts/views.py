from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication

from .models import CustomUser
from .serializers import UserSerializer


class RegisterView(APIView):
    """
        EndPoint for User Registration
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        if not 'otp' in request.data:
            return Response({"Error" : "otp is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)

        if(serializer.is_valid()):
            serializer.save()
            user = serializer.instance

            if(user.role == "advisor"):
                user.is_advisor = True 
                user.save()

            if(not user.verify_otp(request.data["otp"])): # dummy logic for otp verification
                user.is_active = False 
                user.save()
                return Response({"Error" : "invalid otp"}, status=status.HTTP_400_BAD_REQUEST)        

            token, created = Token.objects.get_or_create(user=user)
            return Response({
            'token': token.key,
            'user_id': user.pk,
            'mobile': user.mobile
        })

        return Response({"Status" : "failed to register"})    

class AdvisorUserRegisterView(APIView):
    """
        EndPoint for adding Users by Advisors
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        if not request.user.is_advisor:
            return Response({"Error" : "Only Advisors Can Add Users"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)

        if(serializer.is_valid()):
            serializer.save()
            user = serializer.instance
            user.role = "user" # If an Advisor adds a User then role will be user
            user.save()
            data = dict(serializer.initial_data)
            resp = {"id" : user.id, "mobile" : data["mobile"], "role" : data["role"], "status" : f"User created by {request.user.mobile}"}

            return Response(resp)

        return Response({"Status" : "failed to register"})    


class CustomAuthToken(ObtainAuthToken):

    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        user = None
        
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user = serializer.instance
        except:
            # if user already exists then get by mobile
            user = CustomUser.objects.get(mobile=request.data.get("mobile"))

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'mobile': user.mobile,
            'role' : user.role
        })