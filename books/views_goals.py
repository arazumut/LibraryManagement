from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models_goals import ReadingGoal, ReadingChallenge
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from datetime import datetime, timedelta

@login_required
def goal_list(request):
    """
    Display a list of user's reading goals
    """
    user_goals = ReadingGoal.objects.filter(user=request.user)
    active_goals = user_goals.filter(is_completed=False)
    completed_goals = user_goals.filter(is_completed=True)
    
    # Get public challenges
    public_challenges = ReadingChallenge.objects.filter(
        is_private=False, 
        status__in=['upcoming', 'ongoing']
    ).order_by('start_date')[:5]
    
    context = {
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'public_challenges': public_challenges,
        'active_menu': 'reading_goals'
    }
    
    return render(request, 'books/goal_list.html', context)

@login_required
def goal_create(request):
    """
    Create a new reading goal
    """
    if request.method == 'POST':
        # Process the form data here
        # This is a placeholder for form processing
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        goal_type = request.POST.get('goal_type')
        target_value = request.POST.get('target_value')
        period = request.POST.get('period')
        start_date = request.POST.get('start_date') or timezone.now().date()
        end_date = request.POST.get('end_date') or None
        is_public = request.POST.get('is_public', False) == 'on'
        
        try:
            goal = ReadingGoal.objects.create(
                user=request.user,
                title=title,
                description=description,
                goal_type=goal_type,
                target_value=target_value,
                period=period,
                start_date=start_date,
                end_date=end_date,
                is_public=is_public
            )
            messages.success(request, f'Reading goal "{goal.title}" created successfully!')
            return redirect('books:goal_list')
        except Exception as e:
            messages.error(request, f'Error creating goal: {str(e)}')
    
    # For GET requests or form errors
    context = {
        'active_menu': 'reading_goals',
        'goal_types': ReadingGoal.GOAL_TYPE_CHOICES,
        'periods': ReadingGoal.PERIOD_CHOICES,
        'today': timezone.now()
    }
    return render(request, 'books/goal_create.html', context)

@login_required
def goal_detail(request, goal_id):
    """
    Display details of a reading goal
    """
    goal = get_object_or_404(ReadingGoal, id=goal_id)
    
    # Check if the user has permission to view this goal
    if goal.user != request.user and not goal.is_public:
        messages.error(request, "You don't have permission to view this goal.")
        return redirect('books:goal_list')
    
    context = {
        'goal': goal,
        'active_menu': 'reading_goals'
    }
    
    return render(request, 'books/goal_detail.html', context)

@login_required
def goal_update(request, goal_id):
    """
    Update an existing reading goal
    """
    goal = get_object_or_404(ReadingGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        # Process the form data here
        goal.title = request.POST.get('title', goal.title)
        goal.description = request.POST.get('description', goal.description)
        goal.goal_type = request.POST.get('goal_type', goal.goal_type)
        goal.target_value = request.POST.get('target_value', goal.target_value)
        goal.period = request.POST.get('period', goal.period)
        
        if request.POST.get('start_date'):
            goal.start_date = request.POST.get('start_date')
        
        if request.POST.get('end_date'):
            goal.end_date = request.POST.get('end_date')
        
        goal.is_public = request.POST.get('is_public', False) == 'on'
        
        try:
            goal.save()
            messages.success(request, f'Reading goal "{goal.title}" updated successfully!')
            return redirect('books:goal_detail', goal_id=goal.id)
        except Exception as e:
            messages.error(request, f'Error updating goal: {str(e)}')
    
    # For GET requests or form errors
    context = {
        'goal': goal,
        'active_menu': 'reading_goals',
        'goal_types': ReadingGoal.GOAL_TYPE_CHOICES,
        'periods': ReadingGoal.PERIOD_CHOICES
    }
    return render(request, 'books/goal_edit.html', context)

@login_required
def goal_delete(request, goal_id):
    """
    Delete a reading goal
    """
    goal = get_object_or_404(ReadingGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        goal_title = goal.title
        goal.delete()
        messages.success(request, f'Reading goal "{goal_title}" deleted successfully!')
        return redirect('books:goal_list')
    
    context = {
        'goal': goal,
        'active_menu': 'reading_goals'
    }
    
    return render(request, 'books/goal_confirm_delete.html', context)

@login_required
def goal_update_progress(request, goal_id):
    """
    Update progress for a reading goal
    """
    goal = get_object_or_404(ReadingGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        progress_value = int(request.POST.get('progress_value', 0))
        
        if progress_value > 0:
            goal.update_progress(progress_value)
            messages.success(request, f'Progress updated for "{goal.title}"!')
        
        return redirect('books:goal_detail', goal_id=goal.id)
    
    context = {
        'goal': goal,
        'active_menu': 'reading_goals'
    }
    
    return render(request, 'books/goal_update_progress.html', context)

@login_required
def goal_dashboard(request):
    """Okuma hedefleri dashboard'u."""
    # Aktif hedefler
    active_goals = ReadingGoal.objects.filter(
        user=request.user,
        status='active'
    ).order_by('-created_at')
    
    # Tamamlanan hedefler (son 5)
    completed_goals = ReadingGoal.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-updated_at')[:5]
    
    context = {
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'active_menu': 'goals',
    }
    
    return render(request, 'books/goal_dashboard.html', context)

@login_required
def goal_analytics(request, goal_id):
    """Hedef analitikleri."""
    goal = get_object_or_404(ReadingGoal, id=goal_id, user=request.user)
    
    # İlerleme verileri
    from analytics.models import ReadingGoalProgress
    progress_data = ReadingGoalProgress.objects.filter(
        goal=goal
    ).order_by('date')
    
    # Günlük ilerleme grafiği için veri
    daily_progress = []
    cumulative_progress = []
    
    for progress in progress_data:
        daily_progress.append({
            'date': progress.date.strftime('%Y-%m-%d'),
            'value': progress.daily_progress
        })
        cumulative_progress.append({
            'date': progress.date.strftime('%Y-%m-%d'),
            'value': progress.cumulative_progress
        })
    
    # Hedef tamamlanma tahmini
    if goal.current_value > 0 and goal.target_value > goal.current_value:
        days_passed = (timezone.now().date() - goal.start_date).days
        if days_passed > 0:
            daily_average = goal.current_value / days_passed
            remaining_days = (goal.target_value - goal.current_value) / daily_average if daily_average > 0 else None
            estimated_completion = timezone.now().date() + timezone.timedelta(days=int(remaining_days)) if remaining_days else None
        else:
            estimated_completion = None
    else:
        estimated_completion = None
    
    context = {
        'goal': goal,
        'progress_data': progress_data,
        'daily_progress': daily_progress,
        'cumulative_progress': cumulative_progress,
        'estimated_completion': estimated_completion,
    }
    
    return render(request, 'books/goal_analytics.html', context)

@login_required
def update_goal_progress(request, goal_id):
    """Hedef ilerlemesini güncelle."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    goal = get_object_or_404(ReadingGoal, id=goal_id, user=request.user)
    
    if goal.status != 'active':
        return JsonResponse({'error': 'Bu hedef aktif değil'}, status=400)
    
    progress_value = request.POST.get('progress', 0)
    
    try:
        progress_value = int(progress_value)
        if progress_value < 0:
            return JsonResponse({'error': 'İlerleme değeri negatif olamaz'}, status=400)
        
        # Hedef ilerlemesini güncelle
        old_value = goal.current_value
        goal.current_value = min(goal.current_value + progress_value, goal.target_value)
        
        # Hedef tamamlandı mı kontrol et
        if goal.current_value >= goal.target_value:
            goal.status = 'completed'
            goal.updated_at = timezone.now()
            
            # Başarı bildirimi
            from accounts.models_notification import Notification
            Notification.objects.create(
                recipient=request.user,
                notification_type='goal_achieved',
                title='Hedef Tamamlandı! 🎉',
                message=f'"{goal.title}" hedefinizi başarıyla tamamladınız!',
                priority='high'
            )
        
        goal.save()
        
        # Günlük ilerleme kaydı oluştur
        from analytics.models import ReadingGoalProgress
        today = timezone.now().date()
        progress_record, created = ReadingGoalProgress.objects.get_or_create(
            goal=goal,
            date=today,
            defaults={
                'daily_progress': progress_value,
                'cumulative_progress': goal.current_value,
            }
        )
        
        if not created:
            # Eğer kayıt zaten varsa, sadece ilerlemeyi güncelle
            progress_record.daily_progress += progress_value
            progress_record.cumulative_progress = goal.current_value
            progress_record.save()
        
        return JsonResponse({'success': 'İlerleme güncellendi', 'new_value': goal.current_value})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def reading_goals_dashboard(request):
    """
    Enhanced reading goals dashboard with analytics and insights
    """
    user_goals = ReadingGoal.objects.filter(user=request.user)
    
    # Calculate statistics
    total_goals = user_goals.count()
    active_goals = user_goals.filter(status='in_progress')
    completed_goals = user_goals.filter(status='completed')
    
    # Current year goals
    current_year = timezone.now().year
    yearly_goals = user_goals.filter(
        start_date__year=current_year
    )
    
    # Calculate completion rate
    completion_rate = 0
    if yearly_goals.exists():
        completed_yearly = yearly_goals.filter(status='completed').count()
        completion_rate = (completed_yearly / yearly_goals.count()) * 100
    
    # Get progress data for chart
    progress_data = []
    for goal in active_goals[:5]:  # Top 5 active goals
        progress_data.append({
            'name': goal.title,
            'progress': goal.progress_percentage,
            'target': goal.target_value,
            'current': goal.current_value
        })
    
    # Monthly goal completion trend
    monthly_completions = []
    for i in range(12):
        month = datetime.now().replace(month=i+1, day=1)
        completed_in_month = completed_goals.filter(
            end_date__month=month.month,
            end_date__year=current_year
        ).count()
        monthly_completions.append(completed_in_month)
    
    context = {
        'total_goals': total_goals,
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'completion_rate': completion_rate,
        'progress_data': progress_data,
        'monthly_completions': monthly_completions,
        'yearly_goals_count': yearly_goals.count(),
        'active_menu': 'reading_goals_dashboard'
    }
    
    return render(request, 'books/goals/dashboard.html', context)