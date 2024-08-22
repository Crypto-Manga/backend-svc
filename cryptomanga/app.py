import base64
import hashlib
import hmac
import os
from typing import List

from flask import request
from flask.json import jsonify

from cryptomanga import app, mongo
from cryptomanga.battle.handler import BattleHandler
from cryptomanga.battle.workshop import WorkshopApi
from cryptomanga.handler.mongo_api import MongoApi
from cryptomanga.handler.sessions_handler import SessionsHandler
from cryptomanga.handler.the_graph_api import TheGraphApi
from cryptomanga.handler.train_handler import TrainHandler
from cryptomanga.handler.twitter_api import TwitterApi
from cryptomanga.persistence.cache.heroku_redis import HerokuRedis
from cryptomanga.persistence.model import Attribute, DarkBattle, Metadata
from cryptomanga.util import is_valid_request, strip_suffix

redis = HerokuRedis()
graph = TheGraphApi(redis=redis)
twitter = TwitterApi(redis=redis)
mongodb = MongoApi(mongo=mongo)
workshop = WorkshopApi(redis=redis, graph=graph)
train_handler = TrainHandler(twitter=twitter, graph=graph, mongo=mongodb)
battle_handler = BattleHandler(
    redis=redis, twitter=twitter, mongo=mongodb, graph=graph, workshop=workshop
)
sessions_handler = SessionsHandler()


@app.route("/metadata/<cid>/<id_str>", methods=["GET"])
def metadata(cid, id_str):
    if request.method == "GET":
        id = strip_suffix(id_str)
        result = Metadata.query.filter_by(id=id).first()
        if result is None:
            return None, 404

        return jsonify(result.serialize())


@app.route("/sessions/<id>", methods=["GET"])
def sessions(id):
    if request.method == "GET":

        result = sessions_handler.handle(int(id))
        return jsonify({"data": result})


@app.route("/wallets", methods=["GET"])
def wallets():
    if request.method == "GET":
        result = mongodb.get_all_wallets()
        return jsonify({"data": result})


@app.route("/metadata_new", methods=["GET"])
def wallet_new():
    if request.method == "GET":
        wallet = request.args.get("wallet")
        page = int(request.args.get("page")) - 1
        page_size = 5
        token_ids: List[int] = graph.get_cma_tokens_for_wallet(wallet.lower())

        if len(token_ids) == 0:
            return jsonify(
                {"data": [], "page": 1, "total_page": 0, "total_results": "0"}
            )

        token_ids.sort()
        pages = [
            token_ids[i : i + page_size] for i in range(0, len(token_ids), page_size)
        ]

        current_tokens = pages[page]
        ret_val = list()
        for token_id in current_tokens:
            metadata = Metadata.query.filter_by(id=token_id).first()
            serialized = metadata.serialize()
            sessions = sessions_handler.handle(token_id)
            serialized["sessions"] = sessions
            ret_val.append(serialized)

        return jsonify(
            {
                "data": ret_val,
                "page": page + 1,
                "total_pages": len(pages),
                "total_results": len(token_ids),
            }
        )


@app.route("/metadata", methods=["GET"])
def wallet():
    if request.method == "GET":
        wallet = request.args.get("wallet")
        token_ids: List[int] = graph.get_cma_tokens_for_wallet(wallet.lower())
        ret_val = list()
        for token_id in token_ids:
            metadata = Metadata.query.filter_by(id=token_id).first()
            serialized = metadata.serialize()
            sessions = sessions_handler.handle(token_id)
            serialized["sessions"] = sessions
            ret_val.append(serialized)

        return jsonify({"data": ret_val})


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    if request.method == "GET":
        shells = DarkBattle.query.order_by(DarkBattle.won.desc()).all()
        return jsonify({"data": [shell.serialize() for shell in shells]})


@app.route("/client", methods=["GET", "POST"])
def twitter_pulse():
    if request.method == "GET":
        hash_digest = hmac.digest(
            key=os.environ["twitter_key_secret"].encode("utf-8"),
            msg=request.args.get("crc_token").encode("utf-8"),
            digest=hashlib.sha256,
        )
        return {
            "response_token": "sha256=" + base64.b64encode(hash_digest).decode("ascii")
        }

    elif request.method == "POST" and is_valid_request(request):

        data = request.get_json()
        # We only handle the event when someone tweets at us.
        # No likes, retweets etc are currently processed.

        battle_handler.handle(data)
            

        return {"message": "success"}, 200
