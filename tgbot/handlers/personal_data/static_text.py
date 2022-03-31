PERSONAL_DATA_NOT_EXISTS = ('📍Вы еще не заполняли свои паспортные данные.\n\n'
                            'Это необходимо для формирования договора.\n\n')
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

command_cancel = '/cancel'
ABOUT_FILLING_PERSONAL_DATA = (f'Я буду писать какие данные мне отправить.\n\n'
                               f'Для отмены в любой момент отправьте '
                               f'{command_cancel}')
ASK_FIRST_NAME = 'Введите Ваше <b>ИМЯ</b>'
ASK_LAST_NAME = 'Введите Вашу <b>ФАМИЛИЮ</b>'
ASK_MIDDLE_NAME = 'Введите Ваше <b>ОТЧЕСТВО</b>'
HELLO_FULL_NAME = 'Приятно познакомиться, {name}!'
ASK_GENDER = 'Выберите ваш <b>ПОЛ</b>'
ASK_BIRTHDAY = ('<b>ДАТА РОЖДЕНИЯ</b>\n\n'
                '<i>Введите в формате ДД.ММ.ГГГГ. Например, 25.10.1996.</i>')
ASK_EMAIL = ('<b>АДРЕС ЭЛЕКТРОННОЙ ПОЧТЫ</b>\n\n'
             '<i>Введите полностью. Например, rustamwho@gmail.com</i>')
ASK_PHONE_NUMBER = ('<b>НОМЕР ТЕЛЕФОНА</b>\n\n'
                    '<i>Введите российский номер.</i>')
ASK_PASSPORT_SERIAL = ('<b>СЕРИЯ ПАСПОРТА</b>\n\n'
                       '<i>Введите 4 цифры.</i>')
ASK_PASSPORT_NUMBER = ('<b>НОМЕР ПАСПОРТА</b>\n\n'
                       '<i>Введите номер паспорта.</i>')
ASK_PASSPORT_DATE_OF_ISSUE = ('<b>ДАТА ВЫДАЧИ ПАСПОРТА</b>\n\n'
                              '<i>Введите в формате ДД.ММ.ГГГГ. '
                              'Например, 25.10.1996.</i>')
ASK_PASSPORT_ISSUED_BY = ('<b>КЕМ ВЫДАН ПАСПОРТ</b>\n\n'
                          '<i>Введите название полностью.</i>')
ASK_ADDRESS_REGISTRATION = ('<b>АДРЕС ПРОПИСКИ</b>\n\n'
                            '<i>Введите адрес полностью, включая регион, '
                            'город, улицу и дом. Например, Республика '
                            'Татарстан, г. Казань, ул. Баумана, д. 1</i>')
ASK_ADDRESS_RESIDENCE_FIRST = ('<b>АДРЕС ПРОЖИВАНИЯ</b>\n\n'
                               'Совпадает с местом прописки?')
ASK_ADDRESS_RESIDENCE_SECOND = ('<b>АДРЕС ПРОЖИВАНИЯ</b>\n\n'
                                '<i>Введите адрес полностью, включая регион, '
                                'город, улицу и дом. Например, Республика '
                                'Татарстан, г. Казань, ул. Баумана, д. 1</i>')
ASK_CLOSE_PERSON_NAME = ('<b>БЛИЗКИЙ ЧЕЛОВЕК</b>\n\n'
                         '<i>Введите в виде ИМЯ (КЕМ ПРИХОДИТСЯ). Например, '
                         '"Юля (Жена)".</i>')
ASK_CLOSE_PERSON_PHONE = ('<b>НОМЕР БЛИЗКОГО ЧЕЛОВЕКА</b>\n\n'
                          '<i>Введите российский номер абонента '
                          '{close_person_name}.</i>')
ASK_CLOSE_PERSON_ADDRESS_FIRST = ('<b>АДРЕС ПРОЖИВАНИЯ БЛИЗКОГО ЧЕЛОВЕКА</b>'
                                  '\n\nСовпадает с адресом вашего проживания?')
ASK_CLOSE_PERSON_ADDRESS_SECOND = ('<b>АДРЕС ПРОЖИВАНИЯ БЛИЗКОГО ЧЕЛОВЕКА</b>'
                                   '\n\n<i>Введите адрес полностью, включая '
                                   'регион, город, улицу и дом. Например, '
                                   'Республика Татарстан, г. Казань, ул. '
                                   'Баумана, д. 1</i>')

PERSONAL_DATA_WRONG = ('Для редактирования данных выберите в меню '
                       '"<b>Мои данные</b>".\nИли нажмите /personal_data')

PERSONAL_DATA_FINISHED = ('✅ Данные сохранены ✅\nДля формирования договора '
                          'выберите в меню <b>Договор</b>.')
