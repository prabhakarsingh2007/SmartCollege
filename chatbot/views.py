from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatHistory
from .services import get_chatbot_response
import json

@login_required
def chatbot_view(request):
    user = request.user
    
    if request.method == 'POST':
        # Check if request is JSON (AJAX)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                question = data.get('question', '').strip()
            except json.JSONDecodeError:
                question = ''
        else:
            question = request.POST.get('question', '').strip()
            
        if question:
            answer = get_chatbot_response(user, question)
            
            # Save to history
            ChatHistory.objects.create(
                user=user,
                question=question,
                answer=answer
            )
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'status': 'success',
                    'question': question,
                    'answer': answer
                })
                
        # Non-AJAX fallback redirects back to chat view
        return redirect('chatbot')

    # Get user's chat history
    history = ChatHistory.objects.filter(user=user).order_by('timestamp')
    
    return render(request, 'chatbot/chat.html', {
        'history': history
    })
