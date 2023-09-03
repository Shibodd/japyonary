from romkan import KANPAT, KANPAT_H

from django.core.management.base import BaseCommand

class Command(BaseCommand):
  def handle(self, *args, **options):
    print(KANPAT)
    print(KANPAT_H)