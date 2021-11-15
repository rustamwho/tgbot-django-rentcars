command_start = '/stats'
only_for_admins = 'Извините, это меню только для администраторов.'

ADMIN_MENU_BASE = f'️🔽 Выберите нужное действие в меню 🔽\n'

users_amount_stat = "<b>Users</b>: {user_count}\n" \
                    "<b>24h active</b>: {active_24}"

UNAPPROVED_CONTACTS_NOT_EXISTS = ('🔽 Выберите нужное действие в меню 🔽\n\n'
                                  '☑️ Неподтвержденных договоров нет.')
UNAPPROVED_CONTACTS_NOT_EXISTS2 = (
    '🔽 Выберите нужное действие в меню 🔽\n\n'
    '☑️ Неподтвержденных договоров все еще нет.')
NOW_SEND_UNAPPROVED_CONTRACTS = 'Сейчас скину неподтвержденные договоры 👀'

TEXT_FOR_APPROVE_CONTRACT = ('❗<b>Договор от {created_at}</b>❗ \n'
                             '<b>Арендатор:</b> {name_arendator}\n'
                             '<b>Действителен до:</b> {closed_at}')
CONTRACT_CANT_BE_APPROVED = ('\n\n❗ Договор не может быть подтвержден, '
                             'так как водитель еще не загрузил '
                             'фотографии машины')
CONTRACT_IS_APPROVED = '\n\n✅ Подтвержден ✅'

COUNT_CARS = ('Всего машин: <b>{all_cars_count}</b>\n'
              'В аренде: <b>{rented_cars_count}</b>')

COUNT_FINES = ('Всего штрафов:\t{all_fines_count}\n'
               'Не оплачено:\t{unpaid_fines_count}')

ASK_DATE_FINE = ('📍Выбрана машина:   🚘{license_plate}\n\n'
                 '✍️<b>Введите ДАТУ штрафа</b>\n'
                 '<i>Введите в формате ДД.ММ.ГГГГ. Например, 25.10.1996.</i>')
ASK_TIME_FINE = ('✍️<b>Введите ВРЕМЯ штрафа</b>\n'
                 '<i>Введите в формате ЧЧ:ММ. Например, 15:47.</i>')
ASK_AMOUNT_FINE = ('✍️<b>Введите СУММУ штрафа в рублях</b>\n'
                   '<i>Введите только число</i>')
ASK_SCREENSHOT_FINE = ('⬆️<b>Пришлите СКРИНШОТ штрафа</b>\n'
                       '<i>Отправьте только одну картинку</i>')
NEW_FINE_IS_CREATED = ('✅ Штраф сохранен ✅\n\n'
                       '🚘 Машина: {license_plate}\n'
                       '📅 Дата: {date}\n'
                       '💵 Сумма: {amount} руб.\n\n')
NEW_FINE_ABOUT_USER = ('📍 Водитель: {user_name}\n'
                       '📍 Ссылка: {url_to_user}\n'
                       '📍 Telegram ID: {telegram_id}\n'
                       '📍 Номер телефона: {phone_number}\n')
MESSAGE_TO_USER_SENT = '✅ Сообщение о штрафе отправлено водителю.'
MESSAGE_TO_USER_NOT_SENT = ('❗ Пользователь заблокировал бота, сообщение '
                            'отправить не получилось.\n')
MESSAGE_NEW_FINE_USER = ('❗ У вас новый штраф ❗\n\n'
                         '🚘 Машина: {license_plate}\n'
                         '📅 Дата: {date}\n'
                         '💵 Сумма: {amount} руб.\n\n')

CLOSE_CONTRACT_MENU_TEXT = '🔽 Выберите договор, который надо завершить 🔽'
ABOUT_CONTRACT = ('❗ Договор:\n'
                  '📌 Водитель: <i>{user_name}</i>\n'
                  '📌 Машина: <i>{car_name}</i>\n'
                  '📌 Время формирования: <i>{created_at}</i>\n'
                  '📌 Начало аренды: <i>{approved_at}</i>\n')
CLOSED_AT_CONTRACT = '📌 Конец аренды: <i>{closed_at}</i>\n\n'
ASK_ACCEPT_CLOSE_CONTRACT = 'Подтвердите завершение действия договора'
CONTRACT_IS_CLOSED = '✅ Договор завершен ✅'
