from pathlib import Path
import cv2
from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.contenttypes.models import ContentType
from main.models import UserActionModel, TimeStampedModel
from courses.models.lecture_privacy import LecturePrivacy
from courses.models.lecture_quality import LectureQuality
from courses.models.comment import Comment
from moviepy.editor import VideoFileClip
from courses.utils import get_lecture_path

class Lecture(UserActionModel, TimeStampedModel):
    topic = models.ForeignKey("courses.Topic", on_delete=models.CASCADE, related_name="lectures")
    title = models.CharField(max_length=100)
    description = RichTextField()
    objectives = RichTextField(blank=True, null=True)
    video = models.FileField(upload_to=get_lecture_path, blank=True, null=True)
    audio = models.FileField(upload_to='audio', blank=True, null=True)
    script = RichTextField(blank=True, null=True, max_length=100)
    duration = models.FloatField(blank=True, default=0)
    order = models.IntegerField()
    quiz = models.OneToOneField("courses.Quiz", on_delete=models.CASCADE, blank=True, null=True)
    references = models.ManyToManyField("courses.Reference", blank=True)
    teacher = models.ForeignKey("users.Teacher", blank=True, null=True, on_delete=models.CASCADE, related_name="contributed_lectures")
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created', )

    def __str__(self):
          return self.title

    def atomic_post_save(self, sender, created, **kwargs):
        LecturePrivacy.objects.get_or_create(lecture=self)

    def can_access(self, user):
        if self.privacy.is_public():
            return True
        elif self.privacy.is_private():
            return False
        else:
            return user in self.privacy.shared_with.all()

    @property
    def comments(self):
        return Comment.objects.filter(object_type=ContentType.objects.get_for_model(self).id, status='published')

    def delete_qualities(self):
        LectureQuality.objects.filter(lecture=self).delete()
        return True

    def extract_and_set_audio(self):

        if not self.video:
            self.reset_audio()
            return False

        video = VideoFileClip(self.video.path)
        audio = video.audio
        if not audio:
            self.reset_audio()
            return False

        video_path = Path(self.video.path)
        audio_path = video_path.with_suffix('.mp3')
        out_audio = audio.write_audiofile(audio_path)

        self.audio = str(Path(self.video.name).with_suffix('.mp3'))
        self.save()
        return True

    def detect_and_change_video_duration(self):

        if self.video:
            self.duration = VideoFileClip(self.video.path).duration
        else:
            self.duration = 0
        self.save()
        return self.duration

    def detect_original_video_quality(self):

        video = cv2.VideoCapture(self.video.path)
        quality = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

        quality = self.__class__.scale_quality(quality)
        quality_attribute = getattr(LectureQuality.Qualities, f"_{quality}")
        if not quality_attribute:
            return None

        original_quality, created = LectureQuality.objects.get_or_create(
        lecture=self,
        video=str(self.video.name),
        quality=quality_attribute
        )
        return original_quality

    def reset_audio(self):
        self.audio = None
        self.save()

    def reset_duration(self):
        self.duration = 0
        self.save()

    @classmethod
    def convert_video_quality(cls, video_path, quality):
        from courses.utils import get_resolution

        found, width, height = get_resolution(quality)
        if not found:
            return None, False

        video = VideoFileClip(video_path)
        clip_resized = video.resize(height=height)

        video_name = Path(video_path)
        new_video_name = f'{video_name.stem}_{quality}{video_name.suffix}'
        new_video_path = Path(video_path).parent.joinpath(new_video_name)

        clip_resized.write_videofile(
        str(new_video_path),
        temp_audiofile=Path(video_path).parent.joinpath('temp-audio.m4a'),
        remove_temp=True,
        codec="libx264",
        audio_codec="aac"
        )
        return new_video_name, True

    @classmethod
    def get_supported_qualities(cls, quality):
        qualities = [144, 240, 360, 480, 720, 1080]
        if quality not in qualities:
            if quality > 720 or quality > 1080:
                quality = 1080
            elif quality > 480:
                quality = 720
            elif quality > 360:
                quality = 480
            elif quality > 240:
                quality = 360
            elif quality > 144:
                quality = 240
            else:
                return []

        quality_index = qualities.index(quality)
        supported_qualities = qualities[:quality_index]
        return supported_qualities

    @classmethod
    def scale_quality(cls, quality):
        if quality > 1080:
            return 1080
        elif quality > 720:
            return 1080
        elif quality > 480:
            return 720
        elif quality > 360:
            return 480
        elif quality > 240:
            return 360
        elif quality > 144:
            return 240
        else:
            return 144
