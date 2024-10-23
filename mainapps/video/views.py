from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from mainapps.vidoe_text.models import TextFile, TextLineVideoClip, LogoModel
from .models import VideoClip, ClipCategory
import json

@login_required
def add_video_clip(request, category_id):
    category = get_object_or_404(ClipCategory, id=category_id)

    if request.method == 'POST':
        video_file = request.FILES.get('video_file')
        if video_file:
            VideoClip.objects.create(video_file=video_file, title=video_file.name, category=category)
            return HttpResponse(status=200)
    return render(request, 'partials/add_video.html', {'category': category})

@login_required
def delete_clip(request, clip_id):
    clip = get_object_or_404(VideoClip, id=clip_id)
    if request.method == 'POST':
        if clip.video_file:
            clip.video_file.delete(save=False)
        clip.delete()
        return HttpResponse(status=204)
    return render(request, 'partials/confirm_delete.html', {'item': clip})

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(ClipCategory, id=category_id)
    if request.method == 'POST':
        delete_category_and_subcategories(category)
        return HttpResponse(status=204)
    return render(request, 'partials/confirm_delete.html', {'item': category})

def delete_category_and_subcategories(cat):
    # Recursively delete subcategories and associated video clips
    cat.video_clips.all().delete()
    for subcategory in cat.subcategories.all():
        delete_category_and_subcategories(subcategory)
    cat.delete()

@login_required
def category_view(request, category_id=None, video_id=None):
    videos = []
    subcategories = []
    main_categories = []
    current_category = None
    video = None

    if category_id:
        current_category = get_object_or_404(ClipCategory, id=category_id, user=request.user)
        subcategories = current_category.subcategories.all()
        videos = current_category.video_clips.all()
        if video_id:
            video = get_object_or_404(VideoClip, category=current_category, id=video_id)
    else:
        main_categories = ClipCategory.objects.filter(user=request.user)

    context = {
        'current_category': current_category,
        'folders': main_categories,
        'subcategories': subcategories,
        'videos': videos,
        'category_id': category_id,
        'video_id': video_id,
        'video': video,
    }
    return render(request, 'assets/assets.html', context)

@login_required
def upload_video_folder(request):
    if request.method == 'POST':
        uploaded_folder = request.FILES.getlist('folder')
        directories = json.loads(request.POST.get('directories', '{}'))

        if not directories:
            return render(request, 'upload.html', {'error': 'No directory data provided.'})

        categories_ = []
        for folder_path, files in directories.items():
            parent = None
            folder_parts = folder_path.split('/')
            for folder_name in folder_parts:
                category, created = ClipCategory.objects.get_or_create(
                    name=folder_name,
                    parent=parent,
                    user=request.user
                )
                categories_.append(category)
                parent = category
            
            # Save the files under the last category (deepest folder)
            for file_name in files:
                file = next((f for f in uploaded_folder if f.name == file_name), None)
                if file and file.size > 0 and file.name.split('.')[-1].lower() in ['mp4', 'webm', 'mkv', 'avi', 'mov']:
                    VideoClip.objects.create(title=file_name, video_file=file, category=parent)
                elif file and file.size == 0:
                    messages.warning(request, f"File '{file_name}' is empty and has been skipped.")
                else:
                    messages.warning(request, f"File '{file_name}' is not a valid video format.")

        # Delete empty categories
        for cat in categories_:
            if not cat.video_clips.exists():
                messages.info(request, f'The folder {cat.name} was deleted since it has no video files in it.')
                cat.delete()

        messages.success(request, 'Files uploaded successfully!')
        return HttpResponse('Upload Successful!')

    return render(request, 'dir_upload.html')

@login_required
def add_video_clips(request, textfile_id):
    text_file = get_object_or_404(TextFile, id=textfile_id)
    if text_file.user != request.user:
        messages.error(request, 'You do not have access to the resources you requested.')
        return render(request, 'permission_denied.html')

    existing_clips = TextLineVideoClip.objects.filter(text_file=text_file)
    video_categories = ClipCategory.objects.filter(user=request.user)

    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        if purpose == 'process':
            process_video_clips(request, text_file, existing_clips)
            return redirect(f'/text/process-textfile/{textfile_id}')
        elif purpose == 'update':
            update_video_clips(request, existing_clips)
            messages.success(request, 'TextFile updated successfully')
            return redirect(f'/text/process-textfile/{textfile_id}')
        elif purpose == 'text_file' and request.FILES.get('text_file'):
            text_file.text_file = request.FILES.get('text_file')
            text_file.save()
            return redirect(reverse('video:add_scenes', args=[textfile_id]))
        else:
            messages.error(request, 'You did not upload a text file.')
            return redirect(reverse('video:add_scenes', args=[textfile_id]))

    return render_add_video_clips_page(text_file, existing_clips, video_categories)

def process_video_clips(request, text_file, existing_clips):
    """Process video clips based on the uploaded text file."""
    if existing_clips.exists():
        existing_clips.delete()

    lines = text_file.process_text_file()
    video_clips_data = []

    for index, line in enumerate(lines):
        video_file = request.FILES.get(f'uploaded_video_{index}')
        video_clip_id = request.POST.get(f'selected_video_{index}')
        video_clip = get_object_or_404(VideoClip, id=video_clip_id) if video_clip_id else None

        if video_file or video_clip:
            video_clips_data.append(TextLineVideoClip(
                text_file=text_file,
                video_file=video_clip,
                video_file_path=video_file,
                line_number=index + 1,
            ))
        else:
            messages.error(request, "You did not choose the clips completely.")
            return redirect(reverse('video:add_scenes', args=[textfile_id]))

    TextLineVideoClip.objects.bulk_create(video_clips_data)

def update_video_clips(request, existing_clips):
    """Update existing video clips with new files."""
    for i, clip in enumerate(existing_clips):
        video_file = request.FILES.get(f'uploaded_video_{i}')
        video_clip_id = request.POST.get(f'selected_video_{i}')
        video_clip = get_object_or_404(VideoClip, id=video_clip_id) if video_clip_id else None

        clip.video_file = video_clip
        if request.POST.get(f"video_{i}_status") == 'empty' and clip.video_file_path:
            clip.video_file_path.delete()
        if video_file and request.POST.get(f"video_{i}_status") == 'changed':
            clip.video_file_path = video_file
        clip.save()

def render_add_video_clips_page(text_file, existing_clips, video_categories):
    """Render the page for adding video clips."""
    return render(request, 'assets/add_video_clips.html', {
        'text_file': text_file,
        'existing_clips': existing_clips,
        'video_categories': video_categories,
    })
