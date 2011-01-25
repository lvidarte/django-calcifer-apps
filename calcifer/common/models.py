# -*- coding: utf-8 -*-

from PIL import Image
from mimetypes import guess_type

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Tag(models.Model): # {{{
    """Tag model."""
    title = models.CharField(_('title'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True)

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        db_table = 'calcifer_common_tags'
        ordering = ('title',)

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('blog-tag-list', None, {'slug': self.slug})

    def get_total_posts(self):
        from calcifer.blog.models import Post
        return Post.objects.filter(tags__id=self.id).count()
# }}}
class File(models.Model): # {{{
    file = models.FileField(_('file'),
            upload_to='uploads/%Y/%m/%d', max_length=512)
    alt = models.CharField(_('alt'), max_length=256, blank=True)
    size = models.IntegerField(_('size'), blank=True, default=0)
    mime = models.CharField(_('mimetype'), max_length=256, blank=True)
    width = models.IntegerField(_('width'), blank=True, default=0)
    height = models.IntegerField(_('height'), blank=True, default=0)
    is_image = models.BooleanField(_('is image'), blank=True, default=False)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    author = models.ForeignKey(User, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('files')
        db_table  = 'calcifer_common_files'
        ordering  = ('-created',)
        get_latest_by = 'created'

    @models.permalink
    def get_absolute_url(self):
        path = self.file.url[len('uploads/')+1:] # strip 'uploads/'
        return ('blog-uploads', None, {'path': path})

    @models.permalink
    def get_url_wthumb(self, width):
        return ('cache-imgs-w', None, 
                {'width': width, 'url': self.get_absolute_url()})

    @models.permalink
    def get_url_hthumb(self, height):
        return ('cache-imgs-h', None, 
                {'height': height, 'url': self.get_absolute_url()})

    def thumbnail(self):
        if self.is_image:
            return u'<img src="%s" alt="%s" />' % (
                        self.get_url_hthumb(75), self.alt)
        else:
            return u''

    thumbnail.short_description = _('thumbnail')
    thumbnail.allow_tags = True

    def get_size(self):
        if self.size < 1048576: # < 1Mib
            return "%s Kib" % round(self.size / float(1024),1)
        else: # >= 1Mib
            return "%s Mib" % round(self.size / float(1048576),1)

    get_size.short_description = _('size')
    get_size.allow_tags = True

    def save(self, force_insert=False, force_update=False):
        setattr(self, 'size', self.file.size) 
        mime = guess_type(self.file.name)[0]
        setattr(self, 'mime', mime) 

        if mime.split('/')[0] == 'image':
            setattr(self, 'is_image', 1) 
            img = Image.open(self.file)
            width, height = img.size
            setattr(self, 'width', width) 
            setattr(self, 'height', height) 
        else:
            setattr(self, 'is_image', 0) 
            setattr(self, 'width', 0) 
            setattr(self, 'height', 0) 

        super(File, self).save(force_insert, force_update)

    def __unicode__(self):
        return u'%s' % self.file.name
# }}}
