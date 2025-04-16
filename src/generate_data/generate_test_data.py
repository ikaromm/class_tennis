import random
import string
from uuid import uuid4


def generate_test_data(file_name: str):

    with open(file_name, "w") as f:
        f.write("part_name;part_number;part_car_model_legado;blob\n")
        chars = string.ascii_letters + string.digits
        blob = "".join(random.choices(chars, k=1000))
        for i in range(10_000):
            car_model = None
            if i % 2 == 0:
                car_model = "car_a"
            else:
                car_model = "car_b"

            f.write(f"part_{i};{uuid4()};{car_model};{blob}\n")
