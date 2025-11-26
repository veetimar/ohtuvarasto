from flask import Flask, render_template, request, redirect, url_for
from varasto import Varasto

app = Flask(__name__)


class WarehouseManager:
    def __init__(self):
        self.warehouses = {}
        self.id_counter = 0

    def get_next_id(self):
        self.id_counter += 1
        return self.id_counter

    def create(self, name, capacity, initial_balance):
        wh_id = self.get_next_id()
        self.warehouses[wh_id] = {
            "name": name, "varasto": Varasto(capacity, initial_balance)
        }


manager = WarehouseManager()


@app.route("/")
def index():
    return render_template("index.html", warehouses=manager.warehouses)


@app.route("/create", methods=["POST"])
def create_warehouse():
    name = request.form.get("name", "").strip()
    try:
        capacity = float(request.form.get("capacity", "0"))
        initial = float(request.form.get("initial_balance", "0"))
    except ValueError:
        return redirect(url_for("index"))
    if name and capacity > 0 and initial >= 0:
        manager.create(name, capacity, initial)
    return redirect(url_for("index"))


@app.route("/delete/<int:wh_id>", methods=["POST"])
def delete_warehouse(wh_id):
    manager.warehouses.pop(wh_id, None)
    return redirect(url_for("index"))


def _parse_amount(form_data):
    try:
        amount = float(form_data.get("amount", "0"))
        return amount if amount >= 0 else None
    except ValueError:
        return None


@app.route("/add/<int:wh_id>", methods=["POST"])
def add_to_warehouse(wh_id):
    amount = _parse_amount(request.form)
    if wh_id in manager.warehouses and amount is not None:
        manager.warehouses[wh_id]["varasto"].lisaa_varastoon(amount)
    return redirect(url_for("index"))


@app.route("/remove/<int:wh_id>", methods=["POST"])
def remove_from_warehouse(wh_id):
    amount = _parse_amount(request.form)
    if wh_id in manager.warehouses and amount is not None:
        manager.warehouses[wh_id]["varasto"].ota_varastosta(amount)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
