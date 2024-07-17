import json
import config
import numpy as np  
from PIL import Image, ImageDraw, ImageFont
from jproperties import Properties
import cv2
import os

class GamestateHelper:
    def __init__(self, game_id):
        self.game_id = game_id
        self.gamestate = self.get_gamestate()

    def get_gamestate(self):
        with open(f"{config.gamestate_path}/{self.game_id}.json", "r") as f:
            gamestate = json.load(f)
        return gamestate
    
    def drawTile(self, context, position, tileName):
        configs = Properties()
        with open("data/tileImageCoordinates.properties", "rb") as f:
            configs.load(f)
        x = configs.get(position)[0].split(",")[0]
        y = configs.get(position)[0].split(",")[1]
        filepath = "images/resources/hexes/defended/"+tileName+".png"
        if not os.path.exists(filepath):  
            filepath = "images/resources/hexes/homesystems/"+tileName+".png"

        tileImage = Image.open(filepath).convert("RGBA")
        tileImage = GamestateHelper.remove_background(tileImage)
        tileImage = tileImage.resize((345, 322))
        context.paste(tileImage,(int(x),int(y)))
        return context

    
    def remove_background(image):  
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2BGRA)  
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2GRAY)  
        _, mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)  
        mask = cv2.bitwise_not(mask)  
        result = cv2.bitwise_and(cv_image, cv_image, mask=mask)  

        b, g, r, a = cv2.split(result)  
        result_rgba = cv2.merge((r, g, b, a))  # Reorder the channels to RGBA format  

        result_pil = Image.fromarray(result_rgba, 'RGBA')  
        return result_pil

    def player_setup(self, player_id, faction):

        name = self.gamestate["players"][str(player_id)]["player_name"]

        if self.gamestate["setup_finished"] == "True":
            return ("The game has already been setup!")

        with open("data/factions.json", "r") as f:
            faction_data = json.load(f)
        self.gamestate["players"][str(player_id)].update(faction_data[faction])
        self.update()
        return(f"{name} is now setup!")

    def setup_finished(self):

        for i in self.gamestate["players"]:
            if len(self.gamestate["players"][i]) < 3:
                return(f"{self.gamestate['players'][i]['player_name']} still needs to be setup!")

        self.gamestate["setup_finished"] = "True"
        return("Game setup complete")

    def update(self):
        with open(f"{config.gamestate_path}/{self.game_id}.json", "w") as f:
            json.dump(self.gamestate, f)

    def get_player_stats(self, player_id):
        return self.gamestate["players"][str(player_id)]

    def update_player_stats(self, *args):

        for ar in args:
            self.gamestate["players"][ar.player_id] = ar.stats
        self.update()