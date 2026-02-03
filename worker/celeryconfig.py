"""
Celery Beat Schedule Configuration
Automated task scheduling for jobs, courses, and log cleanup
"""

from celery.schedules import crontab

# Celery beat schedule
beat_schedule = {
    # Fetch jobs every 6 hours
    'fetch-jobs-every-6-hours': {
        'task': 'worker.job_tasks.fetch_all_jobs',
        'schedule': crontab(minute=0, hour='*/6'),  # 00:00, 06:00, 12:00, 18:00
        'options': {'expires': 3600}  # Task expires after 1 hour
    },
    
    # Fetch courses every 12 hours
    'fetch-courses-every-12-hours': {
        'task': 'worker.course_tasks.fetch_all_courses',
        'schedule': crontab(minute=0, hour='*/12'),  # 00:00, 12:00
        'options': {'expires': 7200}  # Task expires after 2 hours
    },
    
    # Cleanup old logs daily at 3 AM
    'cleanup-old-logs-daily': {
        'task': 'worker.tasks.cleanup_old_logs',
        'schedule': crontab(hour=3, minute=0),  # 03:00 daily
    },
    
    # Cleanup expired jobs daily at 4 AM (backup to TTL)
    'cleanup-expired-jobs-daily': {
        'task': 'worker.job_tasks.cleanup_expired_jobs',
        'schedule': crontab(hour=4, minute=0),  # 04:00 daily
    },
    
    # Cleanup expired courses daily at 4:30 AM (backup to TTL)
    'cleanup-expired-courses-daily': {
        'task': 'worker.course_tasks.cleanup_expired_courses',
        'schedule': crontab(hour=4, minute=30),  # 04:30 daily
    },
}
