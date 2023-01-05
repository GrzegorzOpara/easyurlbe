from django.shortcuts import render
from django.contrib.auth import get_user
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.db.models import Q
from .models import UrlEntry, User
from .serializers import UrlEntrySerializer, UserGetEntrySerializer


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
            user.delete()
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
