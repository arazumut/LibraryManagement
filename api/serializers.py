from rest_framework import serializers
from accounts.models import User
from books.models import Book
from books.models_category import Category
from libraries.models import Library
from loans.models import Loan

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type']
        read_only_fields = ['id']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category',
        write_only=True
    )
    available = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'isbn', 'author', 'publisher', 
            'publication_year', 'description', 'cover_image',
            'category', 'category_id', 'pages', 'language', 
            'status', 'available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_available(self, obj) -> bool:
        """
        Returns True if the book status is 'available'.
        """
        return obj.status == 'available'

class LibrarySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    admins = UserSerializer(many=True, read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='owner',
        write_only=True
    )
    
    class Meta:
        model = Library
        fields = [
            'id', 'name', 'address', 'phone', 'email',
            'description', 'owner', 'owner_id', 'admins',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class LoanSerializer(serializers.ModelSerializer):
    borrower = UserSerializer(read_only=True)
    loaned_by = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    borrower_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='borrower',
        write_only=True
    )
    loaned_by_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='loaned_by',
        write_only=True
    )
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        source='book',
        write_only=True
    )
    
    class Meta:
        model = Loan
        fields = [
            'id', 'borrower', 'borrower_id', 'loaned_by', 'loaned_by_id', 
            'book', 'book_id', 'loan_date', 'due_date', 'return_date',
            'status', 'notes'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
