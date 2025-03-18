import os
import django
import redis
from django.conf import settings

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HRMS.settings")
# Initialize Django
django.setup()

def clear_cache():
    """Clears all cached data from Redis."""
    try:
        redis_client = redis.Redis.from_url(settings.CACHES['default']['LOCATION'])
        redis_client.flushall()
        print("✅ Cache cleared successfully!")
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")

if __name__ == "__main__":
    clear_cache()
