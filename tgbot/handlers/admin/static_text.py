command_start = '/stats'
only_for_admins = 'Извините, это меню только для администраторов.'

ADMIN_MENU_BASE = f'️🔽 Выберите нужное действие в меню 🔽\n' \
                  f'{command_start} - bot stats'

users_amount_stat = "<b>Users</b>: {user_count}\n" \
                    "<b>24h active</b>: {active_24}"

UNAPPROVED_CONTACTS_NOT_EXISTS = ('🔽 Выберите нужное действие в меню 🔽\n\n'
                                  '☑️ Неподтвержденных договоров нет.')
UNAPPROVED_CONTACTS_NOT_EXISTS2 = (
    '🔽 Выберите нужное действие в меню 🔽\n\n'
    '☑️ Неподтвержденных договоров все еще нет.')
NOW_SEND_UNAPPROVED_CONTRACTS = 'Сейчас скину неподтвержденные договоры.'

TEXT_FOR_APPROVE_CONTRACT = ('<b>Договор от {created_at}</b> \n'
                             '<b>Арендатор:</b> {name_arendator}\n'
                             '<b>Действителен до:</b> {closed_at}')
CONTRACT_IS_APPROVED = '\n\n✅ Подтвержден ✅'
