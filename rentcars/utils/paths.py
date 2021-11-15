def car_photos_path(instance, filename):
    car_license_plate = instance.car.license_plate
    return f'cars/car_{car_license_plate}/{filename}'


def contract_photos_path(instance, filename):
    user_id = instance.contract.user.user_id
    return 'contracts/photo_car/user_{0}/{1}'.format(user_id, filename)


def fine_screens_path(instance, filename=None):
    filename = (f'{instance.car.license_plate[:-3]} '
                f'{instance.get_date_in_str()}_{instance.amount}rub')
    return f'fines/{filename}.jpg'
