from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models_goals import ReadingGoal, ReadingChallenge
from django.utils import timezone

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
        'periods': ReadingGoal.PERIOD_CHOICES
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
