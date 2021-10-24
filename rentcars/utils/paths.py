def car_photos_path(instance, filename):
    car_license_plate = instance.car.license_plate
    return f'cars/car_{car_license_plate}/{filename}'


def contract_photos_path(instance, filename):
    user_id = instance.contract.user.user_id
    return 'contracts/photo_car/user_{0}/{1}'.format(user_id, filename)
