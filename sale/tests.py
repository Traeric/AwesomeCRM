from django.test import TestCase

# Create your tests here.

import subprocess
import os
BAES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.chdir(BAES_DIR)

res = subprocess.call("python manage.py createsuperuser --username=Tom --email=2789519045@qq.com")

print(res)


