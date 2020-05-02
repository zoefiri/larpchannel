channel_id = 0
savlim = 4000

sav_json = {};
arcanum = bot.get_channel(channel_id)
async for message in arcanum.history(limit=savlim):
    print(message.content)
    print(message.author.name)
    print(message.attachments)
    sav_json[message.id] = {}
    sav_json[message.id]['content'] = message.content
    sav_json[message.id]['author'] = message.author.name
    sav_json[message.id]['date'] = message.created_at.strftime("%m/%d/%Y, %H:%M:%S")
    sav_json[message.id]['attachments'] = []
    if len(message.attachments) > 0:
        os.mkdir('arcanum/'+str(message.id))
        for attach in message.attachments:
            sav_json[message.id]['attachments'].append(str(attach.id)+attach.filename)
            await attach.save('arcanum/'+str(message.id)+'/'+str(attach.id)+attach.filename, seek_begin=True, use_cached=False)
