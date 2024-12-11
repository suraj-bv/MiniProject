from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from matchcalc import calc_match_score
import openai


app = Flask(__name__)

app.secret_key = os.urandom(24).hex()

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database.db")

db = SQLAlchemy(app)

client = openai.OpenAI(api_key='~OPENAI_KEY~')


# table of User
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.Integer, nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    financial_nature = db.Column(db.String(10), nullable=False, default="Normal")
    dietary_restrictions = db.Column(db.String(10), nullable=False, default="No restrictions")
    language_match = db.Column(db.String(50), nullable=True)


# table of trips
class Trips(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    nature_trip = db.Column(db.String(50), nullable=True)
    trip_preferences = db.Column(db.String(10), nullable=False)


# table of Matches
class Matches(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1 = db.Column(db.Integer, db.ForeignKey("users.id"))
    user2 = db.Column(db.Integer, db.ForeignKey("users.id"))
    like_user1 = db.Column(db.Boolean, default=False)
    like_user2 = db.Column(db.Boolean, default=False)


# the routes are meant to mapp the URLs to a specific function that will handle the logic for that URL.
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    # check if the user name in the data base and if the password belong to the user.
    username = request.form["username"]
    password = request.form["password"]
    user = Users.query.filter_by(username=username).first()
    if not user or user.password != password:
        return render_template("login.html", error_message="Invalid username or password")

    session["user_id"] = user.id  #save the id and name in the session
    session["user_name"] = username
    return redirect(url_for("home"))
    
 
 # clear the session and return the user to the login page   
@app.route("/logout")
def logout():
    session.clear()
    return render_template("login.html")
    
    
# add a new user. receive the data from the html form and add to the db.
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    new_user = Users(username=request.form["username"], password=request.form["password"], role=1,
                     first_name=request.form["first_name"], last_name=request.form["last_name"],
                     date_of_birth=datetime.strptime(request.form["date_of_birth"], "%Y-%m-%d").date(),
                     gender=request.form["gender"], financial_nature=request.form["financial_nature"],
                     dietary_restrictions=request.form["dietary_restrictions"], email=request.form["email"],
                     language_match=request.form["language_match"])
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("login"))



# home page. after login the landing page. inject to the html the data of the user trips.
@app.route("/", methods=["GET"])
def home():
    if "user_id" not in session:   # check if the user in session
        return redirect(url_for("login"))
        
    user_id=session["user_id"]
    my_trips = Trips.query.filter_by(user_id=user_id).all()

    return render_template("home.html", username=session["user_name"], my_trips=my_trips)
    
    
# add a new trip for the user. resivie the data from the html form and add to the db.
@app.route("/new_trip", methods=["GET", "POST"])
def new_trip():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("new_trip.html", username=session["user_name"])

    start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()

    new_trip = Trips(user_id=session["user_id"], destination=request.form["destination"],
                     start_date=start_date, end_date=end_date, nature_trip=request.form["nature_trip"],
                     trip_preferences=request.form["trip_preferences"])
    db.session.add(new_trip)
    db.session.commit()
    return redirect(url_for("home"))


# from the chosen trip in the home page create a table of potential machtes by score and sent it to the html of find_pal.
@app.route("/find_pal", methods=["GET"])
def find_pal():
    if "user_id" not in session:
        return redirect(url_for("login"))

    trip_id = request.args.get('trip', default=-1, type=int) #save the id of the chosen trip.
    if trip_id == -1:
        return redirect(url_for("home"))
    
    me = Users.query.filter_by(id=session["user_id"]).first() # save the detail of the user
    my_trip = Trips.query.filter_by(id=trip_id).first() # save the detail of the user trip
    # bring from the db all the trip with the same destination that are't belonges to the user
    trips = Trips.query.filter_by(destination=my_trip.destination).filter(Trips.user_id != me.id).all()
    trips_scores = []
    # for each trip caclculate the score of the machte (using matchcalc) and add to the list if bigger than 0.
    for trip in trips:
        pal = Users.query.filter_by(id=trip.user_id).first() 
        score = calc_match_score(me, my_trip, pal, trip)
        if score > 0:
            trips_scores.append((pal, trip, score))
    trips_scores.sort(key=lambda element: element[2], reverse=True) # sort the list so the most suitable pal will be first.
    return render_template("find_pal.html", me=me, trips_scores=trips_scores) 


# in the find_pal html, an api to catch the "like" (only is the user swipe right = like)
@app.route("/like", methods=["GET"])
def like():
    my_id = request.args.get('me', default=-1, type=int) # check
    if my_id == -1:
        return "", 400

    pal_id = request.args.get('pal', default=-1, type=int) 
    if pal_id == -1:
        return "", 400

    # If the user and the pal alredy exsting in the db in table "Matches", save it to match variable.
    # chack both scenarios. Either the corrent user is the user1 or the user2
    match = Matches.query.filter(((Matches.user1 == my_id) & (Matches.user2 == pal_id)) | (
            (Matches.user1 == pal_id) & (Matches.user2 == my_id))).first()
    
    # change the user "like_user" paranter to be "True"
    if match:
        if match.user1 == my_id:
            match.like_user1 = True
        else:
            match.like_user2 = True
    else:  # if there is no data in the db for this match create a new one 
        match = Matches(user1=my_id, user2=pal_id, like_user1=True, like_user2=False)

    db.session.add(match)
    db.session.commit()

    return "", 200


# sent all the matches (if both likes each other) of the user to a html so he can chat with tham. 
@app.route("/matches", methods=["GET"])
def matches():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # save the user detils and his maches to sent it the the html
    user_id = session["user_id"]
    current_user = Users.query.filter_by(id=user_id).first() 
    my_matches = Matches.query.filter((Matches.user1 == user_id) | (Matches.user2 == user_id)).filter_by(
        like_user1=True).filter_by(like_user2=True).all()
    
    #create a list of only the pals that the user match with (pal = the other user) 
    matched_users = []
    for match in my_matches:
        match_user_id = match.user1
        if match.user1 == user_id:
            match_user_id = match.user2
        matched_users.append(Users.query.filter_by(id=match_user_id).first()) # list to sent the match html of only the pal. 

    return render_template("matches.html", matched_users=matched_users, current_user=current_user)


# show the user deteils and all his trips. 
@app.route("/profile", methods=["GET"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    user = Users.query.filter_by(id=user_id).first()
    trips = Trips.query.filter_by(user_id=user_id).all()
    return render_template("profile.html", user=user, trips=trips)


# Define route to handle chat messages
@app.route('/chat', methods=['POST'])
def handle_chat():
    # Get the user's message from the request
    user_message = request.json.get('message')
    # Fetch user data from the database
    user_data = fetch_user_data()

    reply = ""

    if user_data:
        # Check if the initial message has been shown
        if 'initial_message_shown' not in session:
            # Set the flag to indicate the initial message has been shown
            session['initial_message_shown'] = True

            # Greet the user by their first name if available
            if 'first_name' in user_data:
                reply += f"Welcome {user_data['first_name']}!\n"

            # Mention the user's trip details if available
            if user_data['destination'] and user_data['start_date'] and user_data['end_date']:
                reply += f"I see that you are planning a trip to {user_data['destination']} from {user_data['start_date']} to {user_data['end_date']}.\n"
        else:
            # No initial message needed, proceed with normal reply
            pass

    # Generate a reply if the user's message is not empty
    if user_message.strip():
        reply += get_completion(user_message, user_data)

    # Store the conversation in the session
    if 'conversation' not in session:
        session['conversation'] = []
    session['conversation'].append({'user': user_message, 'bot': reply.strip()})

    # Return the reply as a JSON response
    return jsonify({'reply': reply.strip() or "How can I assist you today?"})



# Function to fetch user data from the database
def fetch_user_data():
    # Get the user ID from the session
    user_id = session.get('user_id')

    if user_id:
        # Query the user from the database
        user = db.session.query(Users).filter_by(id=user_id).first()

        if user:
            # Query the user's latest trip from the database
            latest_trip = db.session.query(Trips).filter_by(user_id=user.id).order_by(Trips.id.asc()).first()

            # Prepare user data dictionary
            user_data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'gender': user.gender,
                'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if user.date_of_birth else None,
                'financial_nature': user.financial_nature,
                'language_match': user.language_match,
                'dietary_restrictions': user.dietary_restrictions,
                'destination': latest_trip.destination if latest_trip else None,
                'start_date': latest_trip.start_date.strftime(
                    '%Y-%m-%d') if latest_trip and latest_trip.start_date else None,
                'end_date': latest_trip.end_date.strftime('%Y-%m-%d') if latest_trip and latest_trip.end_date else None,
                'nature_trip': latest_trip.nature_trip if latest_trip else None,
                'trip_preferences': latest_trip.trip_preferences if latest_trip else None
            }
        else:
            user_data = None
    else:
        user_data = None

    return user_data

# Function to generate a response using the OpenAI API
def get_completion(prompt, user_data, model="gpt-3.5-turbo"):
    # Prepare the messages for the API request
    messages = [
        {"role": "user", "content": prompt}  # Send the user's query as a separate message
    ]

    # Include user details in the messages if available
    if user_data:
        user_details = (
            f"User {user_data['first_name']} {user_data['last_name']} is a {user_data['gender']} born on {user_data['date_of_birth']}."
            f"\nFinancial Nature: {user_data['financial_nature']}"
            f"\nLanguage Match: {user_data['language_match']}"
            f"\nDietary Restrictions: {user_data['dietary_restrictions']}"
            f"\nDestination: {user_data['destination']}"
            f"\nStart Date: {user_data['start_date']}"
            f"\nEnd Date: {user_data['end_date']}"
            f"\nNature of Trip: {user_data['nature_trip']}"
            f"\nTrip Preferences: {user_data['trip_preferences']}"
        )
        messages.append({"role": "user", "content": user_details})

    # Generate a response using the OpenAI API
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=400
    )
    
    # Return the generated response
    return response.choices[0].message.content




# Define route for fullscreen chat
@app.route("/fullscreen_chat")
def fullscreen_chat():
    # Render the fullscreen chat HTML template
    return render_template('fullscreen_chat.html')




# Define route to export chat history to a PDF
@app.route('/export_chat', methods=['GET'])
def export_chat():
    # Check if there is a conversation to export
    if 'conversation' not in session:
        return "No conversation to export", 400

    # Create a PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Add each chat message to the PDF
    for chat in session['conversation']:
        pdf.multi_cell(0, 10, f"User: {chat['user']}")
        pdf.multi_cell(0, 10, f"Bot: {chat['bot']}")
        pdf.ln()

    # Save the PDF to a file
    pdf_path = os.path.join(basedir, 'chat_history.pdf')
    pdf.output(pdf_path)

    # Send the PDF file as an attachment
    return send_file(pdf_path, as_attachment=True)


# Define route to get the initial message for the user
@app.route('/initial_message', methods=['GET'])
def initial_message():
    # Fetch user data from the database
    user_data = fetch_user_data()

    initial_reply = ""

    # Greet the user by their first name if available
    if user_data and 'first_name' in user_data:
        initial_reply += f"Welcome {user_data['first_name']}!\n"

        # Mention the user's trip details if available
        if user_data['destination'] and user_data['start_date'] and user_data['end_date']:
            initial_reply += f"I see that you are planning a trip to {user_data['destination']} from {user_data['start_date']} to {user_data['end_date']}.\n"

    # Set the initial message flag in the session
    session['initial_message_shown'] = True

    # Return the initial reply as a JSON response
    return jsonify({'reply': initial_reply.strip() or "How can I assist you today?"})




if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
