# commands.py
import discord
from utilities import from_register_channel, from_admin, from_right_user, get_help_embed, create_private_channel, generate_user_summary, kick_user, delete_user_channel, get_daily_bet, generate_bet_item, send_bet_message
from config import ADMIN_ID_1, ADMIN_ID_2, GUILD_ID
from database import get_user_table, get_match_table
from user import User
from updator import Updator


def setup_commands(tree, client, events_api):

    @tree.command(name="hello", description="hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(content="hello")

    @tree.command(name="clear", description="Clear all chat history")
    async def clear_chat(interaction: discord.Interaction):
        if interaction.user.id == int(
                ADMIN_ID_1) or interaction.user.id == int(ADMIN_ID_2):
            await interaction.response.send_message(
                content="All messages have been cleared")
            await interaction.channel.purge()
            return

        if from_register_channel(interaction):
            await interaction.response.send_message(
                content='You can only use /register in this channel')
            return

        if not from_right_user(interaction):
            await interaction.response.send_message(
                content='Please go to your channel {0} to use this command'.
                format(interaction.channel.name))
            return
        await interaction.response.send_message(
            content="All messages have been cleared")
        await interaction.channel.purge()

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
                'You already registered a channel with the name of {0} for this account'
                .format(user_entity.channel_name))
            return

        user, user_channel = await create_private_channel(
            client, interaction, user_id, channel_name)
        embed_content = get_help_embed()
        await user_channel.send(content="Welcome {0}!".format(
            user_channel.name),
                                embeds=[embed_content])
        user_entity = User(user.id, user.name, user_channel.id,
                           user_channel.name, 0, 0, 0, 0, {}, 2)
        get_user_table().add_user(user_entity)
        # updator = Updator()
        # updator.update_user_bet_history(user.id)
        await interaction.response.send_message(
            content=
            "Channel {0} is created for {1}. Please go to your right channel in Bet Channels."
            .format(channel_name, user.name))

    @tree.command(name="create", description="Create a new player")
    async def create_player(interaction: discord.Interaction, user_id: str,
                            channel_name: str):
        #user_id = int(user_id)

        if from_admin(interaction):
            guild = client.get_guild(GUILD_ID)
            if guild.get_member(int(user_id)) is None:
                await interaction.response.send_message(
                    content='User with id = {0} does not exist in the server'.
                    format(user_id))
                return

            user_entity = get_user_table().view_user(user_id)
            if user_entity is not None:
                await interaction.response.send_message(
                    content='User with id = {0} already existed'.format(
                        user_id))
            else:
                user, user_channel = await create_private_channel(
                    interaction, user_id, channel_name)
                embed_content = get_help_embed()
                await user_channel.send(content="Welcome {0}!".format(
                    user.name),
                                        embeds=[embed_content])
                user_entity = User(user.id, user.name, user_channel.id,
                                   user_channel.name, 0, 0, 0, 0, {}, 2)
                get_user_table().add_user(user_entity)
                updator = Updator()
                updator.update_user_bet_history(user.id)
                await interaction.response.send_message(
                    content="Channel {0} is created for {1}".format(
                        channel_name, user.name))
        else:
            await interaction.response.send_message(
                content=
                'This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help.'
            )

    @tree.command(name="delete", description="Delete an existing player")
    async def delete_player(interaction: discord.Interaction, user_id: str):
        #user_id = int(user_id)

        #channel_id = interaction.channel_id
        #print("from delete_player", db['user'])
        if from_admin(interaction):

            guild = client.get_guild(GUILD_ID)
            if guild.get_member(int(user_id)) is None:
                await interaction.response.send_message(
                    content='User with id = {0} does not exist in the server'.
                    format(user_id))
                return
            user_channel_id = await kick_user(client, interaction, user_id)
            if user_channel_id:
                await delete_user_channel(client, user_channel_id)
                await interaction.response.send_message(
                    content="User with id = {0} is deleted".format(user_id))

            else:
                await interaction.response.send_message(
                    content="There is no user with id = {0}".format(user_id))
        else:
            await interaction.response.send_message(
                content=
                'This is an admin command. You are not allowed to perform this command! Please use /bet, /me, record, and /help.'
            )

    @tree.command(name="update", description="Update scores")
    async def update_scores(interaction: discord.Interaction):
        if from_admin(interaction):
            await interaction.response.send_message(content="Updating ...")
            updator = Updator()
            updator.update_ended_matches()
            #updator.update_upcoming_matches()
            updator.update_all_user_bet_history()
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
                #print(user.name)
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

    @tree.command(name="bet", description="Choose a betting option")
    async def bet(interaction: discord.Interaction):
      if from_register_channel(interaction):
        await interaction.response.send_message(
          content='You can only use /register in this channel')
        return

      if not from_right_user(interaction):
        await interaction.response.send_message(
          content='Please go to your channel {0} to use this command'.format(
            interaction.channel.name))
        return
      await interaction.response.defer()
      daily_bet = get_daily_bet()

      #await interaction.response.defer()
      user_id = interaction.user.id
      user = get_user_table().view_user(str(user_id))
      user_record = user.to_payload()
      user_bet_history = user_record["history"]

      if len(daily_bet) == 0:
        await interaction.followup.send(content='Hôm nay ko có trận đâu bạn ei')
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

    @tree.command(name="profile", description="Show your record")
    async def view_me(interaction: discord.Interaction):
      if from_register_channel(interaction):
        await interaction.response.send_message(
          content='You can only use /register in this channel')
        return
      if not from_right_user(interaction):
        await interaction.response.send_message(
          content='Please go to your channel {0} to use this command'.format(
            interaction.channel.name))
        return
      user_id = interaction.user.id
      user = get_user_table().view_user(str(user_id))
      user_record = user.to_record()
      embed_content = generate_user_summary(user_record, isOwner=True)

      await interaction.response.send_message(content='', embeds=[embed_content])


    @tree.command(name="record", description="Show all records")
    async def view_all_record(interaction: discord.Interaction):
      if from_register_channel(interaction):
        await interaction.response.send_message(
          content='You can only use /register in this channel')
        return
      if not from_right_user(interaction):
        await interaction.response.send_message(
          content='Please go to your channel {0} to use this command'.format(
            interaction.channel.name))
        return
      user_id = str(interaction.user.id)
      users = get_user_table().view_all()
      user_records = [user.to_record() for user in users]
      user_records = sorted(user_records,
                            key=lambda x: (x.score, x.win, x.draw, -x.loss),
                            reverse=True)
      embed_content = [
        generate_user_summary(record, idx + 1, record.user_id == user_id)
        for idx, record in enumerate(user_records)
      ]
      # How many elements each
      # list should have
      n = 10
      # using list comprehension
      final = [
        embed_content[i * n:(i + 1) * n]
        for i in range((len(embed_content) + n - 1) // n)
      ]
      await interaction.response.send_message(content='Bảng xếp hạng bét thủ')
      for embed_chunk in final:
        await interaction.followup.send(content='', embeds=embed_chunk)

    @tree.command(name="help", description="Show rules and commands")
    async def help(interaction):
      if from_register_channel(interaction):
        await interaction.response.send_message(
          content='You can only use /register in this channel')
        return
      if not from_right_user(interaction):
        await interaction.response.send_message(
          content='Please go to your channel {0} to use this command'.format(
            interaction.channel.name))
        return
      embed_content = get_help_embed()
      await interaction.response.send_message(content='', embeds=[embed_content])