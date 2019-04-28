import StringIO
import csv
import datetime
import os

import requests
import gzip

from itertools import islice, chain

from django.core.management import BaseCommand

from rest_api.models import Movie, Actor


def split(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.next()], batchiter)


class Command(BaseCommand):

    main_url = 'https://www.dropbox.com/s'
    movies_url = os.path.join(main_url, '3do9bu0awq048uh/title.basics.tsv.gz?dl=1')
    actors_url = os.path.join(main_url, 'xaidig3yw2viyym/name.basics.tsv.gz?dl=1')
    all_movie_ids = None
    through_model = None
    MOVIES_FILE_NAME = 'movies.tsv'
    ACTORS_FILE_NAME = 'actors.tsv'
    BATCH_SIZE = 10000

    def handle(self, *args, **options):
        # self.import_data(self.movies_url, self.MOVIES_FILE_NAME)
        # self.import_data(self.actors_url, self.ACTORS_FILE_NAME)
        self.populate_actors()

    @staticmethod
    def import_data(url, fname):
        response = requests.get(url).content
        zipped = StringIO.StringIO(response)
        unzipped = gzip.GzipFile(fileobj=zipped)

        with open(fname, 'w') as outfile:
            outfile.write(unzipped.read())

    @staticmethod
    def __populate_movies(batch, num):
        bulked = []
        for row in batch:
            try:
                movie = Movie(
                    genres=row[8].split(','),
                    length=None if row[7] == '\\N' else int(row[7]),
                    end_year=None if row[6] == '\\N' else datetime.date(year=int(row[6]), month=1, day=1),
                    start_year=None if row[5] == '\\N' else datetime.date(year=int(row[5]), month=1, day=1),
                    is_adult=bool(row[4]),
                    original_title=row[3],
                    primary_title=row[2],
                    movie_type=row[1],
                    tconst=row[0]
                )
                bulked.append(movie)
            except IndexError:
                pass
                # At least one row is improperly formatted and contains columns
                # with unescaped and unpaired double quote characters
        Movie.objects.bulk_create(bulked)
        print 'Batch {} created'.format(num)

    def __populate_actors(self, batch, num):
        bulked_actors = []
        bulked_actor_movies = []
        for row in batch:
            try:
                actor = Actor(
                    primary_profession=row[4],
                    death_year=None if row[3] == '\\N' else datetime.date(year=int(row[3]), month=1, day=1),
                    birth_year=None if row[2] == '\\N' else datetime.date(year=int(row[2]), month=1, day=1),
                    name=row[1],
                    nconst=row[0]
                )
                bulked_actors.append(actor)
                actor_movie_ids = set(row[5].split(','))
                bulked_actor_movies.extend([self.through_model(actor_id=row[0],
                                                               movie_id=movie_id)
                                            for movie_id in actor_movie_ids & self.all_movie_ids])
            except IndexError:
                pass
                # Just in case some rows are improperly formatted, like single unescaped quotations etc
        # with transaction.atomic():
        Actor.objects.bulk_create(bulked_actors)
        self.through_model.objects.bulk_create(bulked_actor_movies)
        print 'Batch {} created'.format(num)

    def _populate(self, fname):
        if fname == self.MOVIES_FILE_NAME:
            method = self.__populate_movies
        elif fname == self.ACTORS_FILE_NAME:
            method = self.__populate_actors
            self.through_model = Actor.movies.through
            self.all_movie_ids = set(Movie.objects.values_list('tconst', flat=True))
        else:
            raise AttributeError("Incorrect filename provided")

        with open(fname) as infile:
            reader = csv.reader(infile, delimiter='\t')
            reader.next()
            for num, batch in enumerate(split(reader, self.BATCH_SIZE), start=1):
                method(batch, num)

    def populate_movies(self):
        self._populate(self.MOVIES_FILE_NAME)

    def populate_actors(self):
        self._populate(self.ACTORS_FILE_NAME)
