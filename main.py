from telebot import TeleBot, types
import json

from telebot.types import InlineKeyboardMarkup ,BotCommand

bot = TeleBot('6093650930:AAHjesG87iPoPjcEPJk7BLtjfKU09QOKWf0')


#majburiy obuna uchun funksiya --------------------------
def Checksub(msg):
    with open("data.json", "rb") as f:
        data = json.load(f)
    user = []
    for channel in data["kanallar"]:
        try:

            checkuser = bot.get_chat_member(f"@{channel}", msg.from_user.id).status

            if checkuser in ["member", "administrator", "creator"]:
                continue
            else:
                user.append(channel)
        except:
            bot.send_message(data['ega'],f"{channel} kanalida xatolik bor")

    checksubbtns = types.InlineKeyboardMarkup(row_width=1)
    if len(user) == 1:
        checksubbtns.add(types.InlineKeyboardButton(text=f"{user[0].title()}", url=f"https://t.me/{user[0]}"))
        checksubbtns.add(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="checksub"))
        bot.send_message(msg.from_user.id,"ushbu kanalga obuna bo'lgandan so'ng botni ishlatishingiz mumkin!",reply_markup=checksubbtns)
    elif len(user) > 1:
        for channel in user:
            button = types.InlineKeyboardButton(text=f"{channel.title()}", url=f"https://t.me/{channel}")
            checksubbtns.add(button)
        checksubbtns.add(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="checksub"))
        bot.send_message(msg.from_user.id,"ushbu kanallarga obuna bo'lgandan so'ng botni ishlatishingiz mumkin!",reply_markup=checksubbtns)
    else:
        return True


#nomzodlar va ovolar soni funksiyasi
def vote(msg):
    #nomzodlar malumotlarini fayldan yuklash
    with open("data.json","r") as f:
        data = json.load(f)
        data_nomzodlar = data["nomzodlar"]
        data_ovozlar = data["ovozlar"]
        data_adminlar = data["adminlar"]
    try:
        buttons = types.InlineKeyboardMarkup(row_width=1)

        for k, q in data_nomzodlar.items():
            # admin start bosganida ko'rinadigan tugmalar
            if str(msg.from_user.id) in data_adminlar.keys():
                admin_button = types.InlineKeyboardButton(text="Bot malumotlarini tahrirlash",
                                                          callback_data="edit_info")
                if str(msg.from_user.id) == data["ega"]:
                    ega_button = types.InlineKeyboardButton(text="adminlar", callback_data="edit_admin")
                    buttons.add(ega_button)
                buttons.add(admin_button)
                break
            # oddiy foydalanuvchi start bosganida ovozlarni ko'rsatish
            ovozlar_soni = 0
            for id, ovoz in data_ovozlar.items():
                if q == ovoz:
                    ovozlar_soni += 1
            button = types.InlineKeyboardButton(text=f"{k} - {q} ({ovozlar_soni})" ,callback_data=q)
            buttons.add(button)

        return buttons

    except :
        bot.send_message(data['ega'],"nomzodlarni haqida malumotda xatolik bor")
    #nomzodlar tugmalari malumotlari


def userinfo(msg):
    try:
        with open("data.json","r") as f:
            data = json.load(f)
        user_info = {
            "id": msg.from_user.id,
            "username": msg.from_user.username,
            "premium": msg.from_user.is_premium
        }

        with open('data.json', 'w') as file:
            data["users"][str(msg.from_user.id)] = user_info
            json.dump(data, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"{msg.from_user.username} foydalanuvchisini malumotlarini saqlashni iloji bo'lmadi bo'lmadi: {e}")




commands = [
    BotCommand(command="/start", description="botni ishga tushurish"),
]

bot.set_my_commands(commands)
# Set the commands

@bot.message_handler(commands=['start','help'])
def start_message(msg: types.Message):


    # bot.send_message(
    #     chat_id=-1002117856692,
    #     text="Please vote below:",
    #     reply_markup=vote(msg)
    # )


    with open("data.json","rb") as f:
            data = json.load(f)



    #foydalanuvchi malumotlarini yig'ish
    userinfo(msg)



    user = Checksub(msg)
    if str(msg.from_user.id) in data['adminlar'] or str(msg.from_user.id) == data['ega']:
        with open("img/admin.jpg", "rb") as f:
            img = f
            bot.send_photo(msg.from_user.id,img,caption="Bot admin paneliga xush kelibsiz!",reply_markup=vote(msg))
    else:
        if user:
            with open("img/nomzodlar.jpg","rb")as f:
                img = f
                bot.send_photo(msg.from_user.id, img, caption=data["nomzodlartext"],reply_markup=vote(msg))

@bot.message_handler()
def send_admin(msg: types.Message):
    with open('data.json','rb') as f:
        data = json.load(f)

    # foydalanuvchi malumotlarini yig'ish'
    userinfo(msg)


    if str(msg.from_user.id) in data['adminlar'].keys() or data['ega']:

        if 'yangi' in data['kanallar']:

            username = msg.text

            if not username.startswith("@"):
                username = "@" + username
            try:
                chat = bot.get_chat(username)
                bot.reply_to(msg, f"{chat.title} kanali majburiy obunaga qo'shildi!")
                new_username = username.replace("@", "")
                index = data["kanallar"].index("yangi")
                data["kanallar"][index] = new_username
                with open("data.json", "w") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                bot.reply_to(msg, "Kanal topilmadi yoki xato yuz berdi.")



    #botga admin qo'shish
    if "addadmin" in data["info"]:
        username = msg.text
        if "@" in username:
            username = username.replace("@", "")
        for id, info in data["users"].items():
            if username == info["username"]:
                if username not in data['adminlar'].values():
                    data["adminlar"][str(id)] = info["username"]
                    with open("data.json", "r+") as file:
                        existing_data = json.load(file)
                        existing_data.update(data)
                        file.seek(0)
                        json.dump(existing_data, file, indent=4, ensure_ascii=False)
                        file.truncate()
                    bot.send_message(msg.from_user.id, f"{username} foydalanuvchisi botga admin sifatida qo'shildi",reply_markup=vote(msg))
                else:

                    bot.send_message(msg.from_user.id,  "bu foydalanuvchi allaqachon admin bo'lgan!",
                                       reply_markup=vote(msg))
            else:
                bot.send_message(msg.from_user.id,
                                 "foydalanuvchi botga start berganidan keyingina botga adminlik huquqini olishi mumkin!")
        data["info"].remove("addadmin")
        with open("data.json","w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    data["info"].clear()

    with open("data.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'forward_from', 'forward_from_chat'])
def forward_to_channel(message):
    with open("data.json","rb") as f :
        data = json.load(f)
    # foydalanuvchi malumotlarini yig'ish
    userinfo(message)

    #kanallarga xabar yuborish
    if "send" in data["info"]:
        for kanal in data["kanallar"]:
            try:
                if message.content_type == 'text':
                    bot.send_message(f"@{kanal}", message.text)
                elif message.content_type == 'photo':
                    bot.send_photo(f"@{kanal}", message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video':
                    bot.send_video(f"@{kanal}", message.video.file_id, caption=message.caption)
                elif message.content_type == 'document':
                    bot.send_document(f"@{kanal}", message.document.file_id, caption=message.caption)
            except:
                bot.send_message(data['ega'], f"{kanal} kanaliga  xabar yuborib bo'lmadi ")
        data["info"].remove("send")
        with open("data.json","w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)



    #barcha foydalanuvchilarga xabar yuborish
    elif "senduser" in data["info"]:
        for id,info in data["users"].items():
            users = info['id']
            try:
                if message.content_type == 'text':
                    bot.send_message(users, message.text)
                elif message.content_type == 'photo':
                    bot.send_photo(users, message.photo[-1].file_id, caption=message.caption)
                elif message.content_type == 'video':
                    bot.send_video(users, message.video.file_id, caption=message.caption)
                elif message.content_type == 'document':
                    bot.send_document(users, message.document.file_id, caption=message.caption)
            except:
                pass
        data["info"].remove("senduser")
        with open("data.json","w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)



    #premium foydalanuvchilarga xabar yuborish
    elif "sendpremiumuser" in data["info"]:
        for id,info in data["users"].items():
            if info["premium"]:
                users = str(info['id'])
                try:
                    if message.content_type == 'text':
                        bot.send_message(users, message.text)
                    elif message.content_type == 'photo':
                        bot.send_photo(users, message.photo[-1].file_id, caption=message.caption)
                    elif message.content_type == 'video':
                        bot.send_video(users, message.video.file_id, caption=message.caption)
                    elif message.content_type == 'document':
                        bot.send_document(users, message.document.file_id, caption=message.caption)
                except:
                    pass
    data["info"].clear()
    print(data['info'])
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



@bot.callback_query_handler(func=lambda x: x.data)
def query(msg: types.CallbackQuery):
    # foydalanuvchi malumotlarini yig'ish'
    userinfo(msg)
    with open("data.json","rb") as f:
        data = json.load(f)
    match msg.data:
        case "checksub":
            bot.delete_message(msg.from_user.id, msg.message.id)
            user = Checksub(msg)
            if user:
                with open("img/nomzodlar.jpg", "rb") as f:
                    img = f
                    bot.send_photo(msg.from_user.id, img, caption=data["nomzodlartext"],reply_markup=vote(msg))


        #admin paneli ushun callbacklar------------------------------------------------------------------------------------------------------------
        case "nomzodlar":
            buttons = InlineKeyboardMarkup(row_width=1)
            for k, q in data["nomzodlar"].items():

                # oddiy foydalanuvchi start bosganida ovozlarni ko'rsatish
                ovozlar_soni = 0
                for id, ovoz in data["ovozlar"].items():
                    if q == ovoz:
                        ovozlar_soni += 1
                button = types.InlineKeyboardButton(text=f"{k} - {q} ({ovozlar_soni})",callback_data="admin uchun ovoz berish")
                buttons.add(button)
            with open("img/nomzodlar.jpg","rb") as f:
                img = f
                bot.send_photo(msg.from_user.id, img ,caption=data["nomzodlartext"],reply_markup=buttons)



        #majburiy obunalarga yangi kanal qo'shish

        case "addchannel" :
            if "yangi" not in data["kanallar"]:
                data['kanallar'].append("yangi")
                with open("data.json", "w") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            bot.send_message(msg.from_user.id,"majburiy obuna uchun qo'shmoqchi bo'lgan kanal nomini yuboring masalan @devops_itcenter")

        #majburiy obunadan kanallarni olib tashlash uchun
        case "removechannel" :
            rmbtns = types.InlineKeyboardMarkup(row_width=1)
            for rmchannels in data['kanallar']:
                rmbtn = types.InlineKeyboardButton(text=f"{rmchannels} kanalini majburoy obunadan o'chirish", callback_data=f"remove{rmchannels}")
                rmbtns.add(rmbtn)
            bot.send_message(msg.from_user.id,f"olib tashlanishi kerak bo'lgan kanalni tanlang",reply_markup=rmbtns)


        #kanalga reklama yuborish
        case "reklama":
            bot.send_message(msg.from_user.id,"kanallarga yuboriladigan xabarni yozing")
            if "send" not in data["info"]:
                data["info"].append('send')
                with open("data.json","w") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
        case "senduser":
            bot.send_message(msg.from_user.id, "Foydalanuvchilarga yuboriladigan xabarni yuboring")
            if "senduser" not in data["info"]:
                data["info"].append('senduser')
                with open("data.json","w") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
        case "sendpremiumuser":
            puser = 0
            for k,q in data['users'].items():
                if q['premium']:
                    puser += 1
            bot.send_message(msg.from_user.id, f"Premium Foydalanuvchilarga yuboriladigan xabarni yuboring:\npremium foydalanuvchilar soni: {puser}")
            if "sendpremiumuser" not in data["info"]:
                data["info"].append('sendpremiumuser')
                with open("data.json", "w") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
        case "edit_admin":
            editadminbtn = types.InlineKeyboardMarkup(row_width=1)
            for id,username in data["adminlar"].items():
                editadminbtn.add(types.InlineKeyboardButton(text=f"@{username}",callback_data=f"rm{id}"))
            editadminbtn.add(types.InlineKeyboardButton(text="yangi admin qo'shish",callback_data="addadmin"))
            bot.send_message(msg.from_user.id,"Adminlardan birortasini Adminlikdan olib tashlash uchun admin usernamesi yozilgan qatorni tanlang!\nyangi admin qo'shish uchun yangi admin qatorini tanlang!",reply_markup=editadminbtn)

        case "addadmin":
            bot.send_message(msg.from_user.id,"Adminlikka nomzod profil botga obuna bo'lganini tekshiring va usernamesini yuboring masalan @devopsumarov !")
            data['info'].append("addadmin")
            with open('data.json',"w") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        #ovoz berihsni kanallarga uzatish
        case "votechannel":
            try:
                votechannelbtn = types.InlineKeyboardMarkup(row_width=1)
                for kanal in data['kanallar']:
                    votechannelbtn.add(
                        types.InlineKeyboardButton(text=f"{kanal} kanaliga yuborish", callback_data=f"sendvote{kanal}")
                    )
                votechannelbtn.add(
                    types.InlineKeyboardButton(text="hammasiga", callback_data='sendvote')
                )
                bot.send_message(msg.from_user.id, "qasi kanallarga yuborish kerakligini tanlang",
                                 reply_markup=votechannelbtn)
            except:
                pass


        # majburiy obunadagi barchaga ovoz yig'ish xabarini jo'natish
        case "sendvote":
            for kanal in data["kanallar"]:
                buttons = InlineKeyboardMarkup(row_width=1)
                for k, q in data["nomzodlar"].items():

                    # oddiy foydalanuvchi start bosganida ovozlarni ko'rsatish
                    ovozlar_soni = 0
                    for id, ovoz in data["ovozlar"].items():
                        if q == ovoz:
                            ovozlar_soni += 1
                    button = types.InlineKeyboardButton(text=f"{k} - {q} ({ovozlar_soni})",
                                                        callback_data=q)
                    buttons.add(button)
                with open("img/nomzodlar.jpg", "rb") as f:
                    img = f
                    bot.send_photo(f"@{kanal}", img, caption=data["nomzodlartext"], reply_markup=buttons)

    for kanal in data['kanallar']:
        if msg.data == f"sendvote{kanal}":
            buttons = InlineKeyboardMarkup(row_width=1)
            for k, q in data["nomzodlar"].items():

                # oddiy foydalanuvchi start bosganida ovozlarni ko'rsatish
                ovozlar_soni = 0
                for id, ovoz in data["ovozlar"].items():
                    if q == ovoz:
                        ovozlar_soni += 1
                button = types.InlineKeyboardButton(text=f"{k} - {q} ({ovozlar_soni})",
                                                    callback_data=q)
                buttons.add(button)
            with open("img/nomzodlar.jpg", "rb") as f:
                img = f
                bot.send_photo(f"@{kanal}", img, caption=data["nomzodlartext"], reply_markup=buttons)



    #adminni o'chirish uchun yozilgan
    if str(msg.from_user.id) == data['ega']:
        id = msg.data
        if  msg.data == id:
            id = id.replace("rm","")
            if id in data["adminlar"].keys():
                bot.send_message(msg.from_user.id, f"{data['adminlar'][id]} adminlikdan olib tashlandi")
                del data["adminlar"][id]  # "adminlar" lug'atidan ID'ni o'chirish
                with open('data.json', "r+") as f:
                    file_data = json.load(f)  # Faylni o'qish
                    file_data["adminlar"].pop(id, None)  # Fayldan ID'ni o'chirish
                    f.seek(0)  # Fayl boshiga kursorni qaytarish
                    json.dump(file_data, f, indent=4, ensure_ascii=False)  # Faylni yozish
                    f.truncate()








    #kanallarni o'chirish
    for kanal in data['kanallar']:
        if msg.data ==  f"remove{kanal}":
            data["kanallar"].remove(kanal)
            with open("data.json", "w") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            bot.answer_callback_query(msg.id, text=f"{kanal} kanali majburiy obunadan o'chirildi !")


    #admin paneli uchun malumotlariga kirish
    if msg.data == "edit_info":
        editbtns = types.InlineKeyboardMarkup(row_width=1)
        editbtns.add(
            types.InlineKeyboardButton(text="ovoz yig'ish postini kanalga uzatish",callback_data="votechannel"),
            types.InlineKeyboardButton(text="Majburiy obunaga kanal qo'shish",callback_data="addchannel"),
            types.InlineKeyboardButton(text="Majburiy obunadan kanalni olib tashlash",callback_data="removechannel"),
            types.InlineKeyboardButton(text="Nomzodlar", callback_data="nomzodlar"),
            types.InlineKeyboardButton(text="kanallarga reklama yuborish", callback_data="reklama"),
            types.InlineKeyboardButton(text="botdan foydalanuvchilarga xabar jo'natish",callback_data="senduser"),
            types.InlineKeyboardButton(text="Premium foydalanuvchilarga xabar jo'natish", callback_data="sendpremiumuser"),
        )
        bot.send_message(msg.from_user.id,"bot malumotlarini tahrirlash oynasi faqat adminlar ushun ochiq bo'ladi!",reply_markup=editbtns)





    #foydalanuvchi ovoz berganida yangi ovoz faylga yuklanishiga javob beradi
    if msg.data in data["nomzodlar"].values():
        if str(msg.from_user.id) not in data["ovozlar"].keys():
            bot.answer_callback_query(msg.id,text="ovoz berildi!")
            data["ovozlar"][msg.from_user.id] = msg.data
            with open("data.json","w") as f:
                json.dump(data,f,indent=4,ensure_ascii=False)

            buttons = InlineKeyboardMarkup(row_width=1)
            for k, q in data["nomzodlar"].items():

                # oddiy foydalanuvchi start bosganida ovozlarni ko'rsatish
                ovozlar_soni = 0
                for id, ovoz in data["ovozlar"].items():
                    if q == ovoz:
                        ovozlar_soni += 1
                button = types.InlineKeyboardButton(text=f"{k} - {q} ({ovozlar_soni})",
                                                    callback_data=q)
                buttons.add(button)

            bot.edit_message_reply_markup(
                chat_id=msg.message.chat.id,
                message_id=msg.message.message_id,
                reply_markup=buttons
                )

        else:
            bot.answer_callback_query(msg.id,text="siz allaqachon ovoz berdingiz!")

#botni ishga tushurish
try:
    bot.polling()
except:
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    bot.polling()



