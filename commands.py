import discord
from discord.ui import Button, View
import logging
from utilities import from_register_channel, from_admin, from_right_user, generate_star_convert_modal, get_help_embed, create_private_channel, generate_user_summary, kick_user, delete_user_channel, get_daily_bet, generate_bet_item, send_bet_message
from config import ADMIN_CHANNEL_ID, ADMIN_ID_1, ADMIN_ID_2, ADMIN_ID_3, GUILD_ID
from database import get_user_table, get_match_table
from user import User
from updator import Updator
from discord import ButtonStyle


def setup_commands(tree, client, events_api):

    @tree.command(name="clear", description="Clear all chat history")
    async def clear_chat(interaction: discord.Interaction):
        try:
            if interaction.user.id in (int(ADMIN_ID_1), int(ADMIN_ID_2),
                                       int(ADMIN_ID_3)):
                await interaction.response.send_message(
                    content="All messages have been cleared")
                await interaction.channel.purge()
            elif from_register_channel(interaction):
                await interaction.response.send_message(
                    content='You can only use /register in this channel')
            elif not from_right_user(interaction):
                await interaction.response.send_message(
                    content='Please go to your channel {0} to use this command'
                    .format(interaction.channel.name))
            else:
                await interaction.response.send_message(
                    content="All messages have been cleared")
                await interaction.channel.purge()
        except Exception as e:
            logging.error(f"Error in clear_chat command: {e}")
            await interaction.response.send_message(
                content="Failed to clear chat due to an error.")

    @tree.command(name="register", description="Register")
    async def register_player(interaction: discord.Interaction,
                              channel_name: str):
        if not from_register_channel(interaction):
            await interaction.response.send_message(
                content="Please go to Welcome/register channel to register")
            return

        user_id = str(interaction.user.id)
        user_entity = get_user_table().view_user(user_id)
        if user_entity is not None:
            await interaction.response.send_message(
                content=
                f'You already registered a channel with the name of {user_entity.channel_name} for this account'
            )
            return

        async def on_button_click(interaction):
            if interaction.data['custom_id'].startswith("approve___"):
                _, user_id, channel_name = interaction.data['custom_id'].split(
                    "___")

                if from_admin(interaction):
                    user, user_channel = await create_private_channel(
                        client, interaction, user_id, channel_name)
                    embed_content = get_help_embed()
                    await user_channel.send(
                        content=f"Welcome {user_channel.name}!",
                        embeds=[embed_content])
                    finished_match_count = get_match_table(
                    ).get_finished_match_count()
                    user_entity = User(user.id, user.name, user_channel.id,
                                       user_channel.name, 0, 0, 0, 0, {}, 2,
                                       finished_match_count, 0)
                    get_user_table().add_user(user_entity)
                    # updator = Updator()
                    # updator.update_user_bet_history(user.id)
                    await interaction.response.edit_message(
                        content=
                        f"Channel {channel_name} is created for {user.name}. Please go to your right channel in Bet Channels.",
                        view=None)
                else:
                    await interaction.response.send_message(
                        content=
                        "You do not have permission to approve registrations.")

        admin_channel = client.get_channel(ADMIN_CHANNEL_ID)

        if not admin_channel:
            await interaction.response.send_message(
                content=
                "Admin channel not found. Please contact the server administrators."
            )
            return
        try:
            # Send registration request to admin channel with button for approval
            approval_button = Button(
                style=ButtonStyle.green,
                label="Approve",
                custom_id=f"approve___{user_id}___{channel_name}")
            view = View(timeout=None)
            approval_button.callback = on_button_click
            view.add_item(approval_button)
            await admin_channel.send(
                content=
                f"New registration request from user {interaction.user.name} for creating channel: {channel_name}",
                view=view)
            await interaction.response.send_message(
                content=
                "Your registration request has been sent to the admins for approval. Please wait for confirmation."
            )
        except discord.errors.Forbidden:
            await interaction.response.send_message(
                content=
                "Bot does not have permission to send messages in the admin channel."
            )
        except Exception as e:
            await interaction.response.send_message(
                content=
                f"An error occurred while sending the registration request: {e}"
            )

    @tree.command(name="create", description="Create a new player")
    async def create_player(interaction: discord.Interaction, user_id: str,
                            channel_name: str):
        try:
            if not from_admin(interaction):
                await interaction.response.send_message(
                    content=
                    'This is an admin command. You are not allowed to perform this command.'
                )
                return

            guild = client.get_guild(GUILD_ID)
            if not guild.get_member(int(user_id)):
                await interaction.response.send_message(
                    content='User with id = {0} does not exist in the server.'.
                    format(user_id))
                return

            user_entity = get_user_table().view_user(user_id)
            if user_entity:
                await interaction.response.send_message(
                    content='User with id = {0} already exists.'.format(
                        user_id))
                return

            user, user_channel = await create_private_channel(
                interaction, user_id, channel_name)
            embed_content = get_help_embed()
            await user_channel.send(content="Welcome {0}!".format(user.name),
                                    embeds=[embed_content])
            finished_match_count = get_match_table().get_finished_match_count()
            user_entity = User(user.id, user.name, user_channel.id,
                               user_channel.name, 0, 0, 0, 0, {}, 2,
                               finished_match_count, 0)
            get_user_table().add_user(user_entity)
            updator = Updator()
            updator.update_user_bet_history(user.id)
            await interaction.response.send_message(
                content="Channel {0} is created for {1}".format(
                    channel_name, user.name))
        except Exception as e:
            logging.error(f"Error in create_player command: {e}")
            await interaction.response.send_message(
                content="An error occurred while creating a new player.")

    @tree.command(name="delete", description="Delete an existing player")
    async def delete_player(interaction: discord.Interaction, user_id: str):
        try:
            if not from_admin(interaction):
                await interaction.response.send_message(
                    content=
                    'This is an admin command. You are not allowed to perform this command.'
                )
                return

            guild = client.get_guild(GUILD_ID)
            if not guild.get_member(int(user_id)):
                await interaction.response.send_message(
                    content='User with id = {0} does not exist in the server.'.
                    format(user_id))
                return

            user_channel_id = await kick_user(client, interaction, user_id)
            if user_channel_id:
                await delete_user_channel(client, user_channel_id)
                await interaction.response.send_message(
                    content="User with id = {0} has been deleted.".format(
                        user_id))
            else:
                await interaction.response.send_message(
                    content="There is no user with id = {0}.".format(user_id))
        except Exception as e:
            logging.error(f"Error in delete_player command: {e}")
            await interaction.response.send_message(
                content="An error occurred while deleting a player.")

    # Additional command implementations should continue in a similar pattern with try-except blocks around their core logic.

    # Remember to log important events and catch exceptions to handle them gracefully, providing feedback to the user when something goes wrong.
    @tree.command(name="update", description="Update scores")
    async def update_scores(interaction: discord.Interaction):
        try:
            if not from_admin(interaction):
                await interaction.response.send_message(
                    content=
                    'This is an admin command. You are not allowed to perform this command.'
                )
                return

            updator = Updator()
            updator.update_ended_matches()
            updator.update_all_user_bet_history()
            updator.update_user_reward_hopestar()
            await interaction.followup.send(
                content="Scores updated successfully!")
        except Exception as e:
            logging.error(f"Error in update_scores command: {e}")
            await interaction.response.send_message(
                content="An error occurred while updating scores.")

    @tree.command(name="remind", description="Remind players")
    async def remind_players(interaction: discord.Interaction):
        try:
            if not from_admin(interaction):
                await interaction.response.send_message(
                    content=
                    'This is an admin command. You are not allowed to perform this command.'
                )
                return

            users = get_user_table().view_all()
            daily_bet = get_daily_bet(events_api)
            if not daily_bet:
                await interaction.response.send_message(
                    content="No matches today.")
                return

            embed_contents = [
                generate_bet_item(
                    bet_detail,
                    get_match_table().view_match(str(
                        bet_detail.match_id)).to_payload())
                for bet_detail in daily_bet
            ]
            await interaction.response.send_message(
                content="Reminded all users.")
            for user in users:
                channel = client.get_channel(user.channel_id)
                if channel:
                    await channel.send(
                        content=
                        f"Reminder: There are {len(daily_bet)} matches today. Please place your bets."
                    )
                    for embed in embed_contents:
                        await channel.send(embed=embed)
        except Exception as e:
            logging.error(f"Error in remind_players command: {e}")
            await interaction.response.send_message(
                content="An error occurred while reminding players.")

    @tree.command(name="bet", description="Choose a betting option")
    async def bet(interaction: discord.Interaction):
        try:
            if from_register_channel(interaction):
                await interaction.response.send_message(
                    content='You can only use /register in this channel.')
                return

            if not from_right_user(interaction):
                await interaction.response.send_message(
                    content='Please go to your channel {0} to use this command.'
                    .format(interaction.channel.name))
                return

            daily_bet = get_daily_bet(events_api)
            if not daily_bet:
                await interaction.followup.send(
                    content='No matches to bet on today.')
                return

            await interaction.response.defer()
            user_id = str(interaction.user.id)
            user = get_user_table().view_user(user_id)
            user_bet_history = user.history if user else {}

            await interaction.followup.send(content='Today\'s matches:')
            for bet_detail in daily_bet:
                match_info = get_match_table().view_match(
                    str(bet_detail.match_id)).to_payload()
                user_bet_for_match = user_bet_history.get(str(match_id))
                await send_bet_message(interaction, bet_detail,
                                       user_bet_for_match, match_info)
        except Exception as e:
            logging.error(f"Error in bet command: {e}")
            await interaction.followup.send(
                content="An error occurred while processing bets.")

    @tree.command(name="profile", description="Show your record")
    async def view_me(interaction: discord.Interaction):
        try:
            if from_register_channel(interaction):
                await interaction.response.send_message(
                    content='You can only use /register in this channel.')
                return

            if not from_right_user(interaction):
                await interaction.response.send_message(
                    content='Please go to your channel {0} to use this command.'
                    .format(interaction.channel.name))
                return

            user_id = str(interaction.user.id)
            user = get_user_table().view_user(user_id)
            if not user:
                await interaction.response.send_message(
                    content="No user record found.")
                return

            embed_content = generate_user_summary(user.to_record(),
                                                  isOwner=True)
            await interaction.response.send_message(content='',
                                                    embeds=[embed_content])
        except Exception as e:
            logging.error(f"Error in profile command: {e}")
            await interaction.response.send_message(
                content="An error occurred while fetching your profile.")

    @tree.command(name="record", description="Show all records")
    async def view_all_record(interaction: discord.Interaction):
        try:
            if from_register_channel(interaction):
                await interaction.response.send_message(
                    content='You can only use /register in this channel.')
                return

            if not from_right_user(interaction):
                await interaction.response.send_message(
                    content='Please go to your channel {0} to use this command.'
                    .format(interaction.channel.name))
                return

            users = get_user_table().view_all()
            user_records = [user.to_record() for user in users]
            sorted_records = sorted(user_records,
                                    key=lambda x:
                                    (x.score, x.win, x.draw, -x.loss),
                                    reverse=True)

            embeds = [
                generate_user_summary(
                    record, idx + 1,
                    record.user_id == str(interaction.user.id))
                for idx, record in enumerate(sorted_records)
            ]
            await interaction.response.send_message(content='Player rankings:')
            for embed in embeds:
                await interaction.followup.send(content='', embeds=[embed])
        except Exception as e:
            logging.error(f"Error in record command: {e}")
            await interaction.response.send_message(
                content="An error occurred while displaying records.")

    @tree.command(name="help", description="Show rules and commands")
    async def help(interaction: discord.Interaction):
        try:
            if from_register_channel(interaction):
                await interaction.response.send_message(
                    content='You can only use /register in this channel.')
                return

            if not from_right_user(interaction):
                await interaction.response.send_message(
                    content='Please go to your channel {0} to use this command.'
                    .format(interaction.channel.name))
                return

            embed_content = get_help_embed()
            await interaction.response.send_message(content='',
                                                    embeds=[embed_content])
        except Exception as e:
            logging.error(f"Error in help command: {e}")
            await interaction.response.send_message(
                content="An error occurred while providing help.")

    @tree.command(name="convert",
                  description="Convert point to star, 7k5 each")
    async def convert(interaction: discord.Interaction):
        try:
            if from_register_channel(interaction):
                await interaction.response.send_message(
                    content='You can only use /register in this channel.')
                return

            if not from_right_user(interaction):
                await interaction.response.send_message(
                    content='Please go to your channel {0} to use this command.'
                    .format(interaction.channel.name))
                return

            user_id = str(interaction.user.id)
            user = get_user_table().view_user(user_id)
            if not user:
                await interaction.response.send_message(
                    content="No user record found.")
                return

            user_current_score = user.score
            convert_modal = generate_star_convert_modal(user_current_score)
            await interaction.response.send_modal(convert_modal)

        except Exception as e:
            logging.error(f"Error in help command: {e}")
            await interaction.response.send_message(
                content="An error occurred while using convert.")
