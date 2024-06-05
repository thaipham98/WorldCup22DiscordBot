import discord
from discord.ui import Button, View
import logging
from utilities import categorize_bids, delete_verify_channel, from_register_channel, from_admin, from_right_user, generate_request_star_modal, generate_star_convert_modal, generate_view_bid_embed_content, generate_view_bid_make_bid_view, generate_view_bid_select_winner_view, get_help_embed, create_private_channel, generate_user_summary, kick_user, delete_user_channel, get_daily_bet, generate_bet_item, send_bet_message, create_verify_private_channel
from config import ADMIN_CHANNEL_ID, ADMIN_ID_1, ADMIN_ID_2, ADMIN_ID_3, GUILD_ID, REGISTER_CHANNEL_ID, VERIFIED_ROLE_ID, UPDATE_CHANNEL_ID
from database import get_bid_table, get_user_table, get_match_table, get_verification_table
from user import User
from updator import Updator
from discord import ButtonStyle

from verification import Verification


def setup_commands(tree, client, events_api):

    @tree.command(name="bet", description="Choose a betting option")
    async def bet(interaction: discord.Interaction):
        if from_register_channel(interaction):
            await interaction.response.send_message(
                content='You can only use /register in this channel')
            return

        if not from_right_user(interaction):
            await interaction.response.send_message(
                content='Please go to your channel {0} to use this command'.
                format(interaction.channel.name))
            return
        await interaction.response.defer()
        daily_bet = get_daily_bet(events_api)

        #await interaction.response.defer()
        user_id = interaction.user.id
        user = get_user_table().view_user(str(user_id))
        user_record = user.to_payload()
        user_bet_history = user_record["history"]

        if len(daily_bet) == 0:
            await interaction.followup.send(
                content='Hôm nay ko có trận đâu bạn ei')
            return
        await interaction.followup.send(content='Các trận hôm nay:')

        for bet_detail in daily_bet:
            match_id = bet_detail.match_id

            match = get_match_table().view_match(str(match_id))
            match_info = match.to_payload()

            user_bet_for_match = user_bet_history[str(match_id)] if str(
                match_id) in user_bet_history.keys() else None
            await send_bet_message(interaction, bet_detail, user_bet_for_match,
                                   match_info)

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

    @tree.command(name="register", description="Register a channel to bet")
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

        user_verification = get_verification_table().view_verification(user_id)

        if user_verification is not None:
            await interaction.response.send_message(
                content=
                "You already sent a register request. Please wait for admin to approve your request"
            )
            return

        user, user_verify_channel = await create_verify_private_channel(
            client, interaction, user_id, channel_name)

        verification_entity = Verification(user_id, channel_name,
                                           user_verify_channel.id, False)
        get_verification_table().add_verification(verification_entity)

        await user_verify_channel.send(
            content=
            f"Hi <@{user.id}>, please attach your proof of money submission here before creating bet channel",
            view=None)

        async def on_button_click(interaction):
            if not interaction.data['custom_id'].startswith("approve___"):
                return

            _, user_id, channel_name = interaction.data['custom_id'].split(
                "___")

            if not from_admin(interaction):
                await interaction.response.send_message(
                    content=
                    "You do not have permission to approve registrations.")
                return

            user_entity = get_user_table().view_user(user_id)
            if user_entity:
                await interaction.response.edit_message(
                    content='User with name = {0} already exists.'.format(
                        user_entity.name),
                    view=None)
                return

            user, user_channel = await create_private_channel(
                client, interaction, user_id, channel_name)
            embed_content = get_help_embed()
            await user_channel.send(content=f"Welcome {user_channel.name}!",
                                    embeds=[embed_content])
            finished_match_count = get_match_table().get_finished_match_count()
            user_entity = User(user.id, user.name, user_channel.id,
                               user_channel.name, 0, 0, 0, 0, {}, 3,
                               finished_match_count, 0)
            get_user_table().add_user(user_entity)
            get_verification_table().verify(user_id)
            guild = interaction.guild
            if user:
                verified_role = guild.get_role(
                    VERIFIED_ROLE_ID
                )  # Replace VERIFIED_ROLE_ID with your role ID
                try:
                    member = await guild.fetch_member(user_id)
                    if verified_role:
                        await member.add_roles(verified_role)

                except Exception as e:
                    await interaction.response.send_message('Member not found',
                                                            ephemeral=True)

            updator = Updator()
            updator.update_user_bet_history(user.id)
            await interaction.response.edit_message(
                content=f'Registration appproved for {user.name}', view=None)
            update_channel = client.get_channel(UPDATE_CHANNEL_ID)
            if not update_channel:
                return
            await update_channel.send(
                content=f"<@{user.id}> has joined the game.", view=None)
            register_channel = client.get_channel(REGISTER_CHANNEL_ID)
            if not register_channel:
                return
            await register_channel.send(
                content=
                f"Hi <@{user.id}>, channel {channel_name} is created. Please go to your right channel in Bet Channels.",
                view=None)

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
                client, interaction, user_id, channel_name)
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
            role = guild.get_role(VERIFIED_ROLE_ID)
            member = await guild.fetch_member(user_id)
            await member.remove_roles(role)

            user_channel_id, verify_channel_id = await kick_user(
                client, interaction, user_id)
            if user_channel_id and verify_channel_id:
                await delete_user_channel(client, user_channel_id)
                await delete_verify_channel(client, verify_channel_id)
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
    @tree.command(name="peek", description="Look at another player's profile")
    async def peek(interaction: discord.Interaction, player: discord.User):
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
            player_entity = get_user_table().view_user(str(player.id))

            if player_entity is None:
                await interaction.response.send_message(
                    content='Làm đ có th này?')
                return
            embed_content = generate_user_summary(player_entity.to_record(),
                                                  isOwner=False)
            await interaction.response.send_message(content='',
                                                    embeds=[embed_content])

        except Exception as e:
            logging.error(f"Error in peek command: {e}")
            await interaction.response.send_message(
                content="An error occurred while peeking players.")

    @tree.command(name="update", description="Update scores")
    async def update_scores(interaction: discord.Interaction):
        if from_admin(interaction):
            await interaction.response.send_message(content="Updating ...")
            updator = Updator()
            await updator.send_match_results(client)
            updator.update_ended_matches()
            updator.update_upcoming_matches()
            updator.update_all_user_bet_history()
            await updator.update_user_reward_hopestar(client)
            await interaction.followup.send(content="Done updating!")
        else:
            await interaction.response.send_message(
                content=
                'This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help'
            )

    @tree.command(name="remind", description="Remind players")
    async def remind_players(interaction: discord.Interaction):
        #channel_id = interaction.channel_id
        if from_admin(interaction):
            users = get_user_table().view_all()
            daily_bet = get_daily_bet(events_api)

            if len(daily_bet) == 0:
                await interaction.response.send_message(
                    "There are not matches today")
                return

            embed_contents = []
            for bet_detail in daily_bet:
                match_id = bet_detail.match_id
                match = get_match_table().view_match(str(match_id))
                match_info = match.to_payload()
                embed_contents.append(generate_bet_item(
                    bet_detail, match_info))

            await interaction.response.send_message(
                content="Reminded all users.")
            for user in users:
                channel = client.get_channel(user.channel_id)  #channel id here
                if channel is not None:
                    await channel.send(
                        "Nhắc nhẹ: Hnay có {0} trận nhé. Mấy ông thần vào /bet hộ cái"
                        .format(len(daily_bet)))
                    for embed in embed_contents:
                        await channel.send(embed=embed)

        else:
            await interaction.response.send_message(
                content=
                'This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help'
            )

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

    @tree.command(name="convert", description="Convert point to star")
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

    @tree.command(name="request_star",
                  description="Request to buy star from someone")
    async def request_star(interaction: discord.Interaction,
                           receiver: discord.User):
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
            receiver_entity = get_user_table().view_user(str(receiver.id))

            if receiver_entity is None:
                await interaction.response.send_message(
                    content='Làm đ có th này?')
                return
            receiver_channel = client.get_channel(receiver_entity.channel_id)
            if receiver_channel is None:
                await interaction.response.send_message(
                    content='Th này làm đ có kênh?')
                return
            request_star_modal = generate_request_star_modal(client=client,
                                                             receiver=receiver)
            await interaction.response.send_modal(request_star_modal)

        except Exception as e:
            logging.error(f"Error in help command: {e}")
            await interaction.response.send_message(
                content="An error occurred while using request_star.")

    @tree.command(name="peek_bid", description="View bid with id")
    async def peek_bid(interaction: discord.Interaction, bid_id: str):
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
            bid_item = get_bid_table().view_bid(str(bid_id))
            if bid_item is None:
                await interaction.response.send_message(
                    content='Làm đ có bid này?')
                return
            embed_content = generate_view_bid_embed_content(bid_item,
                                                            is_receiver=False)
            if embed_content is None:
                await interaction.response.send_message(
                    content='Làm đ có bid này?')
                return
            await interaction.response.send_message(content='',
                                                    embeds=[embed_content])

        except Exception as e:
            logging.error(f"Error in help command: {e}")
            await interaction.response.send_message(
                content="An error occurred while using peek_bid.")

    @tree.command(name="view_bid", description="View bid offers")
    async def view_bid(interaction: discord.Interaction):
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
            # TODO: add logic to view bid
            bids_to_receiver, bids_to_others = categorize_bids(
                str(interaction.user.id))

            if not len(bids_to_receiver) and not len(bids_to_others):
                await interaction.response.send_message(
                    content='There are no bid')
                return

            await interaction.response.send_message(content='Current bids')
            for bid_item in bids_to_receiver:
                embed_content = generate_view_bid_embed_content(
                    bid_item, is_receiver=True)
                if embed_content is None:
                    continue
                await interaction.followup.send(
                    content='',
                    embeds=[embed_content],
                    view=generate_view_bid_select_winner_view(
                        client, bid_item))

            for bid_item in bids_to_others:
                embed_content = generate_view_bid_embed_content(
                    bid_item, is_receiver=False)
                if embed_content is None:
                    continue
                await interaction.followup.send(
                    content='',
                    embeds=[embed_content],
                    view=generate_view_bid_make_bid_view(client, bid_item))

        except Exception as e:
            logging.error(f"Error in help command: {e}")
            await interaction.response.send_message(
                content="An error occurred while using view_bid.")

    @tree.command(name="profile", description="Show your record")
    async def view_me(interaction: discord.Interaction):
        if from_register_channel(interaction):
            await interaction.response.send_message(
                content='You can only use /register in this channel')
            return
        if not from_right_user(interaction):
            await interaction.response.send_message(
                content='Please go to your channel {0} to use this command'.
                format(interaction.channel.name))
            return
        user_id = interaction.user.id
        user = get_user_table().view_user(str(user_id))
        user_record = user.to_record()
        embed_content = generate_user_summary(user_record, isOwner=True)

        await interaction.response.send_message(content='',
                                                embeds=[embed_content])
