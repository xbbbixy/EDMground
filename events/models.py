from django.db import models
from django.urls import reverse
from genres.models import Genre

class Event(models.Model):
    title = models.CharField(max_length=255,verbose_name="活动标题")
    organizer = models.CharField(max_length=200, blank=True,verbose_name="组织方")
    city = models.CharField(max_length=100, blank=True,verbose_name="城市")
    venue = models.CharField(max_length=200, blank=True,verbose_name="地点")
    start_time = models.DateField(verbose_name="开始时间")
    end_time = models.DateField(null=True, blank=True,verbose_name="结束时间")
    description = models.TextField(blank=True,verbose_name="描述")
    poster = models.ImageField(upload_to='events/posters/', blank=True, null=True,verbose_name="海报")
    ticket_link = models.URLField(blank=True,verbose_name="购票链接")
    is_featured = models.BooleanField(default=False,verbose_name="是否在轮播图显示")
    genres = models.ManyToManyField(Genre, blank=True, related_name='events',verbose_name="曲风")
    price = models.CharField(max_length=100, blank=True,verbose_name="票价")
    purchase_info = models.TextField(blank=True,verbose_name="购票方式说明")

    class Meta:
        verbose_name = "活动"
        verbose_name_plural = "活动"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:detail', args=[str(self.id)])
