from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from drf_spectacular.utils import extend_schema

from .models import CustomUser, Advisor
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
                advisor = Advisor.objects.create(user_profile=user)
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

    def add_client(self, request, client):
        if(request.user.is_advisor):

            if(request.user.mobile == client.mobile):
                return Response({"Error" : "Can not add yourself as client"})

            advisor = Advisor.objects.get(user_profile=request.user)
            client.client_advisor = advisor
            client.save()
            

    def post(self, request, format=None):
        if not request.user.is_advisor:
            return Response({"Error" : "Only Advisors Can Add Users/Clients"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        
        if(serializer.is_valid(raise_exception=True)):
            serializer.save()
            user = serializer.instance
            user.role = "user" # If an Advisor adds a User then role will be user
            user.save()

            # Add client to the adviso's client list
            self.add_client(request, user) #

            data = dict(serializer.initial_data)
            resp = {"id" : user.id, "mobile" : data["mobile"], "role" : data["role"], "status" : f"User created by {request.user.mobile}"}

            return Response(resp)

        return Response({"Status" : "Error, User already exists"})    

class AdvisorClientsView(APIView):
    """
        EndPoint for listing all the Clients for an Advisor
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        if not request.user.is_advisor:
            return Response({"Error" : "Only Advisors Can view Clients"}, status=status.HTTP_400_BAD_REQUEST)

        advisor = None 
        try:
            advisor = Advisor.objects.get(user_profile_id=pk)
        except Exception as e:
            return Response({"Message": f"Advisor with id {pk} does not exist"})
        
        if(advisor):
            # get all the clients for an advisor and send as response
            clients = [UserSerializer(user).data for user in advisor.clients.all()]
            for c in clients:
                c.pop("password")
            return Response({"clients": clients})



# View for creating/accessing login token after registratioin
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