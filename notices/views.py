from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notice

@login_required
def create_notice(request):
    user = request.user
    if user.role not in ['teacher', 'admin'] and not user.is_superuser:
        messages.error(request, "Access denied. Only teachers and admins can create notices.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        if title and description:
            Notice.objects.create(
                title=title,
                description=description,
                created_by=user
            )
            messages.success(request, "Notice posted successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fill out all fields.")
            
    return render(request, 'notices/create.html')

from django.http import JsonResponse

@login_required
def latest_notice_api(request):
    latest = Notice.objects.all().order_by('-created_at').first()
    if latest:
        return JsonResponse({
            'status': 'success',
            'id': latest.id,
            'title': latest.title,
            'description': latest.description[:100] + '...' if len(latest.description) > 100 else latest.description,
            'created_by': latest.created_by.get_full_name() or latest.created_by.username,
            'created_at': latest.created_at.strftime('%Y-%m-%d %I:%M %p')
        })
    return JsonResponse({'status': 'empty'})
