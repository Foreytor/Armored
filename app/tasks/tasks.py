import re
import sys
import os
from .models import *
from celery import shared_task


@shared_task
def myName():
    return false


if __name__ == '__main__':
    pass
