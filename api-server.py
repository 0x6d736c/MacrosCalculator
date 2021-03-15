import MacroEstimator   #Drives calculations
import flask            #Runs API server
from flask import request, jsonify

class APIServer:
    """API Server class for the MacroCalculator. Provides a JSON object response to user based on input data. Allows for reuse of data in multiple applications."""
    app = flask.Flask(__name__)
    app.config["DEBUG"] = True

    #Provides basic API instructions to user
    @app.route('/', methods=['GET'])
    def home():
        return f'''<h1>MacrosCalculator API</h1>
        
        Ya messed something up, friend. 

        <hr>

        Send a GET request using the URL "127.0.0.1:5000/api/v1/calculate" with the following query strings:
    
        Be sure to include the following data:
        <ul>
            <li>height = (any float)</li>
            <li>weight = (any float)</li>
            <li>age = (any int)</li>
            <li>sex = (male, female)</li>
            <li>active = (true, false)</li>
            <li>bf = (any float)</li>
            <li>ef = (1, 2, 3)</li>
            <li>goal = (lose, maintain, gain)</li>
        </ul>

        <hr>

        <strong>Example:</strong> /api/v1/calculate?height=6&weight=180&sex=male&age=30&goal=maintain&ef=1&active=true&bf=15.0

        <hr>

        As you can see, order doesn't matter, just correctness of spelling and capitalization. Have fun. :)
        '''

    @app.route('/api/v1/calculate', methods=['GET'])
    def api_calculate():
        #Create user object to store data passed-in
        user = MacroEstimator.Athlete()

        #Get user height from request
        if "height" in request.args:
            height = float(request.args["height"])
            height = APIAssist.verify_height(height)
            user.height = height

        #Get user weight from request
        if "weight" in request.args:
            weight = float(request.args["weight"])
            weight = APIAssist.verify_weight(weight)
            user.weight = weight

        #Get user age from request
        if "age" in request.args:
            age = int(request.args["age"])
            age = APIAssist.verify_age(age)
            user.age = age

        #Get user bodyfat from request
        #TODO bodyfat approximation not firing, fix
        if "bf" in request.args:
            bf = float(request.args["bf"])
            bf = APIAssist.verify_bf(bf)
            user.body_fat = bf
            print(user.body_fat)
        else:
            user.approximate_body_fat

        #Get user sex from request
        if "sex" in request.args:
            sex = request.args["sex"]
            sex = APIAssist.verify_sex(sex)
            user.gender = sex

        #Get user activity from request
        if "active" in request.args:
            if request.args["active"] == "true":
                user.active_job = True
            else:
                user.active_job = False

        #Get user weight from request
        if "ef" in request.args:
            if request.args["ef"] == "3":
                user.exercise_freq = 3
            elif request.args["ef"] == "2":
                user.exercise_freq = 2
            else:
                user.exercise_freq = 1

        #Get user goal from request
        if "goal" in request.args:
            if request.args["goal"] == "lose":
                user.goal = "Lose Weight"
            elif request.args["goal"] == "gain":
                user.goal = "Gain Weight"
            else:
                user.goal = "Maintain Weight"

            

        #Create measurements and diet for user
        measurements = MacroEstimator.Measurements(person = user)
        diet = MacroEstimator.Diet(athlete = user)


        #Set user macros
        diet.set_macros(goal = user.goal, weight = user.weight)

        stats = {
            "baseStats" : {
                "height" : user.height,
                "weight" : user.weight,
                "age" : user.age,
                "sex" : user.gender,
                "bodyFat" : user.body_fat,
                "activeJob" : user.active_job,
                "exerciseFrequency" : user.exercise_freq,
                "goal": user.goal,
            },

            "calculations" : {
                "BMI" : (round(user.body_mass_index * 100, 4)),
                "BMIstatus" : APIAssist.bmi_status(user),
                "TDEE" : round(diet.total_daily_energy_expenditure(), 4),
                "LBM" : measurements.lean_body_mass(),
                "BMR" : round(measurements.basal_metabolic_rate(), 4),
                "minProtein" : round(measurements.protein_requirement(), 4),
                "macros" : {
                    "protein" : {
                        "grams" : diet.set_protein / MacroEstimator.Diet.PROTEIN_KCAL,
                        "kcal" : diet.set_protein
                    },
                    "carb" : {
                        "grams" : diet.set_carbs / MacroEstimator.Diet.CARBS_KCAL,
                        "kcal" : diet.set_carbs
                    },
                    "fat" : {
                        "grams" : diet.set_fats / MacroEstimator.Diet.FATS_KCAL,
                        "kcal" : diet.set_fats
                    }

                }
            }
        }

        return jsonify(stats)


class APIAssist:
    """Helper methods for the web API."""

    #Verification methods to prevent frivolous API calls
    def verify_height(height):
        """Return None if height is unreasonably short or tall. Else, return input height."""
        if (height > 10.0 or height < 3.0):
            return None
        else:
            return height

    def verify_weight(weight):
        """Return None if weight is unreasonably high. Else, return input weight."""
        if (weight > 1000.0):
            return None
        else:
            return weight

    def verify_age(age):
        """Return None if age is unreasonably low or high. Else, return input age."""
        if (age < 0 or age > 125):
            return None
        else:
            return age

    def verify_bf(bf):
        """Return None if bodyfat exceeds human limits. Else, return input bodyfat."""
        if (bf < 0.0 or bf > 100.0):
            return None
        else:
            return bf

    def verify_sex(sex):
        """Calculator offers Male or Female option. Return None if neither criteria met."""
        if (sex != "male" and sex != "female"):
            return None
        else:
            return sex

    def bmi_status(user):
        """Return BMI status, a string indicating the range of a user's BMI from underweight to obese, based upon input BMI."""
        bmi = round(user.body_mass_index * 100, 4)

        if (bmi < 18.5):
            return "underweight"
        elif (bmi < 25):
            return "normal"
        elif (bmi < 30):
            return "overweight"
        elif (bmi >= 30):
            return "obese"
        else:
            return "n/a"

APIServer.app.run()