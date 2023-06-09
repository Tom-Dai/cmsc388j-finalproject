from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user


from .. import anime_client
from ..forms import AnimeReviewForm, SearchForm, AddToWatchlistForm
from ..models import User, Review, Watchlist
from ..utils import current_time

animes = Blueprint('animes',__name__)

@animes.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()
    if request.method == "POST" and form.validate():
        return redirect(url_for("animes.query_results", query=form.search_query.data))
    return render_template("index.html", form=form)


@animes.route("/search-results/<query>/", methods=["GET"])
def query_results(query):
    try:
        results = anime_client.search(query)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("animes.index"))

    return render_template("query.html", results=results)

@animes.route("/watchlist/<username>/<watchlist_id>/", methods=["GET"])
def watchlist_animes(watchlist_id,username):
    results = []
    user = User.objects(username=username).first()
    watchlist= Watchlist.objects(name=watchlist_id,user= user).first()
    try:
        for id in watchlist.anime_ids:
            results.append(anime_client.retrieve_anime_by_id(id))
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("animes.index"))
    return render_template("query.html", results=results)

@animes.route("/animes/<anime_id>", methods=["GET", "POST"])
def anime_detail(anime_id):
    try:
        result = anime_client.retrieve_anime_by_id(anime_id)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("users.login"))

    form = AnimeReviewForm()
    watchlist_form = AddToWatchlistForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            anime_id=anime_id,
            anime_title=result.title,
            rating = form.rating.data
        )
        review.save()

        return redirect(request.path)
    if watchlist_form.validate_on_submit() and current_user.is_authenticated:
        watchlist= Watchlist.objects(name=watchlist_form.name.data,user=current_user).first()
        if watchlist is None:
            flash("No Watchlist was found")
            redirect(url_for('animes.anime_detail', anime_id))
        else: 
            id = anime_id
            if id in watchlist.anime_ids:
                flash("Already in Watchlist!")
            else:
                new_list = watchlist.anime_ids
                new_list.append(id)
                watchlist.modify(anime_ids = new_list)
                watchlist.save()
                flash("added to watchlist!")

            return redirect(request.path)

    reviews = Review.objects(anime_id=anime_id)

    return render_template(
        "anime_detail.html", form=form, anime=result, reviews=reviews, watchlist_form = watchlist_form
    )

@animes.route("/user/<username>")
def user_detail(username):
    user = User.objects(username=username).first()
    reviews = Review.objects(commenter=user)
    watchlists = Watchlist.objects(user = user)
    return render_template("user_detail.html", username=username, reviews=reviews, watchlists = watchlists)