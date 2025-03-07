from datetime import datetime, timezone, timedelta

# Heure UTC actuelle
utc_time = datetime.now(timezone.utc)
print("UTC Time:", utc_time)
paris_time = utc_time.astimezone(timezone(timedelta(hours=1)))
print("Paris Time:", paris_time)

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'votre_clé_secrète')  # Utiliser une variable d'environnement
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Liste des utilisateurs (avec des mots de passe en clair pour simplification)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    top_animes = db.relationship('TopAnime', backref='user', lazy=True)
    watchlist = db.relationship('Watchlist', backref='user', lazy=True)

class TopAnime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anime_title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anime_title = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='messages', lazy=True)
# Création des tables
with app.app_context():
    db.create_all()
    
    # Création des utilisateurs avec hash des mots de passe
    users = [
        {"username": "Misandratra", "password": "Excellent9,"},
        {"username": "Excellencia", "password": "Excellent9"},
        {"username": "Lisiharivony", "password": "Excellent99"}
    ]
    
    for user_data in users:
        if not User.query.filter_by(username=user_data["username"]).first():
            hashed_password = generate_password_hash(user_data["password"])
            new_user = User(username=user_data["username"], password=hashed_password)
            db.session.add(new_user)
    
    db.session.commit()
    print("Utilisateurs ajoutés avec succès !")


# Vérification de la connexion avant d'accéder aux pages protégées
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Vérifier user_id au lieu de user
            flash('Vous devez être connecté pour accéder à cette page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):  # Vérification sécurisée
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash("Nom d'utilisateur ou Mot de passe incorrects.", 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')




@app.route('/chat')
@login_required
def chat():
    # Récupérer les messages de tous les utilisateurs
    messages = Message.query.order_by(Message.timestamp.asc()).all()
    return render_template('chat.html', messages=messages)
@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    content = request.form['content']
    if content:
        message = Message(content=content, user_id=session['user_id'])
        db.session.add(message)
        db.session.commit()
    return redirect(url_for('chat'))
@app.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)  # Trouve le message par ID
    if message:
        db.session.delete(message)  # Supprime le message de la base de données
        db.session.commit()  # Applique la suppression
    return redirect(url_for('chat'))  # Redirige vers la page du chat
# Liste des animes romance mentionnés dans index.html
animes_data = [
    {"title": "Fruits Basket", "image": "fruits_basket.jpg", "genres": ["Romance", "Drama", "Slice of Life","School"]},
    {"title": "Akatsuki no Yona", "image": "akatsuki_no_yona.jpg", "genres": ["Romance", "Adventure", "Fantasy","Action"]},
    {"title": "Kaichou wa Maid sama", "image": "kaichou_wa_maid_sama.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Violet Evergarden", "image": "violet_evergarden.jpg", "genres": ["Romance", "Drama", "Adventure", "Historical"]},
    {"title": "ReLIFE", "image": "relife.jpg", "genres": ["Romance", "School", "Slice of Life", "Fantasy"]},
    {"title": "Soredemo Sekai wa Utsukushii", "image": "soredemo_sekai_wa_utsukushii.jpg", "genres": ["Romance", "Fantasy", "Adventure"]},
    {"title": "My Happy Marriage", "image": "my_happy_marriage.jpg", "genres": ["Romance", "Supernatural", "Drama", "Historical"]},
    {"title": "The Apothecary Diaries", "image": "the_apothecary_diaries.jpg", "genres": ["Romance", "Mystery", "Drama", "Historical"]},
    {"title": "Romantic Killer", "image": "romantic_killer.jpg", "genres": ["Romance", "Comedy", "Fantasy"]},
    {"title": "Yamada Kun to lv 999", "image": "yamada_kun_to_lv_999.jpg", "genres": ["Romance", "Comedy"]},
    {"title": "7th Time Loop", "image": "7th_time_loop.jpg", "genres": ["Romance", "Fantasy", "Adventure"]},
    {"title": "Kono Oto Tomare", "image": "kono_oto_tomare.jpg", "genres": ["Romance","School"]},
    {"title": "Kamisama Hajimemashita", "image": "kamisama_hajimemashita.jpg", "genres": ["Romance", "Fantasy", "Supernatural"]},
    {"title": "I'll Become a Villainess Who Goes Down in History", "image": "ill_become_a_villainess_who_goes_down_in_history.jpg", "genres": ["Romance", "Fantasy", "Isekai", "Psychology"]},
    {"title": "Wotakoi: Love is Hard for Otaku", "image": "wotakoi_love_is_hard_for_otaku.jpg", "genres": ["Romance", "Comedy", "Slice of Life"]},
    {"title": "Ao Haru Ride", "image": "ao_haru_ride.jpg", "genres": ["Romance", "Drama", "School"]},
    {"title": "Horimiya", "image": "horimiya.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Kaguya-sama: Love is War", "image": "kaguya_sama_love_is_war.jpg", "genres": ["Romance", "Comedy", "Psychology","School"]},
    {"title": "Skip and Loafer", "image": "skip_and_loafer.jpg", "genres": ["Romance", "Slice of Life", "School"]},
    {"title": "Tonari no Kaibutsu Kun", "image": "tonari_no_kaibutsu_kun.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Charlotte", "image": "charlotte.jpg", "genres": ["Romance", "Supernatural", "School", "Drama"]},
    {"title": "Yamada-kun and the Seven Witches", "image": "yamada_kun_and_the_seven_witches.jpg", "genres": ["Romance", "Comedy", "Supernatural"]},
    {"title": "Kishuku Gakkou no Juliet", "image": "kishuku_gakkou_no_juliet.jpg", "genres": ["Romance", "Comedy", "Action"]},
    {"title": "Ookami Shoujo to Kuro Ouji", "image": "ookami_shoujo_to_kuro_ouji.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Kimi ni Todoke", "image": "kimi_ni_todoke.jpg", "genres": ["Romance", "Drama", "School"]},
    {"title": "Honey Lemon Soda", "image": "honey_lemon_soda.jpg", "genres": ["Romance", "Drama", "School"]},
    {"title": "Ouran High School Host Club", "image": "ouran_high_school_host_club.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Itsudatte Bokura no Koi wa 10 cm", "image": "itsudatte_bokura_no_koi_wa_10_cm.jpg", "genres": ["Romance", "Drama", "School"]},
    {"title": "Itazura na Kiss", "image": "itazura_na_kiss.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Special A", "image": "special_a.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Nijiiro Days", "image": "nijiiro_days.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Ao-chan Can't Study", "image": "ao_chan_cant_study.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Kiss Him, Not Me", "image": "kiss_him_not_me.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Hyouka", "image": "hyouka.jpg", "genres": ["Romance", "Mystery", "School"]},
    {"title": "Gekkan Shoujo Nozaki-kun", "image": "gekkan_shoujo_nozaki_kun.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "My Next life as a Villainess", "image": "my_next_life_as_a_villainess.jpg", "genres": ["Romance", "Fantasy", "Isekai","Comedy"]},
    {"title": "Nisekoi", "image": "nisekoi.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Say I Love You", "image": "say_i_love_you.jpg", "genres": ["Romance", "Drama", "School"]},
    {"title": "Tsurezure Children", "image": "tsurezure_children.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "Bakuman", "image": "bakuman.jpg", "genres": ["Romance", "Comedy", "School", "Slice of Life"]},
    {"title": "Oregairu", "image": "oregairu.jpg", "genres": ["Romance", "Comedy", "School", "Slice of Life", "Psychology"]},
    {"title": "Rascal Does Not Dream of Bunny Girl Senpai", "image": "rascal_does_not_dream_of_bunny_girl_senpai.jpg", "genres": ["Romance", "Supernatural", "Slice of Life", "Psychology", "School"]},
    {"title": "Clannad", "image": "clannad.jpg", "genres": ["Romance", "Drama", "Supernatural", "School"]},
    {"title": "I'm Giving the Disgraced Noble Lady I Rescued a Crash Course in Naughtiness", "image": "im_giving_the_disgraced_noble_lady_i_rescued_a_crash_course_in_naughtiness.jpg", "genres": ["Romance", "Fantasy", "Comedy"]},
    {"title": "Why Raeliana Ended Up at the Duke's Mansion", "image": "why_raeliana_ended_up_at_the_dukes_mansion.jpg", "genres": ["Romance", "Fantasy", "Mystery", "Isekai"]},
    {"title": "Rakudai Kishi no Cavalry", "image": "rakudai_kishi_no_cavalry.jpg", "genres": ["Romance", "Action", "Fantasy"]},
    {"title": "Wise Man's Grandchild", "image": "wise_mans_grandchild.jpg", "genres": ["Romance", "Fantasy", "Isekai", "Action", "Comedy"]},
    {"title": "In Spectre", "image": "in_spectre.jpg", "genres": ["Romance", "Mystery", "Supernatural"]},
    {"title": "Jitsu wa Watashi wa", "image": "jitsu_wa_watashi_wa.jpg", "genres": ["Romance", "Comedy", "Supernatural"]},
    {"title": "Ranma 1/2", "image": "ranma_1_2.jpg", "genres": ["Romance", "Comedy", "Action"]},
    {"title": "Rikei ga Koi ni Ochita no de Shoumei shitemita", "image": "rikei_ga_koi_ni_ochita_no_de_shoumei_shitemita.jpg", "genres": ["Romance", "Comedy", "School"]},
    {"title": "The Saint's Magic Power is Omnipotent", "image": "the_saints_magic_power_is_omnipotent.jpg", "genres": ["Romance", "Fantasy", "Isekai"]},
    {"title": "Dance with Devils", "image": "dance_with_devils.jpg", "genres": ["Romance", "Fantasy", "Supernatural"]},
    {"title": "Inuyasha", "image": "inuyasha.jpg", "genres": ["Romance", "Fantasy", "Adventure", "Action", "Historical", "Supernatural"]},
    {"title": "Meiji Tokyo Renka", "image": "meiji_tokyo_renka.jpg", "genres": ["Romance", "Historical", "Supernatural", "Isekai"]}
]

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    else:
        return render_template('index.html', user=None)

@app.route('/recommend', methods=['POST'])
def recommend():
    genre = request.form.get('genre')

    # Filtrer les animes selon le genre
    if genre:
        filtered_animes = [anime for anime in animes_data if genre in anime['genres']]
    else:
        filtered_animes = animes_data  # Si aucun genre n'est sélectionné, afficher tous les animes

    # Vérifier si l'utilisateur est connecté
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

        # Générer le HTML directement dans la réponse
        anime_html = ""
        for anime in filtered_animes:
            anime_html += f"""
                <li>
                    <h3>{anime['title']}</h3>
                    <br>
                    <img src="{url_for('static', filename='images/' + anime['image'])}" alt="{anime['title']}" style="width: 200px;">
                    <p>Genres: {', '.join(anime['genres'])}</p>
            """

            if anime['title'] in [a.anime_title for a in user.top_animes]:
                anime_html += f"""
                    <form method="POST" action="{url_for('remove_from_top_10', anime_title=anime['title'])}">
                        <button type="submit">Retirer de mon top 10</button>
                    </form>
                """
            else:
                anime_html += f"""
                    <form method="POST" action="{url_for('add_to_top_10', anime_title=anime['title'])}">
                        <button type="submit">Ajouter à mon top 10</button>
                    </form>
                """

            if anime['title'] in [a.anime_title for a in user.watchlist]:
                anime_html += f"""
                    <form method="POST" action="{url_for('remove_from_watchlist', anime_title=anime['title'])}">
                        <button type="submit">Retirer de ma Watchlist</button>
                    </form>
                """
            else:
                anime_html += f"""
                    <form method="POST" action="{url_for('add_to_watchlist', anime_title=anime['title'])}">
                        <button type="submit">Ajouter à ma Watchlist</button>
                    </form>
                """

            anime_html += "</li>"

        return jsonify({'html': anime_html})

    else:
        return jsonify({'error': 'Vous devez être connecté pour effectuer cette recherche.'}), 401




@app.route('/add_to_top_10/<anime_title>', methods=['POST'])
@login_required
def add_to_top_10(anime_title):
    user = User.query.get(session['user_id'])
    
    # Vérifier si l'anime est déjà dans le top_10 de l'utilisateur
    if not any(anime.anime_title == anime_title for anime in user.top_animes):
        if len(user.top_animes) < 10:
            new_top_anime = TopAnime(anime_title=anime_title, user_id=user.id)
            db.session.add(new_top_anime)
            db.session.commit()
    
    # Générer un extrait HTML mis à jour pour cet anime
    anime_html = ""
    anime = next(a for a in animes_data if a['title'] == anime_title)  # Trouver l'anime par titre
    if anime['title'] in [a.anime_title for a in user.top_animes]:
        anime_html += f"""
            <form method="POST" action="{url_for('remove_from_top_10', anime_title=anime['title'])}">
                <button type="submit">Retirer de mon top 10</button>
            </form>
        """
    else:
        anime_html += f"""
            <form method="POST" action="{url_for('add_to_top_10', anime_title=anime['title'])}">
                <button type="submit">Ajouter à mon top 10</button>
            </form>
        """
    
    return jsonify({'status': 'success', 'html': anime_html})



@app.route('/remove_from_top_10/<anime_title>', methods=['POST'])
@login_required
def remove_from_top_10(anime_title):
    user = User.query.get(session['user_id'])
    
    # Trouver l'anime dans la liste TopAnime de l'utilisateur
    anime_to_remove = TopAnime.query.filter_by(anime_title=anime_title, user_id=user.id).first()
    
    if anime_to_remove:
        db.session.delete(anime_to_remove)
        db.session.commit()
    
    return redirect(url_for('top_10'))


@app.route('/top_10')
@login_required
def top_10():
    user = User.query.get(session['user_id'])
    top_10 = [anime.anime_title for anime in user.top_animes]
    return render_template('top_10.html', top_10=top_10)

@app.route('/add_to_watchlist/<anime_title>', methods=['POST'])
@login_required
def add_to_watchlist(anime_title):
    user = User.query.get(session['user_id'])
    
    # Vérifiez si l'anime est déjà dans la watchlist de l'utilisateur
    existing_watchlist_item = Watchlist.query.filter_by(anime_title=anime_title, user_id=user.id).first()
    
    if not existing_watchlist_item:
        new_watchlist_item = Watchlist(anime_title=anime_title, user_id=user.id)
        db.session.add(new_watchlist_item)
        db.session.commit()
    
    return redirect(url_for('index'))


@app.route('/remove_from_watchlist/<anime_title>', methods=['POST'])
@login_required
def remove_from_watchlist(anime_title):
    user = User.query.get(session['user_id'])
    
    # Trouver l'anime dans la liste Watchlist de l'utilisateur
    anime_to_remove = Watchlist.query.filter_by(anime_title=anime_title, user_id=user.id).first()
    
    if anime_to_remove:
        db.session.delete(anime_to_remove)
        db.session.commit()
    
    return redirect(url_for('watchlist'))


@app.route('/watchlist')
@login_required
def watchlist():
    user = User.query.get(session['user_id'])
    watchlist = [anime.anime_title for anime in user.watchlist]
    return render_template('watchlist.html', watchlist=watchlist)






@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)  # Retirer l'utilisateur de la session
    flash('Déconnexion réussie!', 'success')
    return redirect(url_for('login'))  # Rediriger vers la page de connexion


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)

