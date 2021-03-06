from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RequestMusicForm
from .models import UserInput, YoutubeLink
import pydub
from .youtube import youtubedl
from .extract import *
from django.contrib import messages

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
base_url = "https://www.youtube.com/watch?v="

# Create your views here.
def index(request):
    return render(request, 'lofi/index.html')

def request_lofi(request):
    if request.method == 'POST':
        form = RequestMusicForm(request.POST)
        if form.is_valid():
            article_url = form.cleaned_data['article_url']
            text = form.cleaned_data['text']
            freq_num = form.cleaned_data['freq_num']
            rand_video = form.cleaned_data['rand_video']
            has_url = False

            # checks to see if any blanks
            if not article_url:
                has_url = True
            
            if not freq_num or (freq_num < 1 and freq_num > 9):
                freq_num = 3

            # UserInput.objects.create(article_url=article_url, has_url=has_url, text="Done", freq_num=freq_num,
            # rand_video=rand_video)
            videoId = ""

            if article_url:
                videoId = article_request(article_url, freq_num, rand_video)
            elif text:
                videoId = text_request(text, freq_num, rand_video)
            else:
                messages.error(request, 'Please enter an article url or some text.')
                return render(request, "lofi/request_lofi.html", {
                    'form': form
                })

            if videoId is not None:
                video = base_url + videoId
            else:
                messages.error(request, 'Sorry! Please try again.')
                return render(request, "lofi/request_lofi.html", {
                    'form': form
                })

            ytVid = YoutubeLink.objects.create(url=video)
            # return redirect('playback', ytVid.id)
            request.session['converted'] = False
            # return redirect('loading', converted)
            return redirect('playback', ytVid.id)
            # return redirect('loading')
    else:
        form = RequestMusicForm()
    return render(request, 'lofi/request_lofi.html', {'form': form})


def playback(request, video_id):
    converted = request.session.get('converted')
    video_object = YoutubeLink.objects.get(pk=video_id)
    url = video_object.url
    video_id = url[32:]
    youtubedl(url)
    filename = "downloads/" + video_id + ".wav"

    return render(request, 'lofi/playback.html', {"url": url, "video_id": video_id, "filename": filename})


def visualizer(request, video_id):
    filename = "downloads/" + video_id + ".wav"
    return render(request, 'lofi/visualizer.html', {"filename": filename})
