from django.shortcuts import render
from django.contrib.auth import get_user
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets, generics, status
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.db.models import Q
from .models import UrlEntry, User
from .serializers import UrlEntrySerializer, UserGetEntrySerializer, EmailSerializer, ResetPasswordSerializer
from .smtp import sendEmail
import json

class UserListView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):

        '''
        List all username for given requested user
        then it's possible to further filter out results basing on the optional query paramater
        '''      
        try:
            query = '' if request.GET.get('query') == None else request.GET.get('query')
            usernames = User.objects.all().filter(Q(username=query))
            serializer = UserGetEntrySerializer(usernames, many=True)
        except:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        '''
        Creates new user entry
        {"username":"test","email":"test@test.com","password":"zaq1@WSX"}
        '''
        try:
            if len(User.objects.all().filter(username=request.data.get('username'))) > 0:
                raise Exception("This user alrady exists!") 

            new_entry = {
                'username': request.data.get('username'),
                'email': request.data.get('email'),
                'password': request.data.get('password')
            }

            user = User.objects.create_user(username=new_entry["username"], email=new_entry["email"], password=new_entry["password"])   
            user.save
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)  
        else:
            return Response(status=status.HTTP_201_CREATED)

class UserDetailedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        
        try:
            user = request.user
            print(user)
            # user.delete()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)  
        else:
            return Response(status=status.HTTP_200_OK)


    def put(self, request, *args, **kwargs):
        
        try:
            user = request.user
            user.save()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)  
        else:
            return Response(status=status.HTTP_200_OK)
        
class UserPasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        
        try:
            user = request.user
            user.set_password(request.data.get('password'))
            user.save()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)  
        else:
            return Response(status=status.HTTP_200_OK)

class UrlListView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        '''
        List all Url items for given requested user
        then it's possible to further filter out results basing on the optional query paramater
        '''      
       
        query = '' if request.GET.get('query') == None else request.GET.get('query')

        urls = UrlEntry.objects.filter(user = request.user.id).filter(Q(url_name__icontains=query) | Q(url_desc__icontains=query))
        serializer = UrlEntrySerializer(urls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
           
    def post(self, request, *args, **kwargs):
        '''
        Creates new url entry for specific user
        test: {"url_name":"wp.pl","url_link":"http://www.wp.pl","url_desc":"My favorite news portal"}
        '''
        new_entry = {
            'url_name': request.data.get('url_name'),
            'url_link': request.data.get('url_link'),
            'url_desc': request.data.get('url_desc'),
            'user': request.user.id
        }

        serializer = UrlEntrySerializer(data=new_entry)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UrlDetailView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, url_id, user_id):
        '''
        Helper method to get the object with given todo_id, and user_id
        '''
        try:
            return UrlEntry.objects.get(id=url_id, user = user_id)
        except UrlEntry.DoesNotExist:
            return None

    def get(self, request, url_id, *args, **kwargs):
        '''
        Retrieves the Todo with given todo_id
        '''
        url_entry = self.get_object(url_id, request.user.id)
        if not url_entry:
            return Response(
                {"res": "Object with url id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UrlEntrySerializer(url_entry)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, url_id, *args, **kwargs):
        url_entry = self.get_object(url_id, request.user.id)
        if not url_entry:
            return Response(
                {"res": "Object with url id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_entry = {
            'url_name': request.data.get('url_name'),
            'url_link': request.data.get('url_link'),
            'url_desc': request.data.get('url_desc'),
            'user': request.user.id
        }

        serializer = UrlEntrySerializer(instance = url_entry, data=new_entry, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, url_id, *args, **kwargs):
        url_entry = self.get_object(url_id, request.user.id)
        if not url_entry:
            return Response(
                {"res": "Object with url id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        url_entry.delete()
        return Response({"res": "Object deleted!"}, status=status.HTTP_200_OK)

class PasswordReset(APIView):
    permission_classes = [permissions.AllowAny]

    """
    Request for Password Reset Link.
    """

    serializer_class = EmailSerializer

    def post(self, request):    
        """
        Create token.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]
        user = User.objects.filter(email=email).first()
        if user:
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            # reset_url =  reverse(
            #     "password-reset",
            #     kwargs={"encoded_pk": encoded_pk, "token": token},
            # )
            reset_link = f"{settings.FE_URL}/password-change/{encoded_pk}/{token}"

            smtp_response = sendEmail(email, 1, reset_link)
            
            if (smtp_response.message_id):
                return Response({"message": f"Email successfully sent, id: {smtp_response.message_id}"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": smtp_response}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "User doesn't exists"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ResetPassword(APIView):
    """
    Verify and Reset Password Token View.
    """
    permission_classes = [permissions.AllowAny]

    serializer_class = ResetPasswordSerializer

    def patch(self, request, *args, **kwargs):
        """
        Verify token & encoded_pk and then reset the password.
        """
        serializer = self.serializer_class(
            data=request.data, context={"kwargs": kwargs}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"message": "Password reset complete"},
            status=status.HTTP_200_OK,
        )