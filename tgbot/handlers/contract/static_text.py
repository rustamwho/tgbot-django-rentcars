NOT_EXISTS_CONTRACTS = '❗️У вас нет действующих договоров с арендодателем.'

PERSONAL_DATA_NOT_EXISTS = ('📍Вы не заполнили свои данные.📍\n\nВыберите в '
                            'меню "<b>Мои данные</b>" или '
                            'Нажмите /personal_data')

PERSONAL_DATA_WRONG = ('Для редактирования данных выберите в меню '
                       '"<b>Мои данные</b>".\nИли нажмите /personal_data')

PERSONAL_DATA = ('Ваши данные:\n'
                 '📌<b>{last_name} {first_name} {middle_name}</b>\n'
                 '📌<b>Пол:</b> {gender}\n'
                 '📌<b>Дата рождения:</b> {birthday}\n'
                 '📌<b>Почта:</b> {email}\n'
                 '📌<b>Номер телефона:</b> {phone_number}\n'
                 '📌<b>Паспорт:</b> {passport_serial} №{passport_number}\n'
                 '📌<b>Выдан:</b> {passport_date_of_issue} '
                 '{passport_issued_by}\n'
                 '📌<b>Адрес прописки:</b> {address_registration}\n'
                 '📌<b>Адрес проживания:</b> {address_of_residence}\n\n'
                 '📌<b>Близкий человек:</b> {close_person_phone} '
                 '{close_person_name}\n'
                 '📌<b>Адрес:</b> {close_person_address}')

CONTRACT_EXISTS_NO_PHOTO = ('Договор сформирован, но вы еще не загрузили '
                            'фотографии машины.')
CONTRACT_NOT_EXISTS_CAR = '❌ У вас еще нет арендованной машины'
CONTRACT_EXISTS_CAR = '\n\n📍 Ваша машина: {car_info}'
ASK_CAR_PHOTOS = ('Сфотографируйте и отправьте мне <b>фотографии машины</b>.\n'
                  '\nМожно скинуть по одному или все разом. Я их все сохраню '
                  'для Вас на будущее.\n\n❗️'
                  '<i>Сделайте больше фотографий, после подтверждения их '
                  'нельзя будет изменить!</i>')

ABOUT_CONTRACT_MENU_TEXT = ('<b>Ваш договор:</b>\n'
                            '📌 Время формирования: <i>{created_at}</i>\n'
                            '📌 Начало аренды: <i>{approved_at}</i>\n'
                            '📌 Конец аренды: <i>{closed_at}</i>\n'
                            '📌 Машина: <i>{car_name}</i>\n\n'
                            '❗ Договор может быть завершен раньше времени '
                            'администратором.')

MY_FINES_MENU_TEXT = ('Ваши штрафы:\n'
                      'Всего: {all_fines_count}\n'
                      'Не оплачено: {unpaid_fines_count}')
MY_ALL_FINES_LIMIT = ('За все время у вас {all_fines_count} штрафов\n'
                      'Последние {limit} (сначала неоплаченные):\n'
                      '{text_fines}\n')
MY_ALL_FINES_DOES_NOT_EXISTS = 'У вас нет штрафов 🎉'
MY_PAID_FINES = ('Ваши ОПЛАЧЕННЫЕ штрафы:\n'
                 '{text_fines}')
MY_PAID_FINES_DOES_NOT_EXISTS = 'У вас нет оплаченных штрафов 🤔'
MY_UNPAID_FINES = ('Ваши НЕОПЛАЧЕННЫЕ штрафы:\n'
                   '{text_fines}')
MY_UNPAID_FINES_DOES_NOT_EXISTS = 'У вас нет неоплаченных штрафов 🎉'
