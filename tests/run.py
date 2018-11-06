import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

if __name__ == "__main__":
  from django.core.management import execute_from_command_line

  args = sys.argv
  args += ['test', 'test_redis_cache']
  execute_from_command_line(args)
