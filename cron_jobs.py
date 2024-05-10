# cron_jobs.py
from discord.ext import tasks

def setup_cron_jobs(client):
    @tasks.loop(time=[some_time_variable])
    async def update_odd_cron_job():
        # Implementation here
        pass

    update_odd_cron_job.start()
