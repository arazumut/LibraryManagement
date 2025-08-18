from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
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
    LoanSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows books to be viewed or edited.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def loans(self, request, pk=None):
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
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def my_loans(self, request):
        loans = Loan.objects.filter(borrower=request.user)
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        loans = Loan.objects.filter(return_date__isnull=True)
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        # İçe aktarmaları fonksiyonun dışında yapmak yerine burada yapıyoruz
        import datetime
        loans = Loan.objects.filter(
            return_date__isnull=True, 
            due_date__lt=datetime.date.today()
        )
        serializer = self.get_serializer(loans, many=True)
        return Response(serializer.data)
