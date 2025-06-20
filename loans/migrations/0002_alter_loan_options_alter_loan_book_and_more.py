# Generated by Django 5.2.3 on 2025-06-20 13:04

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_tag_alter_book_options_alter_booknote_options_and_more'),
        ('loans', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loan',
            options={'ordering': ['-loan_date'], 'verbose_name': 'Ödünç Verme', 'verbose_name_plural': 'Ödünç Vermeler'},
        ),
        migrations.AlterField(
            model_name='loan',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='books.book', verbose_name='Kitap'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='borrower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowed_books', to=settings.AUTH_USER_MODEL, verbose_name='Ödünç Alan'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='due_date',
            field=models.DateTimeField(verbose_name='İade Tarihi'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='loan_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Ödünç Verme Tarihi'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='loaned_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_loans', to=settings.AUTH_USER_MODEL, verbose_name='Ödünç Veren'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notlar'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='return_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Gerçek İade Tarihi'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='status',
            field=models.CharField(choices=[('active', 'Aktif'), ('returned', 'İade Edildi'), ('overdue', 'Gecikmiş')], default='active', max_length=10, verbose_name='Durum'),
        ),
    ]
