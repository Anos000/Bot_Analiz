import telebot
from telebot import types
import pandas as pd
import os
import matplotlib.pyplot as plt


bot = telebot.TeleBot('7702548527:AAH-xkmHniF9yw09gDtN_JX7tleKJLJjr4E')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура

    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру

    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)

    bot.send_message(message.from_user.id, text='Твоя моя понимать?', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, 'Пожалуйста, отправьте CSV файл для анализа.')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Ну ладно :(')


# Функция для ограничения текста в ячейках
def truncate_text(text, max_len=15):
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text


# Функция для создания изображения таблицы
def create_table_image(df, file_path):
    # Увеличиваем размер изображения
    fig, ax = plt.subplots(figsize=(15, 6))  # Размер 15x6 для более просторного отображения

    ax.axis('tight')  # Отключаем оси
    ax.axis('off')  # Отключаем оси для чистого отображения таблицы

    # Преобразуем данные DataFrame в строки с обрезкой текста
    truncated_df = df.applymap(lambda x: truncate_text(str(x), max_len=15))

    # Создаем таблицу
    table = ax.table(cellText=truncated_df.values, colLabels=truncated_df.columns, cellLoc='center', loc='center')

    # Отключаем авторазмер шрифта для управления его величиной вручную
    table.auto_set_font_size(False)

    # Устанавливаем меньший размер шрифта для компактности
    table.set_fontsize(8)  # Размер шрифта 8 для улучшения читабельности

    # Увеличиваем размер ячеек для лучшего распределения текста
    table.scale(1.5, 1.5)  # Увеличиваем ширину и высоту ячеек больше

    # Сохраняем изображение таблицы в файл с плотной обрезкой по границам
    plt.savefig(file_path, bbox_inches='tight', dpi=300)
    plt.close()


# Обработчик загрузки файлов
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        # Получаем информацию о загруженном файле
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Определяем путь для сохранения загруженного файла
        file_name = message.document.file_name
        file_path = os.path.join("downloads", file_name)

        # Сохраняем загруженный файл
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

            # Чтение файла CSV
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_path)

            # Создаем изображение таблицы из первых 5 строк DataFrame
            image_path = os.path.join("downloads", "table_image.png")
            create_table_image(df.head(), image_path)

            excel_path = os.path.join("downloads", f"{file_name.split('.')[0]}.xlsx")
            df.to_excel(excel_path, index=False)  # Сохраняем DataFrame в Excel

            # Отправляем пользователю изображение с таблицей
            with open(image_path, 'rb') as image:
                bot.send_photo(message.chat.id, image)
                # Отправка Excel файла
            with open(excel_path, 'rb') as excel_file:
                bot.send_document(message.chat.id, excel_file)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, загрузите файл в формате CSV.")
    except Exception as e:
        # Отправляем сообщение об ошибке в случае сбоя
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

bot.polling(none_stop=True, interval=0)