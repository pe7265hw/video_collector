from django.test import TestCase
from django.urls import reverse
from .models import Video
from django.db import IntegrityError
from django.core.exceptions import ValidationError

class TestHomePageMessage(TestCase):

    def test_app_title_message_show_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Time Wasting Dwarf Fortress Videos')

class TestAddVideos(TestCase):
    
    def test_add_video(self):
        valid_video = {
            'name': 'survival of the smartest (Dwarf Fortress)',
            'url': 'https://www.youtube.com/watch?v=IyFsxqsW96M',
            'notes': 'Hoodie Hair video on Dwarf Fortress and dwarvern discoveries.' 
        }

        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)

        self.assertTemplateUsed('video_collection/video_list.html')

        # does video list show the new video?
        self.assertContains(response, 'survival of the smartest')
        self.assertContains(response, 'Hoodie Hair video on Dwarf Fortress and dwarvern discoveries.')
        self.assertContains(response, 'https://www.youtube.com/watch?v=IyFsxqsW96M')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        video = Video.objects.first()

        self.assertEqual('survival of the smartest (Dwarf Fortress)', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=IyFsxqsW96M', video.url)
        self.assertEqual('Hoodie Hair video on Dwarf Fortress and dwarvern discoveries.', video.notes)
        self.assertEqual('IyFsxqsW96M', video.video_id)

    # This tests creates a NoneType Error at the code:
    # messages = response.context['messages'] that I cannot figure out
    def test_add_video_invalid_url_not_added(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=klajsdlkj90w8'
        ]

        url = reverse('add_video')

        for invalid_video_url in invalid_video_urls:
            new_video = {
                'name': 'example',
                'url': invalid_video_url,
                'notes': 'example notes'
            }

        
            response = self.client.post(url, new_video)

            self.assertTemplateUsed('video_collection/add.html')

            messages = response.context['messages']
            message_texts = [message.message for message in messages]

            self.assertIn('Invalid Youtube URL', message_texts)
            self.assertIn('Please check the data entered.', message_texts)

            video_count = Video.objects.count()
            self.assertEqual(0, video_count)

class TestVideoList(TestCase):
    
    #This is also causing a Fail that I cannot figure out, it is always setting videos in template order to be the same as the instantiation order (v1, v2 etc)
    # This is the AssertionError that I see when I run the test, I tried swapping expected_video_order and videos_in_template but got the same result, I'm not sure if it's a problem of the response.context['videos'], I seem to be having bad luck with that
    # AssertionError: Lists differ: [<Vid[102 chars] ID: 2, Name: abc, URL: https://www.youtube.co[238 chars]mpe>] != [<Vid[102 chars] ID: 1, Name: ZXY, URL: https://www.youtube.co[238 chars]mpe>]
    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(name='ZXY', notes='exampe', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='exampe', url='https://www.youtube.com/watch?v=124')
        v3 = Video.objects.create(name='AAA', notes='exampe', url='https://www.youtube.com/watch?v=125')
        v4 = Video.objects.create(name='lmn', notes='exampe', url='https://www.youtube.com/watch?v=126')

        expected_video_order = [v3, v2, v4, v1]

        url = reverse('video_list')
        response = self.client.get(url)

        videos_in_template = list(response.context['videos'])

        self.assertEqual(expected_video_order, videos_in_template)

    def test_no_video_message(self):
        url = reverse('video_list')
        response = self.client.get(url)
        self.assertContains(response, 'No videos were found')
        self.assertEqual(0, len(response.context['videos']))

    def test_video_number_message_one_video(self):
        v1 = Video.objects.create(name='ZXY', notes='exampe', url='https://www.youtube.com/watch?v=123')
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')    

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='ZXY', notes='exampe', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='exampe', url='https://www.youtube.com/watch?v=124')
        url = reverse('video_list')
        response = self.client.get(url)

        self.assertContains(response, '2 videos')

        


class TestVideoSearch(TestCase):
    pass



class TestVideoModel(TestCase):
    
    def test_duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='ZXY', notes='exampe', url='https://www.youtube.com/watch?v=123')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='ZXY', notes='exampe', url='https://www.youtube.com/watch?v=123')

    def test_invalid_url_raises_invalidation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://github.com',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=klajsdlkj90w8'
        ]

        for invalid_video_url in invalid_video_urls:

            with self.assertRaises(ValidationError):
                Video.objects.create(name="example", url=invalid_video_url, notes="example note")

        self.assertEqual(0, Video.objects.count())