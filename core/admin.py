from django.contrib import admin
from .models import Question, Category, Account, Option, Result, Statistics

admin.site.register(Statistics)
admin.site.register(Question)
admin.site.register(Category)
admin.site.register(Option)
admin.site.register(Result)
admin.site.register(Account)

