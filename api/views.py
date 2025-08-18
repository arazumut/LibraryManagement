from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from django.contrib.auth import get_user_model
from accounts.models import User
from books.models import Book
from books.models_category import Category
from libraries.models import Library
from loans.models import Loan
from .serializers import (
    UserSerializer, 
    BookSerializer, 
    CategorySerializer,
    LibrarySerializer, 
    LoanSerializer,
    UserRegistrationSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    
    list:
    Return a list of all users.
    
    retrieve:
    Return the user instance.
    
    create:
    Create a new user instance.
    
    update:
    Update an existing user instance.
    
    partial_update:
    Update part of an existing user instance.
    
    destroy:
    Delete a user instance.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Returns the current user's profile information.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    
    list:
    Return a list of all books.
    
    retrieve:
    Return the book instance.
    
    create:
    Create a new book instance.
    
    update:
    Update an existing book instance.
    
    partial_update:
    Update part of an existing book instance.
    
    destroy:
    Delete a book instance.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def loans(self, request, pk=None):
        """
        Returns a list of loans for the specified book.
        """
        book = self.get_object()
        loans = Loan.objects.filter(book=book)
        serializer = LoanSerializer(loans, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        category = self.get_object()
        books = Book.objects.filter(category=category)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

class LibraryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows libraries to be viewed or edited.
    """
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class LoanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows loans to be viewed or edited.
    
    list:
    Return a list of all loans.
    
    retrieve:
    Return the loan instance.
    
    create:
    Create a new loan instance.
    
    update:
    Update an existing loan instance.
    
    partial_update:
    Update part of an existing loan instance.
    
    destroy:
    Delete a loan instance.
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_loans(self, request):
        """
        Returns all loans for the current authenticated user.
        """
        loans = Loan.objects.filter(borrower=request.user)
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Returns all active loans (loans that have not been returned yet).
        """
        loans = Loan.objects.filter(return_date__isnull=True)
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Returns all overdue loans (loans that are past their due date and not returned).
        """
        # İçe aktarmaları fonksiyonun dışında yapmak yerine burada yapıyoruz
        import datetime
        loans = Loan.objects.filter(
            return_date__isnull=True, 
            due_date__lt=datetime.date.today()
        )
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)


class UserRegisterView(CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class CurrentUserView(RetrieveAPIView):
    """
    API endpoint to get current user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
