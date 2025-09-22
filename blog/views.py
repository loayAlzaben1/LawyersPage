from django.shortcuts import render, get_object_or_404
from .models import BlogPost
from .models import LawyerCard
from .forms import CommentForm
from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage
from django.template.loader import render_to_string
from django.http import JsonResponse, Http404
import os


PAGE_SIZE = 6


def index(request):
    posts_qs = BlogPost.objects.filter(published_at__isnull=False).order_by('-published_at')
    paginator = Paginator(posts_qs, PAGE_SIZE)
    page = request.GET.get('page') or 1
    try:
        posts = paginator.page(page)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Get active lawyer cards to display on the homepage
    lawyers = LawyerCard.objects.filter(is_active=True).order_by('order')[:12]

    # Small debug log to confirm this view executed and which template is served
    try:
        print('DEBUG: Rendering blog index (template updated 2025-09-19)')
    except Exception:
        pass

    return render(request, 'blog/index.html', {
        'posts': posts,
        'page_obj': posts,
        'is_paginated': paginator.num_pages > 1,
        'lawyers': lawyers,
    })


def index_page(request):
    """AJAX endpoint: return rendered HTML for a specific page of cards."""
    if not request.is_ajax() and request.headers.get('x-requested-with') != 'XMLHttpRequest':
        raise Http404
    page = request.GET.get('page') or 1
    posts_qs = BlogPost.objects.filter(published_at__isnull=False).order_by('-published_at')
    paginator = Paginator(posts_qs, PAGE_SIZE)
    try:
        posts = paginator.page(page)
    except EmptyPage:
        return JsonResponse({'html': '', 'has_next': False})

    html = render_to_string('blog/_cards_page.html', {'posts': posts, 'request': request, 'lawyers': LawyerCard.objects.filter(is_active=True).order_by('order')[:12]})
    return JsonResponse({'html': html, 'has_next': posts.has_next()})


def detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.approved = False
            comment.save()
            # Redirect to avoid resubmission
            return redirect(post.get_absolute_url())
    else:
        form = CommentForm()

    approved_comments = post.comments.filter(approved=True)
    return render(request, 'blog/detail.html', {
        'post': post,
        'comment_form': form,
        'approved_comments': approved_comments,
    })


def dev_check(request):
    # Simple endpoint to confirm this Django process is serving requests.
    try:
        print('DEV CHECK: blog.dev_check hit')
    except Exception:
        pass
    from django.http import HttpResponse
    return HttpResponse('blog.dev-check OK - 2025-09-19')
