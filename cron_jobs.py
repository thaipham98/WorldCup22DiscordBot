# cron_jobs.py
from discord.ext import tasks
from config import LEADERBOARD_CHANNEL_ID, LEADERBOARD_MESSAGE_ID
from database import get_user_table
from replit import db
def setup_cron_jobs(client):
    # @tasks.loop(time=[some_time_variable])
    # async def update_odd_cron_job():
    #     # Implementation here
    #     pass

    # update_odd_cron_job.start()

    # Task to update the leaderboard message
    @tasks.loop(minutes=60)  # Adjust the interval as needed
    async def update_leaderboard():

        global LEADERBOARD_MESSAGE_ID
        channel = client.get_channel(int(LEADERBOARD_CHANNEL_ID))
        if channel is None:
            print("Leaderboard channel not found")
            return

        # Get all users from the Replit database
        users = db['user']
        # Create a list of tuples (user_id, name, score)
        user_list = [(user_id, user_info['name'], user_info['score']) for user_id, user_info in users.items()]
        # Sort the list by score in descending order
        sorted_users = sorted(user_list, key=lambda x: x[2], reverse=True)

        # Create the leaderboard table string
        leaderboard_table = "Leaderboard:\n"
        for i, (user_id, name, score) in enumerate(sorted_users, 1):
            leaderboard_table += f"{i}. {name} - {score} points\n"
    
        if LEADERBOARD_MESSAGE_ID is None:
            # Send a new message if we don't have a message ID stored
            message = await channel.send(leaderboard_table)
            LEADERBOARD_MESSAGE_ID = message.id
        else:
            try:
                # Try to fetch the existing message
                message = await channel.fetch_message(LEADERBOARD_MESSAGE_ID)
                await message.edit(content=leaderboard_table)
            except discord.NotFound:
                # If the message was deleted, send a new one
                message = await channel.send(leaderboard_table)
                LEADERBOARD_MESSAGE_ID = message.id
    update_leaderboard.start()


