from django.db import models
from django.utils.text import slugify
from books.models import Book
from django.conf import settings

class Category(models.Model):
    """
    Kitap kategorileri için model.
    """
    name = models.CharField('Kategori Adı', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True)
    description = models.TextField('Açıklama', blank=True, null=True)
    parent = models.ForeignKey('self', verbose_name='Üst Kategori', on_delete=models.CASCADE, 
                             blank=True, null=True, related_name='children')
    image = models.ImageField('Kategori Resmi', upload_to='category_images/', blank=True, null=True)
    color = models.CharField('Renk', max_length=7, default='#007bff', help_text='Hex color code')
    icon = models.CharField('İkon', max_length=50, blank=True, null=True, help_text='Font Awesome icon class')
    is_featured = models.BooleanField('Öne Çıkarılmış', default=False)
    order = models.PositiveIntegerField('Sıra', default=0)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    updated_at = models.DateTimeField('Güncellenme Tarihi', auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def book_count(self):
        """Bu kategorideki kitap sayısını döndürür."""
        return self.books.count()
    
    @property
    def total_book_count(self):
        """Bu kategori ve alt kategorilerindeki toplam kitap sayısı."""
        count = self.book_count
        for child in self.children.all():
            count += child.total_book_count
        return count
    
    @property
    def get_all_children(self):
        """Tüm alt kategorileri rekursif olarak döndürür."""
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children)
        return children
    
    @property
    def get_hierarchy_name(self):
        """Kategori hiyerarşisini string olarak döndürür."""
        if self.parent:
            return f"{self.parent.get_hierarchy_name} > {self.name}"
        return self.name
    
    def get_popular_books(self, limit=5):
        """Bu kategorideki popüler kitapları döndürür."""
        return self.books.all().order_by('-loan_count')[:limit]

class BookCategory(models.Model):
    """
    Kitap ve kategoriler arasındaki ilişki için ara model.
    """
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(Category, verbose_name='Kategori', on_delete=models.CASCADE, related_name='books')
    created_at = models.DateTimeField('Eklenme Tarihi', auto_now_add=True)
    
    class Meta:
        ordering = ['category__name']
        verbose_name = 'Kitap Kategorisi'
        verbose_name_plural = 'Kitap Kategorileri'
        # Bir kitap bir kategoride sadece bir kez olabilir
        unique_together = ['book', 'category']
        
    def __str__(self):
        return f"{self.book.title} - {self.category.name}"

class Tag(models.Model):
    """
    Kitap etiketleri için model.
    """
    name = models.CharField('Etiket Adı', max_length=50)
    slug = models.SlugField('Slug', max_length=50, unique=True)
    created_at = models.DateTimeField('Oluşturulma Tarihi', auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Etiket'
        verbose_name_plural = 'Etiketler'
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def book_count(self):
        """Bu etikete sahip kitap sayısını döndürür."""
        return self.books.count()

class BookTag(models.Model):
    """
    Kitap ve etiketler arasındaki ilişki için ara model.
    """
    book = models.ForeignKey(Book, verbose_name='Kitap', on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, verbose_name='Etiket', on_delete=models.CASCADE, related_name='books')
    created_at = models.DateTimeField('Eklenme Tarihi', auto_now_add=True)
    
    class Meta:
        ordering = ['tag__name']
        verbose_name = 'Kitap Etiketi'
        verbose_name_plural = 'Kitap Etiketleri'
        # Bir kitap bir etikete sadece bir kez sahip olabilir
        unique_together = ['book', 'tag']
        
    def __str__(self):
        return f"{self.book.title} - {self.tag.name}"
