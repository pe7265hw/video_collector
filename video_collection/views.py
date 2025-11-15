from django.shortcuts import render
from .forms import VideoForm
from django.contrib import messages

def home(request):
    app_name = 'Time Wasting Dwarf Fortress Videos'
    return render(request, 'video_collection/home.html', {'app_name': app_name})

def add(request):
    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            new_video_form.save()
            messages.info(request, 'New video saved!')
            #todo show success message or redirect to list of videos
        else:
            messages.warning(request, 'Please check the data entered.')
            return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})
            # if data is not valid it will re-display the same page, but will have the data the user typed in
    
    new_video_form = VideoForm
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})
