from django.db import models
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from base.blocks import BaseStreamBlock
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.blocks import (
    CharBlock, TimeBlock, ChoiceBlock, RichTextBlock, ChoiceBlock, StreamBlock, StructBlock, TextBlock, StructValue
)
from collections import defaultdict
from itertools import chain


def merge_schedule(dict1, dict2, merged_dict):
    for k, v in chain(dict1.items(), dict2.items()):
        merged_dict[k].append(v)
        return merged_dict


class ClassIndexPage(RoutablePageMixin, Page):
    intro = StreamField(
        BaseStreamBlock(), verbose_name="Introduction to Trainings", blank=True
    )
    content_panels = Page.content_panels + [
        StreamFieldPanel('intro')
    ]
    # Allows child objects (e.g. BreadPage objects) to be accessible via the
    # template. We use this on the HomePage to display child items of featured
    # content
    def get_trainings(self):
        return TrainingPage.objects.descendant_of(self).live()

    def children(self):
        return self.get_children().specific().live()

    def get_context(self, request, *args, **kwargs):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(ClassIndexPage, self).get_context(request, *args, **kwargs)
        context['class_index_page'] = self
        context['training_pages'] = self.training_pages
        return context

    @route(r'^category/(?P<category>[-\w]+)/$')
    def training_by_category(self, request, category, *args, **kwargs):
        self.search_type = 'category'
        self.search_term = category
        self.training_pages = self.get_trainings().filter(categories__slug=category)
        return Page.serve(self, request, *args, **kwargs)

    @route(r'^$')
    def training_list(self, request, *args, **kwargs):
        self.training_pages = self.get_trainings()
        return Page.serve(self, request, *args, **kwargs)


class ScheduleStructValue(StructValue):

   ''' def session_times(self):
        return self.get('times').split(';')

    def session_day(self):
        self.get('day')
        return self.get('day')
    '''

class ScheduleBlock(StructBlock):
    day = ChoiceBlock(choices=[('MONDAY', 'Monday'),
                                ('TUESDAY', 'Tuesday'),
                                ('WEDNESDAY', 'Wednesday'),
                                ('THURSDAY', 'Thursday'),
                                ('FRIDAY', 'Friday'),
                                ('SATURDAY', 'Saturday')])
    times = CharBlock()
    category = CharBlock(required=False)

    class Meta:
        icon = 'fa-calendar'
        label = 'ScheduleStructBlock'
        value_class = ScheduleStructValue


class TrainingPage(Page):
    sub_title = models.CharField(max_length=100, blank=True, null=True)
    intro = models.CharField(max_length=250)
    body = StreamField(
        BaseStreamBlock(), verbose_name="Training Body", blank=True)
    schedule = StreamField([('schedule', ScheduleBlock())], verbose_name="Training Schedule", blank=True)
    header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        FieldPanel('sub_title'),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('schedule')
    ]

    def get_schedule(self):
        return self.schedule

    def get_schedule_1(self):
        result = {}
        for day in {'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'}:
            result[day] = self.get_schedule_per_day(day)
        return result

    def get_schedule_per_day(self, day):
        day_schedule = defaultdict(list)
        for block in self.schedule:
            x = block.value
            if x.get('day') == day:
                times = x.get('times').split(';')
                category = x.get('category')
                a = dict((time, category) for time in times)
                for key, val in a.items():
                    day_schedule[key].append(val)
        return dict(day_schedule)
