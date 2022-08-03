"""
Django commands to wait for database to be available

"""
import time
from psycopg2 import OperationalError as PsycopgOpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to wait for DB """

    def handle(self, *args, **options) :
        """Entry point of commands"""
        self.stdout.write("waiting for database ...")
        db_up = False
        while db_up is False:
            try:
                self.check(databases =  ['default'])
                db_up = True
            except (PsycopgOpError , OperationalError):
                self.stdout.write('Database unavailable , waiting 1 sec...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database  available'))
