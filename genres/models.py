from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True,verbose_name="曲风名")
    slug = models.SlugField(unique=True,verbose_name="标签")
    description = models.TextField(blank=True,verbose_name="描述")

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='subgenres',
        verbose_name="隶属"
    )

    is_featured = models.BooleanField(default=False,verbose_name="是否热门")
    sample_audio = models.FileField(
        upload_to='genres/samples/',
        blank=True,
        null=True,
        verbose_name="音频文件"
    )

    class Meta:
        ordering = ['name']
        verbose_name = "曲风"
        verbose_name_plural = "曲风"

    def __str__(self):
        return self.name
