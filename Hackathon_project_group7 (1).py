#this portion of the code contains the imports of libraries and packages used
from food_extractor.food_model import FoodModel #foodbert
import pytesseract
import io,os
import pandas as pd
import re
from google.cloud import vision
from google.cloud import vision_v1
import deepl #deepl api
from rapidfuzz import process, fuzz
import numpy as np
import pandas as pd
import requests
import json


#inicialization of the deep learning model that recognizes ingredients
model = FoodModel("chambliss/distilbert-for-food-extraction")


#ingredient database to double check and correct possible flaws
ingredients_database = r"C:\Users\conde\Documents\Masters\Hackathon\ingre"
ings = pd.read_csv(ingredients_database).iloc[:,1].to_list()


#definition of the function that will analyse the image and deliver results
def get_ingredients(file):
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\conde\Documents\Masters\2nd semester\Hackathon\Repo\food-345217-eb439b2535cc.json"


    client_options = {'api_endpoint': 'eu-vision.googleapis.com'}

    client = vision.ImageAnnotatorClient(client_options=client_options)

    # load image into memory
    with io.open(file,"rb") as image_file:
        file_content = image_file.read()
    # perform text detection from the image
    image_detail = vision.Image(content=file_content)
    response = client.document_text_detection(image=image_detail)
    # print text from the dcoment
    doctext = response.full_text_annotation.text
    #print(doctext)

    doctext = deepl.Translator("Here should be the API Key").translate_text(doctext, target_lang="EN-US").text
    #print(doctext)
    
    items = []
    for i, v in enumerate(list(model.extract_foods(doctext)[0].values())[1]):
        if v['conf'] >= 0.2:
            items.append(v['text'].lower())
        else:
            pass
    #print(items)

    items = list(set(items))

    clean_item = list()
    for item in items:
        if (process.extractOne(item, ings, scorer=fuzz.WRatio)[1] > 87):
            clean_item.append(item)
    #print(clean_item)

    items = clean_item

    quantities = dict()
    for i, v in enumerate(items):
        quantities[v] = float(input(f'Enter grams of {v}: '))
    running = False
    #print(quantities)
    return quantities


#path of the file to recognize
shopping_list = r"C:\Users\conde\OneDrive\Pictures\Capturas de Ecrã\shopping_list_sample.png"
russian_recipe = r"C:\Users\conde\OneDrive\Pictures\Capturas de Ecrã\russian_recipe.png"
new_recipe = r"C:\Users\conde\OneDrive\Pictures\Capturas de Ecrã\Screenshot (25).png"

path = new_recipe

#Calorie calculator, taking ingredients dictionary as input
dicti = get_ingredients(path)


query = " ".join(dicti.keys())
api_url = 'https://api.calorieninjas.com/v1/nutrition?query='
response = requests.get(api_url + query, headers={'X-Api-Key': 'Here should be the API Key'})
if response.status_code != requests.codes.ok:
    print("Error:", response.status_code, response.text)


results = json.loads(response.text)["items"]


calo = dict()
for result in results:
    calo[result["name"]] = result["calories"]


calorie_sum = 0
print("\nShopping list:")
for pos in dicti.keys():
    amount = dicti[pos]
    calories = amount*calo[process.extractOne(pos, calo.keys(), scorer=fuzz.WRatio)[0]]/100
    calorie_sum += calories
    print(f"{amount}g of {pos} having {round(calories)} kcal")
print(f"\nYour total shopping list has {round(calorie_sum)} kcal")


print(dicti)


#If dicti (dictionary) is called it will return the dictionary that can be used as input.
#The print statements regarding calories are for the user.