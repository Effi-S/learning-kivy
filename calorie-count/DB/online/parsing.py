"""This module is used to parse external data and add them to the DB for the app."""
from __future__ import annotations
import ijson

from DB.online.connect import FoodData


def parse_foods_foundation(filename, heading) -> list[FoodData]:
    # data = list(json.load(open('FoodData_Central_foundation_food_json_2021-10-28.json'))['FoundationFoods'])
    data = ijson.items(open(filename), f'{heading}.item')
    for i, food in enumerate(data):
        description = food['description']
        portions = food['foodPortions']
        portions = {p['measureUnit']['name']: p['gramWeight'] for p in portions}
        nut_dict = dict.fromkeys(('protein', 'fats', 'carbs', 'sodium', 'sugar', 'water'), .0)
        for nut in food['foodNutrients']:
            name = nut['nutrient']['name']
            unit_name = nut['nutrient']['unitName']
            for s in nut_dict:
                if s.rstrip('s') in name.lower():
                    nut_dict[s] = float(nut['amount'])
                    if unit_name == 'mg':
                        nut_dict[s] /= 1000

        yield FoodData(description=description, portions=portions, **nut_dict)


portions = {}
if __name__ == '__main__':

    foods = list(parse_foods_foundation('FoodData_Central_foundation_food_json_2021-10-28.json',
                                        'FoundationFoods'))
    print(len(foods))
    for food in parse_foods_foundation('FoodData_Central_sr_legacy_food_json_2021-10-28.json',
                                       'SRLegacyFoods'):
        p = food.portions
        for k, v in p.items():
            if k in portions:
                assert portions[k] == p[k], f'{k}, {portions[k]} != {p[k]}'
            else:
                portions[k] = v

    for food in parse_foods_foundation('FoodData_Central_branded_food_json_2021-10-28.json',
                                       'BrandedFoods'):
        p = food.portions
        for k, v in p.items():
            if k in portions:
                assert portions[k] == p[k], f'{k}, {portions[k]} != {p[k]}'
            else:
                portions[k] = v
        print(food)
        break
