import json
import sqlite3

class DrinkRepository:

    def __init__(self, dbPath):
        self.dbPath = dbPath

    def getAvailableDrinks(self):
        conn = self._makeConnection()
        c = conn.cursor()
        query = ("SELECT d.id, d.name, d.image, "
        "CASE "
        "WHEN i.jar_pos IS NOT NULL THEN 1 "
        "ELSE i.mixer > 0 "
        "END as available "
        "FROM drinks d "
        "INNER JOIN drink_ingredient di ON d.id = di.drink_id "
        "INNER JOIN ingredients i ON di.ingredient_id = i.id "
        "GROUP BY d.id, d.name, d.image "
        "HAVING COUNT(i.id) = SUM(available)")

        c.execute(query)

        drinks = []
        for row in c:
            drinks.append({
                "id": row[0],
                "name": row[1],
                "image": row[2]
            })

        conn.close()
    
        return drinks

    def getDrinkRecipe(self, drinkID):
        conn = self._makeConnection()
        c = conn.cursor()
        query = ("SELECT i.id, i.name, i.jar_pos, di.oz, i.flow"
        "FROM ingredients i "
        "INNER JOIN drink_ingredient di ON i.id = di.ingredient_id "
        "WHERE di.drink_id = ?")

        c.execute(query, (drinkID,))

        ingredients = []
        for row in c:
            ingredients.append({
                "id": row[0],
                "name": row[1],
                "jar_pos": row[2],
                "oz": row[3],
                "flow": row[4]
            })
        
        conn.close()

        return ingredients
    
    def insertDrink(self, name, image, ingredients):
        conn = self._makeConnection()
        c = conn.cursor()
        query = "INSERT INTO drinks(name, image) VALUES(?, ?)"

        c.execute(query, (name, image))

        drinkID = c.lastrowid

        self.updateDrinkRecipe(c, drinkID, ingredients)

        conn.commit()
        conn.close()

        return drinkID

    def updateDrink(self, drinkID, name, image, ingredients=None):
        conn = self._makeConnection()
        c = conn.cursor()
        query = "UPDATE drinks SET name = ?, image = ? WHERE id = ?"

        c.execute(query, (name, image, drinkID))

        if ingredients is not None:
            self.updateDrinkRecipe(c, drinkID, ingredients)

        conn.commit()
        conn.close()

        return c.rowcount > 0

    def updateDrinkRecipe(self, cursor, drinkID, ingredients):
       
        # perhaps some other time we can go through the list and update existing ingredients but this makes it easier to get the order right.
        cursor.execute("DELETE FROM drink_ingredient WHERE drink_id = ?", (drinkID))

        params = []
        query = "INSERT INTO drink_ingredient(drink_id, ingredient_id, oz) "

        for ing in ingredients:
            query += "VALUES(?, ?, ?) "
            params.extend([drinkID, ing.get('id'), ing.get('oz')])

        cursor.execute(query, params)    
    
    def deleteDrink(self, drinkID):
        conn = self._makeConnection()
        c = conn.cursor()
        query = "DELETE FROM drinks WHERE id = ?"

        c.execute(query, (drinkID,))

        conn.commit()
        conn.close()

        return c.rowcount > 0

    def _makeConnection(self):
        conn = sqlite3.connect(self.dbPath)
        conn.execute("PRAGMA foreign_keys = 1")

        return conn

class IngredientRepository :

    def __init__(self, dbPath):
        self.dbPath = dbPath

    def getAll(self, availOnly=False):
        conn = self._makeConnection()
        c = conn.cursor()
        query = ("SELECT id, name, jar_pos, mixer, flow "
        "FROM ingredients ")

        if availOnly:
            query += "WHERE (jar_pos IS NOT NULL OR mixer > 0) "

        query += "ORDER BY (jar_pos IS NULL), jar_pos"

        c.execute(query)

        ingredients = []
        for row in c:
            ingredients.append({
                "id": row[0],
                "name": row[1],
                "jar_pos": row[2],
                "mixer": row[3],
                "flow": row[4]
            })
        
        conn.close()

        return ingredients

    def getIngredient(self, ingID, byJar=False):
        conn = self._makeConnection()
        c = conn.cursor()
        query = ("SELECT id, name, jar_pos, mixer, flow "
        "FROM ingredients ")

        if str(ingID).isdigit() and byJar:
            query += "WHERE jar_pos = ?"
        elif str(ingID).isdigit():
            query += "WHERE id = ?"
        else:
            query += "WHERE name = ?"

        c.execute(query, (ingID,))
        row = c.fetchone()
        
        conn.close()

        if row is None:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "jar_pos": row[2],
            "mixer": row[3],
            "flow": row[4]
        }

    def updateIngredient(self, ingID, **kwargs):
        qParams = {}

        if "name" in kwargs and len(kwargs["name"]) > 0 :
            qParams["name = ?"] = kwargs["name"]

        if "mixer" in kwargs:
            qParams["mixer = ?"] = 1 if kwargs["mixer"] else 0

        if "flow" in kwargs and str(kwargs["flow"]).isdigit():
            qParams["flow = ?"] = kwargs["flow"]

        if "jar_pos" in kwargs:
            jarpos = None if kwargs["jar_pos"] is not None and int(kwargs["jar_pos"]) >= 0 else kwargs["jar_pos"]

            prevJar = self.getIngredient(jarpos, True) if jarpos is not None else None
            if prevJar is not None:
                self.updateIngredient(prevJar["id"], jar_pos=None)

            qParams["jar_pos = ?"] = jarpos

        if len(qParams) == 0:
            return

        query = "UPDATE ingredients SET " + ", ".join(qParams.keys()) + " WHERE id = ?"
        params = qParams.values()
        params.append(ingID)

        conn = self._makeConnection()
        c = conn.cursor()
        c.execute(query, params)

        conn.commit()
        conn.close()

        return c.rowcount > 0

    def _makeConnection(self):
        conn = sqlite3.connect(self.dbPath)
        conn.execute("PRAGMA foreign_keys = 1")

        return conn    