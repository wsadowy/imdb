# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.postgres.fields import JSONField


class Actor(models.Model):
    nconst = models.CharField(max_length=20, primary_key=True, null=False)
    name = models.CharField(max_length=200, null=False)
    birth_year = models.DateField(verbose_name='Year of birth', null=True)
    death_year = models.DateField(verbose_name='Year of death', null=True)
    primary_profession = JSONField()
    movies = models.ManyToManyField('Movie')


class Movie(models.Model):
    tconst = models.CharField(max_length=20, primary_key=True, null=False)
    movie_type = models.CharField(max_length=20, null=False)
    primary_title = models.CharField(max_length=1000, null=False)
    original_title = models.CharField(max_length=1000, null=False)
    is_adult = models.BooleanField()
    start_year = models.DateField(null=True)
    end_year = models.DateField(null=True)
    length = models.IntegerField(verbose_name='Runtime (minutes)', null=True)
    genres = JSONField()
