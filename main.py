import telebot
import sqlite3
import json
import random
import task_list
import datetime

bot = telebot.TeleBot('')

profile_button = telebot.types.KeyboardButton('/profile')
profile_button.text = 'Профиль'

test_button = telebot.types.KeyboardButton('/test')
test_button.text = 'Тест'

test_variant_button = telebot.types.KeyboardButton('/test_variant')
test_variant_button.text = 'Тренировочный вариант'

keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard.row(test_button)
keyboard.row(test_variant_button)
keyboard.row(profile_button)

continue_button = telebot.types.KeyboardButton('/continue')
continue_button.text = 'Продолжить'
finish_button = telebot.types.KeyboardButton('/finish')
finish_button.text = 'Завершить'

test_keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
test_keyboard.row(continue_button)
test_keyboard.row(finish_button)

cancel_button = telebot.types.KeyboardButton('/cancel')
cancel_button.text = 'Назад'
cancel_keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
cancel_keyboard.row(cancel_button)

tasks = task_list.task_list_()
tasks = tasks.task_list

test_variant_keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
test_variant_keyboard.row(continue_button)
test_variant_keyboard.row(cancel_button)
test_variant_keyboard.row(finish_button)

first_task_test = telebot.types.ReplyKeyboardMarkup(True, True)
first_task_test.row(continue_button)
first_task_test.row(finish_button)

last_task_test = telebot.types.ReplyKeyboardMarkup(True, True)
last_task_test.row(cancel_button)
last_task_test.row(finish_button)

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
score_for_task = [1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2]
actual_score_for_task = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 42, 44, 45, 46, 47, 48, 49]

score_interval = [50, 80]
def generate_task(message, num):
    task_num = random.randint(0, len(tasks[num - 1]) - 1)
    task = tasks[num - 1][task_num]["text"] 
    bot.send_message(message.from_user.id, task, reply_markup=test_keyboard)
   
    c.execute("UPDATE users SET state = 2 WHERE user_id = ?", (str(message.from_user.id),))
    conn.commit()
 
    print("Пользователь " + str(message.from_user.username) + " id: " + str(message.from_user.id)  + " получил задание №" + str(num))
    
    log_file = open('log.txt', 'a')
    dtn = datetime.datetime.now()
    log_file.write(dtn.strftime("%d-%m-%Y %H:%M") + " Пользователь " + str(message.from_user.username) + " получил задание №" + str(num) + "\n")
    log_file.close()
    
    c.execute("UPDATE users SET task_number = ? WHERE user_id = ?", (str(num), str(message.from_user.id)))
    conn.commit()
    c.execute("UPDATE users SET task_question = ? WHERE user_id = ?", (str(task_num), str(message.from_user.id)))
    conn.commit()

    print("Ответ: " + tasks[num-1][task_num]["answer"])
    
    log_file = open('log.txt', 'a')
    dtn = datetime.datetime.now()
    log_file.write(dtn.strftime("%d-%m-%Y %H:%M") + " Правильный ответ: " + tasks[num-1][task_num]["answer"] + "\n")
    log_file.close()


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    c.execute("SELECT * FROM users WHERE user_id = ?", (str(message.from_user.id),))
    if message.text == "/start":   
        if c.fetchone() is not None:        
            state = c.execute("SELECT state FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
            keyboard_start = keyboard
            if state == 0:
                keyboard_start = keyboard
            if state == 1:
                keyboard_start = test_keyboard
            if state == 2:
                keyboard_start = test_keyboard
            if state == 3:
                keyboard_start = test_variant_keyboard
            
            bot.send_message(message.from_user.id, "Привет, я бот для подготовки к ЕГЭ по обществознанию.", reply_markup=keyboard_start)  
        else:
            bot.send_message(message.from_user.id, "Привет, я бот для подготовки к ЕГЭ по обществознанию.", reply_markup=keyboard)  

    if c.fetchone() is None:
        text = open('score.json', 'r').read() 
        c.execute("INSERT INTO users (user_id, username, test_score, state, task_number, task_question) VALUES (?, ?, ?, ?, ?, ?)", (str(message.from_user.id), str(message.from_user.username), text, 0, 0, 0))
        conn.commit() 
        print("Пользователь " + str(message.from_user.username) + " id: " + str(message.from_user.id)  + " добавлен в базу данных")
        
        log_file = open('log.txt', 'a')
        dtn = datetime.datetime.now()
        log_file.write(dtn.strftime("%d-%m-%Y %H:%M") + " Пользователь " + str(message.from_user.username) + " добавлен в базу данных\n")
        log_file.close()
        return
    if message.text.startswith("Тест"):  
        state = c.execute("SELECT state FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
        if state == 0:           
            bot.send_message(message.from_user.id, "Введите номер задания от 1 до 16", reply_markup=cancel_keyboard)   
            c.execute("UPDATE users SET state = 1 WHERE user_id = ?", (str(message.from_user.id),))
            conn.commit()
        else: 
            return
    elif message.text == "Профиль":
        state = c.execute("SELECT state FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
        if state != 0:
            return
        c.execute("SELECT * FROM users WHERE user_id = ?", (str(message.from_user.id),))
        data = c.fetchone()
        statistic = json.loads(data[3])["task_list"]
        stat_msg = data[2] + ", ваша статистика: \n\n"
        for i in range(1,17):    
            stat_msg += "*Задание №" + str(i) + ":*\n"
            if(statistic[str(i)]["total_answers"] == 0):
                stat_msg += "Вы еще не решали данное задание\n\n"
            else:
                stat_msg += "Правильно решено: " + str(statistic[str(i)]["right_answers"]) + "\n"
                stat_msg += "Всего решено: " + str(statistic[str(i)]["total_answers"]) + "\n"
                percent = statistic[str(i)]["right_answers"] / statistic[str(i)]["total_answers"] * 100
                per_str = str(format(float(percent), '.2f'))

                stat_msg += "Процент правильных ответов: " + per_str + "%"

                if percent < score_interval[0]:
                    stat_msg += "❌\nСтоит уделить больше внимания данному заданию\n\n"
                elif percent < score_interval[1]:
                    stat_msg += "⚠️\nСтоит продолжать работать над решением данного задания\n\n"
                else:
                    stat_msg += "✅\nОтлично! Вы хорошо справляетесь с данным заданием\n\n"
           
        
        bot.send_message(message.from_user.id, stat_msg, parse_mode="Markdown", reply_markup=keyboard)

        print("Пользователь " + str(message.from_user.username) + " id: " + str(message.from_user.id)  + " открыл профиль")
        print("Его статистика: ", statistic)
        
        log_file = open('log.txt', 'a')
        dtn = datetime.datetime.now()
        log_file.write(dtn.strftime("%d-%m-%Y %H:%M") + " Пользователь " + str(message.from_user.username)  + " открыл профиль\n")
        log_file.write("Его статистика: " + str(statistic) + "\n")
        log_file.close()

    elif message.text == "Продолжить":        
        state = c.execute("SELECT state FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
        if state == 2:
            num = c.execute("SELECT task_number FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
            generate_task(message, num)
        elif state == 3:
            num = c.execute("SELECT task_number FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
            if num == 16:
                return

            c.execute("UPDATE users SET task_number = ? WHERE user_id = ?", (str(num + 1), str(message.from_user.id)))
            conn.commit()

            num += 1
            
            test_var_tasks = c.execute("SELECT test_var_tasks FROM users WHERE user_id = ?", (str(message.from_user.id),))
            test_var_tasks = test_var_tasks.fetchone()[0]
            test_var_tasks = json.loads(test_var_tasks)
            task = test_var_tasks[str(num)]
            task_text = "*Задание №" + str(num) + ":*\n" + task["text"] + "\n"

            keyboard_ = test_variant_keyboard

            if(num == 1):
                keyboard_ = first_task_test
            elif(num == 16):
                keyboard_ = last_task_test

            bot.send_message(message.from_user.id, task_text, parse_mode="Markdown", reply_markup=keyboard_)    
            
            if task["user_answer"] != "":
                bot.send_message(message.from_user.id, "*Ваш ответ: " + task["user_answer"] + "*\n", parse_mode="Markdown")

        else:  
            return

    elif message.text == "Завершить":        
        state = c.execute("SELECT state FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
        if state == 2:
            c.execute("UPDATE users SET state = 0 WHERE user_id = ?", (str(message.from_user.id),))
            conn.commit()
            c.execute("SELECT task_question FROM users WHERE user_id = ?", (str(message.from_user.id),))
            num = c.fetchone()[0]
            if num != -1:
                task_num = c.execute("SELECT task_number FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
                bot.send_message(message.from_user.id, "*Вы не решили текущее задание!*", parse_mode = "Markdown", reply_markup=keyboard)
                bot.send_message(message.from_user.id, "*Пояснение:* " + tasks[int(task_num)-1][int(num)]["explanation"], parse_mode = "Markdown")
                bot.send_message(message.from_user.id, "*Ответ:* " + tasks[int(task_num)-1][int(num)]["answer"], parse_mode = "Markdown")
                
                temp_test_score = c.execute("SELECT test_score FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
                temp_test_score = json.loads(temp_test_score)
                test_score = temp_test_score["task_list"]
                right_answers = test_score[str(task_num)]["right_answers"]
                right_answers = int(right_answers)
                total_answers = test_score[str(task_num)]["total_answers"]
                total_answers = int(total_answers) + 1
                test_score[str(task_num)]["right_answers"] = right_answers
                test_score[str(task_num)]["total_answers"] = total_answers
               
                temp_test_score["task_list"] = test_score
                test_score = json.dumps(temp_test_score)
                
                c.execute("UPDATE users SET test_score = ? WHERE user_id = ?", (test_score, str(message.from_user.id)))
                conn.commit()
            else:                
                bot.send_message(message.from_user.id, "Вы закончили решать задания", reply_markup=keyboard)

            c.execute("UPDATE users SET task_number = 0 WHERE user_id = ?", (str(message.from_user.id),))
            conn.commit()
        elif state == 3:
            c.execute("UPDATE users SET state = 0 WHERE user_id = ?", (str(message.from_user.id),))
            conn.commit()

            test_var_tasks = c.execute("SELECT test_var_tasks FROM users WHERE user_id = ?", (str(message.from_user.id),))
            test_var_tasks = test_var_tasks.fetchone()[0]
            test_var_tasks = json.loads(test_var_tasks)
            total_score = 0

            for i in range(1, 17):
                msg_text = "*Задание №" + str(i) + "*\n"
                user_answer = test_var_tasks[str(i)]["user_answer"]
                right_answer = test_var_tasks[str(i)]["answer"]
                right_answer = right_answer[:-1]
                if user_answer == right_answer:
                    msg_text += "*Ваш ответ:* " + user_answer + "\n"
                    msg_text += "✅Ваш ответ правильный!\n\n"

                    total_score += score_for_task[i-1]
                    temp_test_score = c.execute("SELECT test_score FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
                    
                    temp_test_score = json.loads(temp_test_score)

                    test_score = temp_test_score["task_list"]
                    right_answers = test_score[str(i)]["right_answers"]
                    right_answers = int(right_answers) + 1
                    total_answers = test_score[str(i)]["total_answers"]
                    total_answers = int(total_answers) + 1
                    test_score[str(i)]["right_answers"] = right_answers
                    test_score[str(i)]["total_answers"] = total_answers
                    temp_test_score["task_list"] = test_score
                    test_score = json.dumps(temp_test_score)
                    
                    c.execute("UPDATE users SET test_score = ? WHERE user_id = ?", (test_score, str(message.from_user.id)))
                    conn.commit()

                else:
                    msg_text += "*Ваш ответ:* " + user_answer + "\n"
                    msg_text += "❌Ваш ответ неправильный!\n"
                    msg_text += "*Правильный ответ: " + right_answer + "\n"
                    
                    msg_text += "Пояснение:* " + test_var_tasks[str(i)]["explanation"] + "\n\n"
                    
                    temp_test_score = c.execute("SELECT test_score FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
                    
                    temp_test_score = json.loads(temp_test_score)

                    test_score = temp_test_score["task_list"]
                    total_answers = test_score[str(i)]["total_answers"]
                    total_answers = int(total_answers) + 1
                    test_score[str(i)]["total_answers"] = total_answers

                    temp_test_score["task_list"] = test_score
                    test_score = json.dumps(temp_test_score)
                    
                    c.execute("UPDATE users SET test_score = ? WHERE user_id = ?", (test_score, str(message.from_user.id)))
                    conn.commit()                
                msg_length = len(msg_text)
                telegram_limit = 4096
                if msg_length > telegram_limit:
                    msg_text = msg_text[:telegram_limit]
                    bot.send_message(message.from_user.id, msg_text, parse_mode = "Markdown")
                    msg_text = msg_text[telegram_limit:]
                    if msg_text != "":
                        bot.send_message(message.from_user.id, msg_text, parse_mode = "Markdown")
                else:
                    bot.send_message(message.from_user.id, msg_text, parse_mode = "Markdown")
            msg_text = "За первую часть ЕГЭ по обществознанию вы бы набрали:\n"
            msg_text += "*Первичных баллов: " + str(total_score) + "\n"
            msg_text += "Тестовых баллов: " + str(actual_score_for_task[total_score]) + "*\n\n"

            bot.send_message(message.from_user.id, msg_text, parse_mode = "Markdown", reply_markup=keyboard)
            c.execute("UPDATE users SET test_var_tasks = ? WHERE user_id = ?", ("", str(message.from_user.id)))
            conn.commit()
            c.execute("UPDATE users SET task_number = 0 WHERE user_id = ?", (str(message.from_user.id),))
            conn.commit()
        else:
            return

    elif message.text == "Назад":
        
        state = c.execute("SELECT state FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
        if state == 1:
            
            c.execute("UPDATE users SET state = 0 WHERE user_id = ?", (str(message.from_user.id),))
            conn.commit()
            
            bot.send_message(message.from_user.id, "Вы вернулись в главное меню", reply_markup=keyboard)
        elif state == 3:
            
            task_num = c.execute("SELECT task_number FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
            if task_num == 1:
                return
            c.execute("UPDATE users SET task_number = ? WHERE user_id = ?", (str(int(task_num)-1), str(message.from_user.id)))
            conn.commit()
            task_num -= 1       
            test_var_tasks = c.execute("SELECT test_var_tasks FROM users WHERE user_id = ?", (str(message.from_user.id),))
            test_var_tasks = test_var_tasks.fetchone()[0]
            test_var_tasks = json.loads(test_var_tasks)

            task = test_var_tasks[str(task_num)]
            task_text = "*Задание №" + str(task_num) + ":*\n" + task["text"] + "\n"
            keyboard_ = test_variant_keyboard

            if(task_num == 1):
                keyboard_ = first_task_test
            elif(task_num == 16):
                keyboard_ = last_task_test
            bot.send_message(message.from_user.id, task_text, parse_mode="Markdown", reply_markup=keyboard_)    
            if task["user_answer"] != "":
                bot.send_message(message.from_user.id, "*Ваш ответ: " + task["user_answer"] + "*\n", parse_mode="Markdown")
        else:
            return
    elif message.text == "Тренировочный вариант":  
        state = c.execute("SELECT state FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
        if state != 0:
            return
        c.execute("UPDATE users SET state = 3 WHERE user_id = ?", (str(message.from_user.id),))
        conn.commit()

        test_var_tasks = {}
        for i in range(0, 16):         
            num = random.randint(0, len(tasks[i])-1)
            task_num = str(i+1)
            task = {}
            task["text"] = tasks[int(task_num) - 1][num]["text"]
            task["explanation"] = tasks[int(task_num) - 1][num]["explanation"]
            task["answer"] = tasks[int(task_num) - 1][num]["answer"]
            task["user_answer"] = ""
            test_var_tasks[task_num] = task
        
        test_var_tasks = json.dumps(test_var_tasks)
        c.execute("UPDATE users SET test_var_tasks = ? WHERE user_id = ?", (test_var_tasks, str(message.from_user.id)))
        conn.commit()
        bot.send_message(message.from_user.id, "*Ваш тренировочный вариант:* ", parse_mode="Markdown")
        task_num = 1
        c.execute("UPDATE users SET task_number = ? WHERE user_id = ?", (task_num, str(message.from_user.id)))
        conn.commit()

        test_var_tasks = json.loads(test_var_tasks)

        task = test_var_tasks[str(task_num)]["text"]

        keyboard_ = test_variant_keyboard

        if(task_num == 1):
            keyboard_ = first_task_test
        elif(task_num == 16):
            keyboard_ = last_task_test

        bot.send_message(message.from_user.id, "*Задание №1:\n*" + task, reply_markup=keyboard_, parse_mode="Markdown")
    else:    
        state = c.execute("SELECT state FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
        if state == 1: 
            if message.text.isdigit() and int(message.text) > 0 and int(message.text) < 17:     
                num = int(message.text)
                generate_task(message, num)
            else:
                bot.send_message(message.from_user.id, "Неверный номер задания")
                return
        elif state == 2:           
            task_question_ = c.execute("SELECT task_question FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
            if task_question_ == -1:
                return
            if message.text.isdigit() and int(message.text) > 0:
                
                answer = message.text
                
                task_num = c.execute("SELECT task_number FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
                
                task_question = c.execute("SELECT task_question FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]

                task_answer = tasks[int(task_num) - 1][int(task_question)]["answer"]
                
                task_answer = task_answer.replace(".", "")
                if answer == task_answer:                   
                    bot.send_message(message.from_user.id, "*Правильно!*", parse_mode = "Markdown",reply_markup=test_keyboard)                                      
                    temp_test_score = c.execute("SELECT test_score FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
                    
                    temp_test_score = json.loads(temp_test_score)
                    test_score = temp_test_score["task_list"]
        
                    right_answers = test_score[str(task_num)]["right_answers"]
                    right_answers = int(right_answers) + 1
                    total_answers = test_score[str(task_num)]["total_answers"]
                    total_answers = int(total_answers) + 1
                    test_score[str(task_num)]["right_answers"] = right_answers
                    test_score[str(task_num)]["total_answers"] = total_answers

                    temp_test_score["task_list"] = test_score
                    test_score = json.dumps(temp_test_score)                 
                    c.execute("UPDATE users SET test_score = ? WHERE user_id = ?", (test_score, str(message.from_user.id)))
                    conn.commit()
                else: 
                    bot.send_message(message.from_user.id, "*Неверно!*", parse_mode = "Markdown", reply_markup=test_keyboard)              
                    bot.send_message(message.from_user.id, "*Пояснение: *" + tasks[int(task_num)-1][int(task_question)]["explanation"], parse_mode = "Markdown")
                    
                    bot.send_message(message.from_user.id, "*Ответ:* " + tasks[int(task_num)-1][int(task_question)]["answer"], parse_mode = "Markdown")          
                    temp_test_score = c.execute("SELECT test_score FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]
                    
                    temp_test_score = json.loads(temp_test_score)

                    test_score = temp_test_score["task_list"]
                
                    right_answers = test_score[str(task_num)]["right_answers"]
                    right_answers = int(right_answers)
                    total_answers = test_score[str(task_num)]["total_answers"]
                    total_answers = int(total_answers) + 1
                    test_score[str(task_num)]["right_answers"] = right_answers
                    test_score[str(task_num)]["total_answers"] = total_answers
                
                    temp_test_score["task_list"] = test_score
                    test_score = json.dumps(temp_test_score)
                    
                    c.execute("UPDATE users SET test_score = ? WHERE user_id = ?", (test_score, str(message.from_user.id)))
                    conn.commit()

                
                log_file = open("log.txt", "a")
                dtn = datetime.datetime.now()
                log_file.write(dtn.strftime("%d-%m-%Y %H:%M") + " Пользователь " + str(message.from_user.username) + " ответил на вопрос " + str(task_question) + " задания " + str(task_num) + "\n")
                log_file.write("Его ответ - " + answer + "\n")
                log_file.close()              
                c.execute("UPDATE users SET task_question = ? WHERE user_id = ?", (-1, str(message.from_user.id)))
                conn.commit()
            else:
                bot.send_message(message.from_user.id, "Неверный формат ответа.")
                return

        elif state == 3:      
            user_answer = message.text    
            task_num = c.execute("SELECT task_number FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchone()[0]    
            test_var_tasks = c.execute("SELECT test_var_tasks FROM users WHERE user_id = ?", (str(message.from_user.id),))
            test_var_tasks = test_var_tasks.fetchone()[0]
            test_var_tasks = json.loads(test_var_tasks)   
            user_answer_db = test_var_tasks[str(task_num)]["user_answer"]           
            test_var_tasks[str(task_num)]["user_answer"] = user_answer

            test_var_tasks = json.dumps(test_var_tasks)
            c.execute("UPDATE users SET test_var_tasks = ? WHERE user_id = ?", (test_var_tasks, str(message.from_user.id)))
            conn.commit()

            keyboard_ = test_variant_keyboard

            if(task_num == 1):
                keyboard_ = first_task_test
            elif(task_num == 16):
                keyboard_ = last_task_test

            if(user_answer_db == ""):
                
                bot.send_message(message.from_user.id, "*Ответ принят*", parse_mode = "Markdown", reply_markup=keyboard_)
            else:
                
                bot.send_message(message.from_user.id, "*Ответ изменен*", parse_mode = "Markdown", reply_markup=keyboard_)
        else:
            return
        
print("Bot started")


bot.polling(none_stop=True)

