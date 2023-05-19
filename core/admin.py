from django.contrib import admin
from .models import Question, Category, Option, Quizz

admin.site.register(Category)
admin.site.register(Quizz)


class AnswerInLineModel(admin.TabularInline):
    model = Option
    fields = ['title', 'is_true']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'category', 'level']
    inlines = [AnswerInLineModel]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'title', 'is_true']

